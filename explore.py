"""
Локации. Игрок раз в EXPLORE_COOLDOWN_MIN отправляет дракона исследовать
местность и получает либо яйцо случайной редкости, либо мясо.
Сами локации сейчас — это просто флавор-текст поверх одной общей формулы
дропа; при желании каждой локации можно дать свою таблицу весов редкостей.
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
from handlers import quests

router = Router()

EXPLORE_COOLDOWN_MIN = 30
EGG_DROP_CHANCE = 0.35   # иначе выпадает мясо
MEAT_DROP_MIN, MEAT_DROP_MAX = 10, 30

LOCATIONS = {
    "forest": "🌲 Тёмный лес",
    "mountains": "⛰️ Драконьи горы",
    "caves": "🕳️ Подземные пещеры",
}


def locations_kb() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    for key, name in LOCATIONS.items():
        kb.button(text=name, callback_data=f"explore:go:{key}")
    kb.button(text="⬅️ Меню", callback_data="menu:main")
    kb.adjust(1)
    return kb


@router.message(Command("explore"))
async def cmd_explore(message: Message) -> None:
    await message.answer("🗺️ Куда отправить дракона на разведку?", reply_markup=locations_kb().as_markup())


@router.callback_query(F.data == "menu:explore")
async def cb_explore_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text("🗺️ Куда отправить дракона на разведку?", reply_markup=locations_kb().as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("explore:go:"))
async def cb_explore_go(callback: CallbackQuery) -> None:
    location_key = callback.data.split(":")[-1]
    user = await db.get_user(callback.from_user.id)
    if user is None:
        await callback.answer("Сначала напиши /start.", show_alert=True)
        return

    if user["last_explore_at"]:
        last = dt.datetime.fromisoformat(user["last_explore_at"])
        elapsed_min = (dt.datetime.utcnow() - last).total_seconds() / 60
        if elapsed_min < EXPLORE_COOLDOWN_MIN:
            left = round(EXPLORE_COOLDOWN_MIN - elapsed_min)
            await callback.answer(f"Дракон ещё отдыхает после разведки. Подожди ~{left} мин.", show_alert=True)
            return

    await db.update_user_fields(callback.from_user.id, last_explore_at=dt.datetime.utcnow().isoformat())
    await quests.record_progress(callback.from_user.id, "explore")

    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ К локациям", callback_data="menu:explore")

    if random.random() < EGG_DROP_CHANCE:
        rarity = gl.roll_egg_rarity()
        await db.add_egg(callback.from_user.id, rarity)
        rarity_name = gd.RARITIES[rarity]["name"]
        text = f"{LOCATIONS[location_key]}\n\n🥚 Найдено яйцо: <b>{rarity_name}</b>! Загляни в раздел «Драконы»."
    else:
        meat = random.randint(MEAT_DROP_MIN, MEAT_DROP_MAX)
        await db.update_user_fields(callback.from_user.id, meat=user["meat"] + meat)
        text = f"{LOCATIONS[location_key]}\n\n🍖 Найдено мяса: +{meat}"

    await callback.message.edit_text(text, reply_markup=kb.as_markup())
    await callback.answer()
