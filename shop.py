"""
Магазин. Броня доступна всегда, яйца/акции — рандомно, обновление в 11:00 МСК.
Дракона можно продать скупщику — цена зависит от редкости/уровня/способности.
"""
import datetime as dt
import random

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database as db
import game_data as gd
import game_logic as gl
from config import MSK, SHOP_REFRESH_HOUR

router = Router()


# Пул "акционных" товаров, из которых каждый день выбирается 0-2 случайных
ROTATING_POOL = [
    {"key": "egg_rare", "name": "🥚 Редкое яйцо", "price": 350, "kind": "egg", "rarity": "rare"},
    {"key": "egg_epic", "name": "🥚 Эпическое яйцо", "price": 900, "kind": "egg", "rarity": "epic"},
    {"key": "meat_pack", "name": "🍖 Большой запас мяса (100)", "price": 150, "kind": "meat", "amount": 100},
]


def _shop_day_key() -> str:
    """Ключ дня магазина: сутки считаются от 11:00 по МСК до 11:00 следующего."""
    now_msk = dt.datetime.now(MSK)
    if now_msk.hour < SHOP_REFRESH_HOUR:
        now_msk -= dt.timedelta(days=1)
    return now_msk.strftime("%Y-%m-%d")


def get_daily_rotation() -> list[dict]:
    day_key = _shop_day_key()
    rng = random.Random(day_key)  # детерминированно для всех в один день
    count = rng.randint(0, 2)
    return rng.sample(ROTATING_POOL, k=min(count, len(ROTATING_POOL)))


def shop_main_kb() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.button(text="🛡 Броня", callback_data="shop:armor")
    kb.button(text="🎲 Акции дня", callback_data="shop:rotation")
    kb.button(text="💰 Продать дракона", callback_data="shop:sell")
    kb.button(text="⬅️ Меню", callback_data="menu:main")
    kb.adjust(2, 1, 1)
    return kb


@router.message(Command("shop"))
async def cmd_shop(message: Message) -> None:
    await message.answer(
        "🏪 <b>Магазин</b>\nОбновляется каждый день в 11:00 по МСК.",
        reply_markup=shop_main_kb().as_markup(),
    )


@router.callback_query(F.data == "menu:shop")
async def cb_shop_open(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "🏪 <b>Магазин</b>\nОбновляется каждый день в 11:00 по МСК.",
        reply_markup=shop_main_kb().as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data == "shop:armor")
async def cb_shop_armor(callback: CallbackQuery) -> None:
    kb = InlineKeyboardBuilder()
    for key, item in gd.ARMOR_CATALOG.items():
        kb.button(
            text=f"{item['name']} — {item['price']}🪙",
            callback_data=f"shop:buy:armor:{key}",
        )
    kb.button(text="⬅️ Назад", callback_data="menu:shop")
    kb.adjust(1)
    await callback.message.edit_text("🛡 <b>Броня</b> (доступна всегда):", reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(F.data == "shop:rotation")
async def cb_shop_rotation(callback: CallbackQuery) -> None:
    items = get_daily_rotation()
    kb = InlineKeyboardBuilder()
    if not items:
        text = "🎲 Сегодня в акциях ничего нет, кроме брони. Загляни после 11:00 МСК завтра!"
    else:
        text = "🎲 <b>Акции дня</b>:"
        for item in items:
            kb.button(
                text=f"{item['name']} — {item['price']}🪙",
                callback_data=f"shop:buy:rotation:{item['key']}",
            )
    kb.button(text="⬅️ Назад", callback_data="menu:shop")
    kb.adjust(1)
    await callback.message.edit_text(text, reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("shop:buy:armor:"))
async def cb_buy_armor(callback: CallbackQuery) -> None:
    armor_key = callback.data.split(":")[-1]
    item = gd.ARMOR_CATALOG.get(armor_key)
    user = await db.get_user(callback.from_user.id)
    if not item or user is None:
        await callback.answer("Товар не найден.", show_alert=True)
        return
    if user["coins"] < item["price"]:
        await callback.answer("Не хватает монет.", show_alert=True)
        return
    if not user["active_dragon_id"]:
        await callback.answer("Сначала выбери активного дракона.", show_alert=True)
        return

    await db.update_user_fields(callback.from_user.id, coins=user["coins"] - item["price"])
    await db.update_dragon_fields(user["active_dragon_id"], armor_key=armor_key)
    await callback.answer(f"Куплено: {item['name']} 🛡")


@router.callback_query(F.data.startswith("shop:buy:rotation:"))
async def cb_buy_rotation(callback: CallbackQuery) -> None:
    item_key = callback.data.split(":")[-1]
    item = next((i for i in ROTATING_POOL if i["key"] == item_key), None)
    if item is None or item not in get_daily_rotation():
        await callback.answer("Этот товар сегодня недоступен.", show_alert=True)
        return

    user = await db.get_user(callback.from_user.id)
    if user["coins"] < item["price"]:
        await callback.answer("Не хватает монет.", show_alert=True)
        return

    await db.update_user_fields(callback.from_user.id, coins=user["coins"] - item["price"])
    if item["kind"] == "egg":
        await db.add_egg(callback.from_user.id, item["rarity"])
        await callback.answer("Яйцо добавлено в раздел «Драконы» 🥚")
    elif item["kind"] == "meat":
        await db.update_user_fields(callback.from_user.id, meat=user["meat"] + item["amount"])
        await callback.answer(f"+{item['amount']} мяса 🍖")


@router.callback_query(F.data == "shop:sell")
async def cb_shop_sell(callback: CallbackQuery) -> None:
    dragons = await db.get_user_dragons(callback.from_user.id)
    if not dragons:
        await callback.answer("У тебя нет драконов на продажу.", show_alert=True)
        return

    kb = InlineKeyboardBuilder()
    for d in dragons:
        price = gl.dragon_sell_price(d)
        kb.button(text=f"{d['name']} (ур. {d['level']}) — {price}🪙", callback_data=f"shop:sellconfirm:{d['dragon_id']}")
    kb.button(text="⬅️ Назад", callback_data="menu:shop")
    kb.adjust(1)
    await callback.message.edit_text("💰 Выбери дракона для продажи скупщику:", reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("shop:sellconfirm:"))
async def cb_sell_confirm(callback: CallbackQuery) -> None:
    dragon_id = int(callback.data.split(":")[-1])
    dragon = await db.get_dragon(dragon_id)
    user = await db.get_user(callback.from_user.id)
    if not dragon or dragon["owner_id"] != callback.from_user.id:
        await callback.answer("Дракон не найден.", show_alert=True)
        return

    price = gl.dragon_sell_price(dragon)
    await db.delete_dragon(dragon_id)
    await db.update_user_fields(callback.from_user.id, coins=user["coins"] + price)
    if user["active_dragon_id"] == dragon_id:
        await db.update_user_fields(callback.from_user.id, active_dragon_id=None)

    await callback.message.edit_text(f"Скупщик забрал {dragon['name']} за {price}🪙.")
    await callback.answer()
