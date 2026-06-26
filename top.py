"""
Топ игроков по клыкам. Сезон = календарный месяц по МСК.

Сброс сезона сделан "лениво": при каждом обращении к топу проверяем,
не сменился ли месяц с последнего сохранённого ключа сезона в meta.
Если сменился — снимаем снапшот топ-N в season_history, начисляем
награды (как ожидающие выдачи) и обнуляем клыки всем игрокам.
Это не требует отдельного планировщика/cron — таблица лидеров и так
просматривается игроками регулярно, этого достаточно для лайв-проекта
такого масштаба.
"""
import calendar
import datetime as dt

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database as db
import game_data as gd
from config import msk_now, season_key_for

router = Router()

MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}


async def maybe_reset_season() -> None:
    now = msk_now()
    current_key = season_key_for(now.date())
    stored_key = await db.get_meta("season_key")

    if stored_key is None:
        # первый запуск бота — просто фиксируем текущий сезон, ничего не сбрасываем
        await db.set_meta("season_key", current_key)
        return

    if stored_key == current_key:
        return  # сезон ещё не закончился

    top_users = await db.get_top_users(limit=gd.SEASON_TOP_SNAPSHOT_SIZE)
    if top_users:
        rows = [
            {"rank": i + 1, "user_id": u["user_id"], "nickname": u["nickname"], "fangs": u["fangs"]}
            for i, u in enumerate(top_users)
        ]
        await db.save_season_history(stored_key, rows)

    await db.reset_all_fangs()
    await db.set_meta("season_key", current_key)


def _days_left_in_month(now: dt.datetime) -> int:
    last_day = calendar.monthrange(now.year, now.month)[1]
    return last_day - now.day


def top_kb(has_rewards: bool) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    if has_rewards:
        kb.button(text="🎁 Награды сезона", callback_data="top:rewards")
    kb.button(text="⬅️ Меню", callback_data="menu:main")
    kb.adjust(1)
    return kb


async def render_top(user_id: int) -> tuple[str, InlineKeyboardBuilder]:
    await maybe_reset_season()

    top_users = await db.get_top_users(limit=10)
    user = await db.get_user(user_id)
    days_left = _days_left_in_month(msk_now())

    lines = ["<b>Топ сезона по клыкам</b>", "", f"До конца сезона: {days_left} дн.", ""]
    if not top_users:
        lines.append("Топ пока пуст — стань первым, сыграй дуэль! ⚔️")
    else:
        rows = []
        for i, u in enumerate(top_users, start=1):
            medal = MEDALS.get(i, f"{i}.")
            rows.append(f"{medal} {u['nickname']} » {u['fangs']} 🦷")
        lines.append("<blockquote>" + "\n".join(rows) + "</blockquote>")

    if user and user["fangs"] > 0 and not any(u["user_id"] == user_id for u in top_users):
        rank = await db.get_user_rank(user_id, user["fangs"])
        lines.append(f"\nТвоё место » #{rank} ({user['fangs']} 🦷)")

    rewards = await db.get_unclaimed_season_rewards(user_id) if user else []
    return "\n".join(lines), top_kb(bool(rewards))


@router.message(Command("top"))
async def cmd_top(message: Message) -> None:
    text, kb = await render_top(message.from_user.id)
    await message.answer(text, reply_markup=kb.as_markup())


@router.callback_query(F.data == "menu:top")
async def cb_top(callback: CallbackQuery) -> None:
    text, kb = await render_top(callback.from_user.id)
    await callback.message.edit_text(text, reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(F.data == "top:rewards")
async def cb_rewards(callback: CallbackQuery) -> None:
    rewards = await db.get_unclaimed_season_rewards(callback.from_user.id)
    if not rewards:
        await callback.answer("Нет наград для получения.", show_alert=True)
        return

    user = await db.get_user(callback.from_user.id)
    total_coins = total_meat = 0
    lines = ["🎁 <b>Награды за прошлые сезоны</b>", ""]
    for r in rewards:
        coins, meat = gd.season_reward_for_rank(r["rank"])
        total_coins += coins
        total_meat += meat
        lines.append(f"Сезон {r['season_key']} · место #{r['rank']} — +{coins}🪙 +{meat}🍖")
        await db.claim_season_reward(r["season_key"], r["rank"])

    await db.update_user_fields(
        callback.from_user.id,
        coins=user["coins"] + total_coins,
        meat=user["meat"] + total_meat,
    )

    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ К топу", callback_data="menu:top")
    await callback.message.edit_text("\n".join(lines), reply_markup=kb.as_markup())
    await callback.answer(f"Получено: +{total_coins}🪙 +{total_meat}🍖")
