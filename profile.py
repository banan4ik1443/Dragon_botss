"""
Профиль игрока: ник, клыки, дракон в использовании, его уровень/усталость,
монеты/опыт/мясо. Под профилем — кнопки «Настройки» и «Драконы».
"""
from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database as db
import game_logic as gl
import game_data as gd

router = Router()


class NicknameForm(StatesGroup):
    waiting_for_nickname = State()


def profile_kb() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.button(text="⚙️ Настройки", callback_data="profile:settings")
    kb.button(text="🥚 Драконы", callback_data="menu:dragons")
    kb.button(text="⬅️ Меню", callback_data="menu:main")
    kb.adjust(2, 1)
    return kb


async def render_profile(user_id: int) -> str:
    user = await db.get_user(user_id)
    if user is None:
        return "Сначала напиши /start."

    active = None
    if user["active_dragon_id"]:
        active = await db.get_dragon(user["active_dragon_id"])

    vip_line = f"VIP » {user['vip_status']}\n" if user["vip_status"] else ""

    lines = [
        f"<b>{user['nickname']}</b>, твой профиль:",
        "",
        "<blockquote>"
        f"{vip_line}"
        f"Клыки » {user['fangs']} 🦷\n"
        f"Монеты » {user['coins']} 🪙\n"
        f"Опыт » {user['exp']} ✨\n"
        f"Мясо » {user['meat']} 🍖"
        "</blockquote>",
    ]

    if active:
        stats = gl.effective_stats(active)
        species_name = gd.SPECIES[active["species_key"]]["name"]
        lines.append("")
        lines.append(
            f"Активный дракон » {active['name']}\n"
            f" ↳ Вид » {species_name}\n"
            f" ↳ Уровень » {active['level']}\n"
            f" ↳ Усталость » {stats['fatigue']}%"
        )
        if stats["is_banned"]:
            lines.append("⚠️ Дракон обессилен, ему нужен отдых.")
    else:
        lines.append("")
        lines.append("У тебя ещё нет активного дракона — открой яйцо в разделе «Открытие яиц» 🥚")

    lines.append("")
    lines.append("Изменить ник по команде /nickname")

    return "\n".join(lines)


@router.message(Command("profile"))
async def cmd_profile(message: Message) -> None:
    text = await render_profile(message.from_user.id)
    await message.answer(text, reply_markup=profile_kb().as_markup())


@router.callback_query(F.data == "menu:profile")
async def cb_profile(callback: CallbackQuery) -> None:
    text = await render_profile(callback.from_user.id)
    await callback.message.edit_text(text, reply_markup=profile_kb().as_markup())
    await callback.answer()


@router.callback_query(F.data == "profile:settings")
async def cb_settings(callback: CallbackQuery) -> None:
    kb = InlineKeyboardBuilder()
    kb.button(text="✏️ Сменить ник", callback_data="settings:nickname")
    kb.button(text="⬅️ Назад", callback_data="menu:profile")
    kb.adjust(1)
    await callback.message.edit_text("⚙️ Настройки профиля:", reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(F.data == "settings:nickname")
async def cb_ask_nickname(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(NicknameForm.waiting_for_nickname)
    await callback.message.edit_text("Введи новый никнейм (2-20 символов):")
    await callback.answer()


@router.message(NicknameForm.waiting_for_nickname)
async def process_nickname(message: Message, state: FSMContext) -> None:
    nickname = message.text.strip()
    if not (2 <= len(nickname) <= 20):
        await message.answer("Никнейм должен быть от 2 до 20 символов. Попробуй ещё раз:")
        return
    await db.update_user_fields(message.from_user.id, nickname=nickname)
    await state.clear()
    await message.answer(f"Готово! Теперь ты — <b>{nickname}</b>.", reply_markup=profile_kb().as_markup())


@router.message(Command("nickname"))
async def cmd_nickname(message: Message, command: CommandObject) -> None:
    if not command.args:
        await message.answer("Использование: /nickname НовоеИмя")
        return
    nickname = command.args.strip()
    if not (2 <= len(nickname) <= 20):
        await message.answer("Никнейм должен быть от 2 до 20 символов.")
        return
    await db.update_user_fields(message.from_user.id, nickname=nickname)
    await message.answer(f"Готово! Теперь ты — <b>{nickname}</b>.")
