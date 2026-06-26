"""
Чистая игровая логика — никакого Telegram и SQL здесь, только формулы.
Это специально вынесено отдельно, чтобы баланс можно было крутить и
тестировать независимо от бота.
"""
import datetime as dt
import random

import game_data as gd


# ──────────────────────────────────────────────────────────────────────────
# УСТАЛОСТЬ
# ──────────────────────────────────────────────────────────────────────────
def current_fatigue(fatigue_at_save: int, updated_at_iso: str, is_resting: bool) -> int:
    """Считаем усталость на текущий момент с учётом естественного восстановления.

    0-50%   — дракон в порядке
    50-100% — статы начинают падать (см. fatigue_stat_multiplier)
    100%    — полный бан, нужен отдых (REST_HOURS)
    """
    last = dt.datetime.fromisoformat(updated_at_iso)
    hours_passed = (dt.datetime.utcnow() - last).total_seconds() / 3600
    decay = hours_passed * gd.FATIGUE_DECAY_PER_HOUR
    value = fatigue_at_save - decay
    return max(0, min(100, round(value)))


def fatigue_stat_multiplier(fatigue: int) -> float:
    """До 50% усталости статы дракона полные. После — линейно падают,
    при 100% усталости дракон не может сражаться (но это проверяется отдельно
    флагом is_banned_by_fatigue, а не множителем)."""
    if fatigue <= gd.FATIGUE_SOFT_CAP:
        return 1.0
    # на отрезке 50→100 множитель уходит с 1.0 до 0.4
    over = fatigue - gd.FATIGUE_SOFT_CAP  # 0..50
    return 1.0 - (over / 50) * 0.6


def is_banned_by_fatigue(fatigue: int) -> bool:
    return fatigue >= gd.FATIGUE_HARD_CAP


# ──────────────────────────────────────────────────────────────────────────
# СТАТЫ И ПРОКАЧКА
# ──────────────────────────────────────────────────────────────────────────
def effective_stats(dragon: dict) -> dict:
    species = gd.SPECIES[dragon["species_key"]]
    rarity_mult = gd.RARITIES[dragon["rarity"]]["stat_mult"]
    level = dragon["level"]
    fatigue = current_fatigue(dragon["fatigue"], dragon["fatigue_updated_at"], dragon["is_resting"])
    fmult = fatigue_stat_multiplier(fatigue)

    level_mult = 1 + (level - 1) * 0.08  # +8% к статам за уровень

    power = species["base_power"] * rarity_mult * level_mult
    defense = species["base_defense"] * rarity_mult * level_mult
    speed = species["base_speed"] * rarity_mult * level_mult

    if dragon.get("armor_key") and dragon["armor_key"] in gd.ARMOR_CATALOG:
        defense += gd.ARMOR_CATALOG[dragon["armor_key"]]["defense_bonus"]

    return {
        "power": round(power * fmult),
        "defense": round(defense * fmult),
        "speed": round(speed * fmult),
        "fatigue": fatigue,
        "is_banned": is_banned_by_fatigue(fatigue),
    }


def add_dragon_exp(dragon: dict, exp_gain: int) -> tuple[int, int]:
    """Возвращает (новый_level, новый_exp) после начисления опыта."""
    level = dragon["level"]
    exp = dragon["exp"] + exp_gain
    while exp >= gd.exp_to_next_level(level):
        exp -= gd.exp_to_next_level(level)
        level += 1
    return level, exp


# ──────────────────────────────────────────────────────────────────────────
# ВЫПАДЕНИЕ ЯИЦ ПО РЕДКОСТИ
# ──────────────────────────────────────────────────────────────────────────
def roll_egg_rarity() -> str:
    rarities = list(gd.RARITIES.keys())
    weights = [gd.RARITIES[r]["weight"] for r in rarities]
    return random.choices(rarities, weights=weights, k=1)[0]


def roll_species_for_rarity(rarity: str) -> str:
    pool = [key for key, s in gd.SPECIES.items() if s["rarity"] == rarity]
    if not pool:
        # если для редкости пока нет видов в данных — берём любой ближайший
        pool = list(gd.SPECIES.keys())
    return random.choice(pool)


def roll_ability_for_species(species_key: str) -> str:
    element = gd.SPECIES[species_key]["element"]
    pool = [k for k, a in gd.ABILITIES.items() if a["element"] == element]
    return random.choice(pool) if pool else random.choice(list(gd.ABILITIES.keys()))


# ──────────────────────────────────────────────────────────────────────────
# PVP: ИЗМЕНЕНИЕ КЛЫКОВ (трофеев)
# ──────────────────────────────────────────────────────────────────────────
MAX_FANGS_GAIN = 10        # обычный максимум за победу
MAX_FANGS_GAIN_BOOST = 15  # максимум в выходные / для новичков
NEWBIE_PERIOD_DAYS = 3     # сколько дней действует буст новичка


def _is_newbie(created_at_iso: str) -> bool:
    created = dt.datetime.fromisoformat(created_at_iso)
    return (dt.datetime.utcnow() - created).days < NEWBIE_PERIOD_DAYS


def calculate_fangs_change(
    winner_fangs: int,
    loser_fangs: int,
    winner_created_at: str,
    online_factor: float = 1.0,
    is_weekend: bool = False,
) -> int:
    """Сколько клыков получит победитель (у проигравшего снимут столько же).

    Правила:
    - онлайн большой -> разброс маленький, онлайн маленький -> разброс больше
      (online_factor: 0..1, где 1 — высокий онлайн)
    - первые NEWBIE_PERIOD_DAYS дней после регистрации — буст для новичков:
      даже при 0 клыков у обоих новичок получит гарантированный минимум
    - защита от фарма: если у победителя намного больше клыков, чем у
      проигравшего, награда стремится к 0
    - в выходные потолок награды выше (MAX_FANGS_GAIN_BOOST)
    """
    cap = MAX_FANGS_GAIN_BOOST if is_weekend else MAX_FANGS_GAIN

    # базовая доля от разницы клыков противника относительно своих —
    # чем сильнее соперник относительно тебя, тем больше дают
    if winner_fangs <= 0:
        ratio = 1.0
    else:
        ratio = loser_fangs / winner_fangs
        ratio = max(0.0, min(1.5, ratio))  # ограничиваем разгон

    base_gain = cap * min(1.0, ratio)

    # маленький онлайн -> шире разброс результата (случайный множитель)
    spread = 1.0 + (1.0 - online_factor) * 0.5
    randomized = base_gain * random.uniform(1 / spread, spread)

    gain = round(randomized)

    # буст новичкам: гарантированный минимум, даже если оба на 0 клыков
    if _is_newbie(winner_created_at) and gain < cap // 2:
        gain = cap // 2 if not is_weekend else MAX_FANGS_GAIN_BOOST // 2

    return max(0, min(cap, gain))


# ──────────────────────────────────────────────────────────────────────────
# МАГАЗИН: ЦЕНА СКУПКИ ДРАКОНА
# ──────────────────────────────────────────────────────────────────────────
def dragon_sell_price(dragon: dict) -> int:
    rarity_mult = gd.RARITIES[dragon["rarity"]]["stat_mult"]
    base_price = 40 * rarity_mult
    level_bonus = dragon["level"] * 12
    ability_bonus = dragon["ability_level"] * 20
    return round(base_price + level_bonus + ability_bonus)
