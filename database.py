"""
Работа с базой данных (SQLite через aiosqlite).
Все функции — асинхронные, возвращают простые dict'ы, чтобы хендлерам
не нужно было знать про SQL.
"""
import datetime as dt
import aiosqlite

from config import DB_PATH
import game_data as gd

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    nickname TEXT NOT NULL,
    coins INTEGER NOT NULL DEFAULT 0,
    crystals INTEGER NOT NULL DEFAULT 0,
    exp INTEGER NOT NULL DEFAULT 0,
    meat INTEGER NOT NULL DEFAULT 0,
    fangs INTEGER NOT NULL DEFAULT 0,
    vip_status TEXT,
    active_dragon_id INTEGER,
    quest_streak INTEGER NOT NULL DEFAULT 0,
    quest_streak_day TEXT,
    last_explore_at TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dragons (
    dragon_id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id INTEGER NOT NULL,
    species_key TEXT NOT NULL,
    name TEXT NOT NULL,
    rarity TEXT NOT NULL,
    level INTEGER NOT NULL DEFAULT 1,
    exp INTEGER NOT NULL DEFAULT 0,
    fatigue INTEGER NOT NULL DEFAULT 0,
    fatigue_updated_at TEXT NOT NULL,
    is_resting INTEGER NOT NULL DEFAULT 0,
    rest_until TEXT,
    ability_key TEXT NOT NULL,
    ability_level INTEGER NOT NULL DEFAULT 1,
    armor_key TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS eggs (
    egg_id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id INTEGER NOT NULL,
    rarity TEXT NOT NULL,
    obtained_at TEXT NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS duels (
    duel_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player1_id INTEGER NOT NULL,
    player2_id INTEGER NOT NULL,
    winner_id INTEGER NOT NULL,
    fangs_change INTEGER NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS quests (
    quest_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    day_key TEXT NOT NULL,
    quest_key TEXT NOT NULL,
    target INTEGER NOT NULL,
    progress INTEGER NOT NULL DEFAULT 0,
    completed INTEGER NOT NULL DEFAULT 0,
    reward_claimed INTEGER NOT NULL DEFAULT 0,
    reward_coins INTEGER NOT NULL DEFAULT 0,
    reward_meat INTEGER NOT NULL DEFAULT 0,
    is_bonus INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS season_history (
    season_key TEXT NOT NULL,
    rank INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    nickname TEXT NOT NULL,
    fangs INTEGER NOT NULL,
    reward_claimed INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (season_key, rank)
);
"""


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA)
        await db.commit()


def _now() -> str:
    return dt.datetime.utcnow().isoformat()


# ── USERS ───────────────────────────────────────────────────────────────
async def get_user(user_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def create_user(user_id: int, nickname: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO users (user_id, nickname, created_at) VALUES (?, ?, ?)",
            (user_id, nickname, _now()),
        )
        await db.commit()


async def update_user_fields(user_id: int, **fields) -> None:
    if not fields:
        return
    cols = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [user_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE users SET {cols} WHERE user_id = ?", values)
        await db.commit()


# ── EGGS ────────────────────────────────────────────────────────────────
async def add_egg(owner_id: int, rarity: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO eggs (owner_id, rarity, obtained_at) VALUES (?, ?, ?)",
            (owner_id, rarity, _now()),
        )
        await db.commit()
        return cur.lastrowid


async def get_eggs(owner_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM eggs WHERE owner_id = ?", (owner_id,))
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def delete_egg(egg_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM eggs WHERE egg_id = ?", (egg_id,))
        await db.commit()


# ── DRAGONS ─────────────────────────────────────────────────────────────
async def create_dragon(owner_id: int, species_key: str, rarity: str, name: str, ability_key: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """INSERT INTO dragons
               (owner_id, species_key, name, rarity, fatigue_updated_at, ability_key, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (owner_id, species_key, name, rarity, _now(), ability_key, _now()),
        )
        await db.commit()
        return cur.lastrowid


async def get_dragon(dragon_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM dragons WHERE dragon_id = ?", (dragon_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def get_user_dragons(owner_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM dragons WHERE owner_id = ?", (owner_id,))
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def update_dragon_fields(dragon_id: int, **fields) -> None:
    if not fields:
        return
    cols = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [dragon_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE dragons SET {cols} WHERE dragon_id = ?", values)
        await db.commit()


async def delete_dragon(dragon_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM dragons WHERE dragon_id = ?", (dragon_id,))
        await db.commit()


# ── QUESTS ──────────────────────────────────────────────────────────────
async def create_quest(
    user_id: int, day_key: str, quest_key: str, target: int,
    reward_coins: int, reward_meat: int, is_bonus: bool = False,
) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """INSERT INTO quests
               (user_id, day_key, quest_key, target, reward_coins, reward_meat, is_bonus)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, day_key, quest_key, target, reward_coins, reward_meat, int(is_bonus)),
        )
        await db.commit()
        return cur.lastrowid


async def get_quests_for_day(user_id: int, day_key: str) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM quests WHERE user_id = ? AND day_key = ? ORDER BY is_bonus, quest_id",
            (user_id, day_key),
        )
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def update_quest_fields(quest_id: int, **fields) -> None:
    if not fields:
        return
    cols = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [quest_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE quests SET {cols} WHERE quest_id = ?", values)
        await db.commit()


# ── META (служебные глобальные значения, напр. текущий ключ сезона) ─────
async def get_meta(key: str) -> str | None:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT value FROM meta WHERE key = ?", (key,))
        row = await cur.fetchone()
        return row[0] if row else None


async def set_meta(key: str, value: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO meta (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        await db.commit()


# ── ТОПЫ / СЕЗОНЫ ───────────────────────────────────────────────────────
async def get_top_users(limit: int = 10) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT user_id, nickname, fangs FROM users WHERE fangs > 0 ORDER BY fangs DESC LIMIT ?",
            (limit,),
        )
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def get_user_rank(user_id: int, fangs: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users WHERE fangs > ?", (fangs,))
        row = await cur.fetchone()
        return row[0] + 1


async def reset_all_fangs() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET fangs = 0")
        await db.commit()


async def save_season_history(season_key: str, rows: list[dict]) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executemany(
            """INSERT OR REPLACE INTO season_history
               (season_key, rank, user_id, nickname, fangs, reward_claimed)
               VALUES (?, ?, ?, ?, ?, 0)""",
            [(season_key, r["rank"], r["user_id"], r["nickname"], r["fangs"]) for r in rows],
        )
        await db.commit()


async def get_unclaimed_season_rewards(user_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM season_history WHERE user_id = ? AND reward_claimed = 0",
            (user_id,),
        )
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def claim_season_reward(season_key: str, rank: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE season_history SET reward_claimed = 1 WHERE season_key = ? AND rank = ?",
            (season_key, rank),
        )
        await db.commit()
