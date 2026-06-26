"""
Открытие яиц — отдельное от «Драконов» меню. Никакого таймера ожидания:
яйцо открывается сразу с маленькой анимацией (несколько edit_text подряд),
и игрок сразу получает дракона. "Ожидание" в игре теперь не на яйце, а на
самом драконе — ему нужно вырасти до min_duel_level, чтобы пойти в дуэль
(см. game_data.RARITIES[...]["min_duel_level"]).
"""
import asyncio

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database as db
import game_data as gd
import game_logic as gl
from handlers.dragon import render_dragon_card

router = Router()

REVEAL_STEP_DELAY = 0.7


def eggs_list_kb(eggs: list[dict]) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    for egg in eggs:
        rarity = gd.RARITIES[egg["rarity"]]
        kb.button(
            text=f"{rarity['emoji']} Яйцо «{rarity['name']}» — открыть",
            callback_data=f"egg:open:{egg['egg_id']}",
        )
    kb.button(text="⬅️ Меню", callback_data="menu:main")
    kb.adjust(1)
    return kb


async def render_eggs_list(user_id: int) -> tuple[str, InlineKeyboardBuilder]:
    eggs = await db.get_eggs(user_id)
    if not eggs:
        text = (
            "🥚 <b>Открытие яиц</b>\n\n"
            "У тебя пока нет яиц. Сходи в «Локации» 🗺️ или загляни в «Магазин» 🏪 — "
            "там они иногда продаются в акциях дня."
        )
    else:
        text = (
            "🥚 <b>Открытие яиц</b>\n\n"
            f"У тебя {len(eggs)} {'яйцо' if len(eggs) == 1 else 'яйца(иц)'}. "
            "Нажми, чтобы открыть — дракон вылупится сразу же!"
        )
    return text, eggs_list_kb(eggs)


@router.message(Command("eggs"))
async def cmd_eggs(message: Message) -> None:
    text, kb = await render_eggs_list(message.from_user.id)
    await message.answer(text, reply_markup=kb.as_markup())


@router.callback_query(F.data == "menu:eggs")
async def cb_eggs(callback: CallbackQuery) -> None:
    text, kb = await render_eggs_list(callback.from_user.id)
    await callback.message.edit_text(text, reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("egg:open:"))
async def cb_egg_open(callback: CallbackQuery) -> None:
    egg_id = int(callback.data.split(":")[-1])
    eggs = await db.get_eggs(callback.from_user.id)
    egg = next((e for e in eggs if e["egg_id"] == egg_id), None)
    if not egg:
        await callback.answer("Яйцо не найдено.", show_alert=True)
        return
    await callback.answer()

    rarity_key = egg["rarity"]
    rarity = gd.RARITIES[rarity_key]
    msg = callback.message

    # ── маленькая анимация раскрытия ────────────────────────────────────
    await msg.edit_text(f"{rarity['emoji']} Яйцо начинает дрожать...")
    await asyncio.sleep(REVEAL_STEP_DELAY)

    await msg.edit_text(f"{rarity['emoji']} Скорлупа трескается... {rarity['flair']}")
    await asyncio.sleep(REVEAL_STEP_DELAY)

    await msg.edit_text(f"💥 ВЫЛУПЛЯЕТСЯ {rarity['flair']}")
    await asyncio.sleep(max(0.4, REVEAL_STEP_DELAY - 0.2))

    # ── создаём дракона ──────────────────────────────────────────────────
    species_key = gl.roll_species_for_rarity(rarity_key)
    ability_key = gl.roll_ability_for_species(species_key)
    species_name = gd.SPECIES[species_key]["name"]
    ability_name = gd.ABILITIES[ability_key]["name"]

    dragon_id = await db.create_dragon(
        owner_id=callback.from_user.id,
        species_key=species_key,
        rarity=rarity_key,
        name=species_name,
        ability_key=ability_key,
    )
    await db.delete_egg(egg_id)

    user = await db.get_user(callback.from_user.id)
    if not user["active_dragon_id"]:
        await db.update_user_fields(callback.from_user.id, active_dragon_id=dragon_id)

    reveal_text = (
        f"{rarity['flair']}\n"
        f"🎉 <b>{rarity['name'].upper()}!</b> {rarity['flair']}\n\n"
        f"<blockquote>Вид » {species_name}\n"
        f"Способность » {ability_name}</blockquote>\n\n"
        f"Ему нужно подрасти до уровня {rarity['min_duel_level']}, чтобы выйти на дуэль — "
        f"корми и тренируй в разделе «Драконы» 🐉"
    )
    kb = InlineKeyboardBuilder()
    kb.button(text="🐉 К дракону", callback_data=f"dragon:view:{dragon_id}")
    kb.button(text="🥚 Открыть ещё", callback_data="menu:eggs")
    kb.adjust(1)

    await msg.edit_text(reveal_text, reply_markup=kb.as_markup())
