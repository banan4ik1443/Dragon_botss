"""
/start — онбординг. Новому игроку выдаём стартовое яйцо и ресурсы,
рассказываем короткую предысторию, показываем главное меню.
"""
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database as db
import game_data as gd

router = Router()

STARTER_COINS = 150
STARTER_MEAT = 40
STARTER_EGG_RARITY = "common"

STORY_TEXT = (
    "🐉 <b>Долина Драконов</b>\n\n"
    "Гнездо в скалах пустовало много лет, пока однажды ты не нашёл там "
    "яйцо — тёплое, будто внутри спит маленькое солнце.\n\n"
    "Местные говорят: то, кто вырастит дракона из такого яйца, "
    "сможет однажды бросить вызов самим Древним Вирмам.\n\n"
    "Возьми яйцо, немного мяса на первое время — и в путь."
)


def main_menu_kb() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.button(text="👤 Профиль", callback_data="menu:profile")
    kb.button(text="🐉 Драконы", callback_data="menu:dragons")
    kb.button(text="🥚 Открытие яиц", callback_data="menu:eggs")
    kb.button(text="🗺️ Локации", callback_data="menu:explore")
    kb.button(text="🏪 Магазин", callback_data="menu:shop")
    kb.button(text="📋 Задания", callback_data="menu:quests")
    kb.button(text="🏆 Топ", callback_data="menu:top")
    kb.button(text="💎 Донат", callback_data="menu:donate")
    kb.button(text="❓ Помощь", callback_data="menu:help")
    kb.adjust(2, 2, 2, 2, 1)
    return kb


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user = await db.get_user(message.from_user.id)

    if user is None:
        nickname = message.from_user.first_name or f"Игрок{message.from_user.id % 10000}"
        await db.create_user(message.from_user.id, nickname)
        await db.update_user_fields(
            message.from_user.id,
            coins=STARTER_COINS,
            meat=STARTER_MEAT,
        )
        await db.add_egg(message.from_user.id, STARTER_EGG_RARITY)

        await message.answer(STORY_TEXT)
        await message.answer(
            f"Получено:\n"
            f"<blockquote>Яйцо » {gd.RARITIES[STARTER_EGG_RARITY]['name']} 🥚\n"
            f"Монеты » {STARTER_COINS} 🪙\n"
            f"Мясо » {STARTER_MEAT} 🍖</blockquote>\n"
            "Открой яйцо в разделе «🥚 Открытие яиц» — дракон появится сразу же!",
            reply_markup=main_menu_kb().as_markup(),
        )
    else:
        await message.answer(
            f"С возвращением, {user['nickname']}! 👋",
            reply_markup=main_menu_kb().as_markup(),
        )


@router.callback_query(F.data == "menu:main")
async def cb_main_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=main_menu_kb().as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:donate")
async def cb_donate_stub(callback: CallbackQuery) -> None:
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Назад", callback_data="menu:main")
    await callback.message.edit_text(
        "💎 <b>Донат</b>\n\nРаздел в разработке: наборы и VIP-статусы за Telegram Stars появятся здесь.",
        reply_markup=kb.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:help")
async def cb_help(callback: CallbackQuery) -> None:
    text = (
        "<b>Помощь</b>\n\n"
        "<blockquote>/start » начать / главное меню\n"
        "/profile » твой профиль\n"
        "/dragons » твои драконы\n"
        "/eggs » открыть яйцо\n"
        "/explore » разведка локаций\n"
        "/quests » ежедневные задания\n"
        "/shop » магазин\n"
        "/duel » найти соперника для дуэли\n"
        "/top » топ сезона по клыкам\n"
        "/nickname &lt;имя&gt; » сменить никнейм</blockquote>\n\n"
        "Усталость дракона растёт от тренировок и дуэлей. До 50% всё в порядке, "
        "выше — статы начинают падать, на 100% дракону нужен отдых.\n\n"
        "Дракон допускается до дуэлей не сразу — редким видам нужно подрасти "
        "до более высокого уровня."
    )
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Назад", callback_data="menu:main")
    await callback.message.edit_text(text, reply_markup=kb.as_markup())
    await callback.answer()
