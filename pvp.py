"""
Дуэли. Это MVP-реализация матчмейкинга: игроки встают в очередь, как только
набралось двое — бой разыгрывается сразу. В проде онлайн-фактор и реальный
realtime-матчинг считаются отдельным сервисом, здесь это упрощено до
функции _online_factor(), которую легко заменить на честные метрики.
"""
import datetime as dt
import random

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message

import database as db
import game_data as gd
import game_logic as gl
from handlers import quests

router = Router()

DUEL_FATIGUE_DELTA = 15

# Очередь на матчмейкинг: [(user_id, dragon_id, joined_at), ...]
_queue: list[tuple[int, int, dt.datetime]] = []


def _online_factor() -> float:
    """Заглушка: чем больше людей одновременно стоит в очереди, тем выше
    online_factor (меньше разброс наград). Подключите сюда реальную
    метрику активных пользователей за последние N минут."""
    return min(1.0, len(_queue) / 10)


def _is_weekend() -> bool:
    return dt.datetime.utcnow().weekday() >= 5


@router.message(Command("duel"))
async def cmd_duel(message: Message, bot: Bot) -> None:
    user = await db.get_user(message.from_user.id)
    if user is None:
        await message.answer("Сначала напиши /start.")
        return
    if not user["active_dragon_id"]:
        await message.answer("У тебя нет активного дракона. Выбери его в разделе «Драконы».")
        return

    dragon = await db.get_dragon(user["active_dragon_id"])
    stats = gl.effective_stats(dragon)
    if stats["is_banned"]:
        await message.answer("Твой дракон обессилен и не может сражаться — дай ему отдохнуть.")
        return

    min_level = gd.RARITIES[dragon["rarity"]]["min_duel_level"]
    if dragon["level"] < min_level:
        await message.answer(
            f"Твой дракон ещё мал для дуэлей 🌱 Нужен уровень {min_level} "
            f"(сейчас {dragon['level']}) — корми и тренируй его в разделе «Драконы»."
        )
        return

    if any(uid == message.from_user.id for uid, _, _ in _queue):
        await message.answer("Ты уже в очереди на дуэль, жди соперника ⏳")
        return

    _queue.append((message.from_user.id, dragon["dragon_id"], dt.datetime.utcnow()))
    await message.answer("🔍 Ищем тебе соперника...")

    if len(_queue) >= 2:
        (uid1, did1, _), (uid2, did2, _) = _queue[0], _queue[1]
        del _queue[0:2]
        await _resolve_duel(bot, uid1, did1, uid2, did2)


async def _resolve_duel(bot: Bot, uid1: int, did1: int, uid2: int, did2: int) -> None:
    user1, user2 = await db.get_user(uid1), await db.get_user(uid2)
    dragon1, dragon2 = await db.get_dragon(did1), await db.get_dragon(did2)
    stats1, stats2 = gl.effective_stats(dragon1), gl.effective_stats(dragon2)

    power1 = stats1["power"] + stats1["defense"] * 0.5 + stats1["speed"] * 0.3
    power2 = stats2["power"] + stats2["defense"] * 0.5 + stats2["speed"] * 0.3
    total = power1 + power2
    win_chance_1 = power1 / total if total > 0 else 0.5

    winner_is_1 = random.random() < win_chance_1
    winner_uid, winner_did = (uid1, did1) if winner_is_1 else (uid2, did2)
    loser_uid, loser_did = (uid2, did2) if winner_is_1 else (uid1, did1)
    winner_user, loser_user = (user1, user2) if winner_is_1 else (user2, user1)

    fangs_change = gl.calculate_fangs_change(
        winner_fangs=winner_user["fangs"],
        loser_fangs=loser_user["fangs"],
        winner_created_at=winner_user["created_at"],
        online_factor=_online_factor(),
        is_weekend=_is_weekend(),
    )

    await db.update_user_fields(winner_uid, fangs=winner_user["fangs"] + fangs_change)
    await db.update_user_fields(loser_uid, fangs=max(0, loser_user["fangs"] - fangs_change))

    for did in (did1, did2):
        dragon = await db.get_dragon(did)
        fatigue_now = gl.current_fatigue(dragon["fatigue"], dragon["fatigue_updated_at"], dragon["is_resting"])
        await db.update_dragon_fields(
            did,
            fatigue=min(100, fatigue_now + DUEL_FATIGUE_DELTA),
            fatigue_updated_at=dt.datetime.utcnow().isoformat(),
        )

    await quests.record_progress(uid1, "duel_play")
    await quests.record_progress(uid2, "duel_play")

    winner_dragon = await db.get_dragon(winner_did)
    loser_dragon = await db.get_dragon(loser_did)

    text_winner = (
        f"🏆 Победа! Твой {winner_dragon['name']} одолел {loser_dragon['name']}.\n"
        f"🦷 +{fangs_change} клыков."
    )
    text_loser = (
        f"💀 Поражение. Твой {loser_dragon['name']} проиграл {winner_dragon['name']}.\n"
        f"🦷 -{fangs_change} клыков."
    )

    try:
        await bot.send_message(winner_uid, text_winner)
    except Exception:
        pass
    try:
        await bot.send_message(loser_uid, text_loser)
    except Exception:
        pass
