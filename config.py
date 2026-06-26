"""
Конфигурация бота.
Токен берём из переменной окружения BOT_TOKEN, чтобы не хранить секреты в коде.
"""
import os
import datetime as dt
from zoneinfo import ZoneInfo

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv не установлен — тогда переменные нужно выставить вручную

BOT_TOKEN = os.getenv("BOT_TOKEN", "ВАШ_ТОКЕН_СЮДА")

# Все игровые "сутки" (магазин, ежедневки, ивенты) считаем по московскому времени
MSK = ZoneInfo("Europe/Moscow")

# Во сколько по МСК обновляется магазин
SHOP_REFRESH_HOUR = 11

# Ночное окно, когда ивенты не обновляются
EVENT_PAUSE_START_HOUR = 22
EVENT_PAUSE_END_HOUR = 6

DB_PATH = os.getenv("DB_PATH", "dragon_bot.db")


def msk_now() -> dt.datetime:
    return dt.datetime.now(MSK)


def today_msk_key() -> str:
    """Ключ календарного дня по МСК — используется для ежедневных квестов."""
    return msk_now().date().isoformat()


def season_key_for(date_: dt.date) -> str:
    """Ключ сезона топа — календарный месяц по МСК, например '2026-06'."""
    return date_.strftime("%Y-%m")
