"""
Ежедневные задания. Набор на день: всегда "зайти в бота" + до QUEST_EXTRA_COUNT
случайных заданий из тех, что игрок реально может выполнить на своём прогрессе
(нет дракона — не дадут задание "потренировать дракона" и т.п.).

Стрик считается за полное выполнение ВСЕХ заданий дня — он не привязан к
конкретному заданию, а влияет на награду за все задания сразу (через
quest_streak_multiplier в game_data).

Другие модули дёргают record_progress(user_id, "feed"/"train"/"explore"/"duel_play")
после соответствующего действия — это и продвигает прогресс заданий.
"""
import datetime as dt
import random

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database as db
import game_data as gd
from config import today_msk_key

router = Router()


def _roll_target(target_spec) -> int:
    if isinstance(target_spec, tuple):
        return random.randint(*target_spec)
    return target_spec


async def ensure_today_quests(user_id: int) -> list[dict]:
    """Возвращает список заданий на сегодня, генерируя их при первом обращении."""
    today_key = today_msk_key()
    existing = await db.get_quests_for_day(user_id, today_key)
    if existing:
        return existing

    user = await db.get_user(user_id)
    if user is None:
        return []

    # если вчера не было полного выполнения всех заданий — стрик сгорает
    yesterday_key = (dt.date.fromisoformat(today_key) - dt.timedelta(days=1)).isoformat()
    if user["quest_streak_day"] != yesterday_key and user["quest_streak"] != 0:
        await db.update_user_fields(user_id, quest_streak=0)
        user["quest_streak"] = 0

    mult = gd.quest_streak_multiplier(user["quest_streak"])
    has_dragon = bool(user["active_dragon_id"])

    pool = [k for k, t in gd.QUEST_TEMPLATES.items()
            if k != "login" and (not t["requires_dragon"] or has_dragon)]
    chosen_keys = ["login"] + random.sample(pool, k=min(gd.QUEST_EXTRA_COUNT, len(pool)))

    for key in chosen_keys:
        tpl = gd.QUEST_TEMPLATES[key]
        target = _roll_target(tpl["target"])
        coins = round(tpl["reward_coins"] * mult)
        meat = round(tpl["reward_meat"] * mult)
        await db.create_quest(user_id, today_key, key, target, coins, meat, is_bonus=False)

    bonus_coins = round(gd.BONUS_ALL_QUESTS_COINS * mult)
    bonus_meat = round(gd.BONUS_ALL_QUESTS_MEAT * mult)
    await db.create_quest(user_id, today_key, "_bonus", 1, bonus_coins, bonus_meat, is_bonus=True)

    # сам факт обращения к боту сегодня — это и есть выполнение "Зайти в бота"
    await record_progress(user_id, "login", amount=1, _skip_ensure=True)
    return await db.get_quests_for_day(user_id, today_key)


async def _check_bonus(user_id: int, today_key: str) -> None:
    quests = await db.get_quests_for_day(user_id, today_key)
    real = [q for q in quests if not q["is_bonus"]]
    bonus = next((q for q in quests if q["is_bonus"]), None)
    if bonus and not bonus["completed"] and real and all(q["completed"] for q in real):
        await db.update_quest_fields(bonus["quest_id"], progress=1, completed=1)
        user = await db.get_user(user_id)
        await db.update_user_fields(
            user_id,
            quest_streak=user["quest_streak"] + 1,
            quest_streak_day=today_key,
        )


async def record_progress(user_id: int, action_key: str, amount: int = 1, _skip_ensure: bool = False) -> None:
    if not _skip_ensure:
        await ensure_today_quests(user_id)

    today_key = today_msk_key()
    quests = await db.get_quests_for_day(user_id, today_key)
    touched = False
    for q in quests:
        if q["quest_key"] == action_key and not q["completed"]:
            new_progress = min(q["target"], q["progress"] + amount)
            completed = 1 if new_progress >= q["target"] else 0
            await db.update_quest_fields(q["quest_id"], progress=new_progress, completed=completed)
            touched = True
    if touched:
        await _check_bonus(user_id, today_key)


def _quest_line(q: dict) -> str:
    tpl = gd.QUEST_TEMPLATES.get(q["quest_key"])
    if q["is_bonus"]:
        name = "🎁 Бонус: выполнить все задания дня"
    else:
        name = tpl["name"].format(t=q["target"]) if "{t}" in tpl["name"] else tpl["name"]
    mark = "✅" if q["completed"] else "▫️"
    reward = f"+{q['reward_coins']}🪙"
    if q["reward_meat"]:
        reward += f" +{q['reward_meat']}🍖"
    return f"{mark} {name} ({q['progress']}/{q['target']}) — {reward}"


def quests_kb(has_claimable: bool) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    if has_claimable:
        kb.button(text="🎁 Забрать награды", callback_data="quests:claim")
    kb.button(text="⬅️ Меню", callback_data="menu:main")
    kb.adjust(1)
    return kb


async def render_quests(user_id: int) -> tuple[str, InlineKeyboardBuilder]:
    quests = await ensure_today_quests(user_id)
    user = await db.get_user(user_id)

    quest_block = "\n".join(_quest_line(q) for q in quests)
    text = (
        f"<b>Задания на сегодня</b>\n\n"
        f"🔥 Стрик » {user['quest_streak']} дн.\n"
        f"<blockquote>{quest_block}</blockquote>"
    )

    has_claimable = any(q["completed"] and not q["reward_claimed"] for q in quests)
    if not has_claimable:
        text += "\n\nВыполни задания, чтобы открыть награды 🎁"

    return text, quests_kb(has_claimable)


@router.message(Command("quests"))
@router.message(Command("daily"))
async def cmd_quests(message: Message) -> None:
    text, kb = await render_quests(message.from_user.id)
    await message.answer(text, reply_markup=kb.as_markup())


@router.callback_query(F.data == "menu:quests")
async def cb_quests(callback: CallbackQuery) -> None:
    text, kb = await render_quests(callback.from_user.id)
    await callback.message.edit_text(text, reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(F.data == "quests:claim")
async def cb_claim(callback: CallbackQuery) -> None:
    today_key = today_msk_key()
    quests = await db.get_quests_for_day(callback.from_user.id, today_key)
    user = await db.get_user(callback.from_user.id)

    total_coins = total_meat = 0
    for q in quests:
        if q["completed"] and not q["reward_claimed"]:
            total_coins += q["reward_coins"]
            total_meat += q["reward_meat"]
            await db.update_quest_fields(q["quest_id"], reward_claimed=1)

    if total_coins == 0 and total_meat == 0:
        await callback.answer("Нет наград для получения.", show_alert=True)
        return

    await db.update_user_fields(
        callback.from_user.id,
        coins=user["coins"] + total_coins,
        meat=user["meat"] + total_meat,
    )

    text, kb = await render_quests(callback.from_user.id)
    await callback.message.edit_text(text, reply_markup=kb.as_markup())
    await callback.answer(f"Получено: +{total_coins}🪙 +{total_meat}🍖")
