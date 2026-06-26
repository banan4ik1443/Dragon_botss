"""
Статичные игровые данные.
Это "контентная" часть — добавление новых драконов/редкостей не требует
правок логики, только дополнения словарей ниже.
"""

# ──────────────────────────────────────────────────────────────────────────
# РЕДКОСТИ ЯИЦ / ДРАКОНОВ
# ──────────────────────────────────────────────────────────────────────────
# weight       — вес для рандомного выпадения (чем больше, тем чаще)
# weight          — вес для рандомного выпадения (чем больше, тем чаще)
# min_duel_level  — с какого уровня дракон этой редкости допускается до дуэлей
#                   (чем реже дракон, тем дольше его растить перед боями —
#                   именно это и есть "время ожидания", а не таймер на яйце)
# stat_mult       — множитель к базовым характеристикам дракона этой редкости
# ability_slots   — сколько спец. способностей получает дракон такой редкости
# emoji/flair     — для анимации открытия яйца
RARITIES = {
    "common":    {"name": "Обычный",      "weight": 45, "min_duel_level": 3,  "stat_mult": 1.0, "ability_slots": 1, "emoji": "⚪️", "flair": ""},
    "uncommon":  {"name": "Необычный",    "weight": 27, "min_duel_level": 4,  "stat_mult": 1.2, "ability_slots": 1, "emoji": "🟢", "flair": ""},
    "rare":      {"name": "Редкий",       "weight": 15, "min_duel_level": 5,  "stat_mult": 1.5, "ability_slots": 2, "emoji": "🔵", "flair": "✨"},
    "epic":      {"name": "Эпический",    "weight": 8,  "min_duel_level": 6,  "stat_mult": 2.0, "ability_slots": 2, "emoji": "🟣", "flair": "✨⚡️"},
    "legendary": {"name": "Легендарный",  "weight": 4,  "min_duel_level": 8,  "stat_mult": 2.8, "ability_slots": 3, "emoji": "🟡", "flair": "🌟⚡️🌟"},
    "mythic":    {"name": "Мифический",   "weight": 1,  "min_duel_level": 10, "stat_mult": 4.0, "ability_slots": 3, "emoji": "🔴", "flair": "💥🌟⚡️🌟💥"},
}
RARITY_ORDER = ["common", "uncommon", "rare", "epic", "legendary", "mythic"]

# ──────────────────────────────────────────────────────────────────────────
# СТИХИИ / ЭЛЕМЕНТЫ — на них завязаны ивенты ("Гроза" усиливает молнию и т.п.)
# ──────────────────────────────────────────────────────────────────────────
ELEMENTS = ["fire", "water", "earth", "lightning", "ice", "shadow", "light", "wind"]
ELEMENT_NAMES = {
    "fire": "Огонь", "water": "Вода", "earth": "Земля", "lightning": "Молния",
    "ice": "Лёд", "shadow": "Тень", "light": "Свет", "wind": "Ветер",
}

# ──────────────────────────────────────────────────────────────────────────
# СПЕЦ. СПОСОБНОСТИ — у дракона появляются сразу, прокачиваются отдельно
# ──────────────────────────────────────────────────────────────────────────
# Реальный список будет в разы больше, здесь — основа для каждой стихии.
ABILITIES = {
    "fire_breath":      {"name": "Огненное дыхание",  "element": "fire",       "base_power": 12},
    "tidal_wave":       {"name": "Волна",              "element": "water",      "base_power": 10},
    "stone_skin":       {"name": "Каменная кожа",      "element": "earth",      "base_power": 8},
    "thunder_strike":   {"name": "Удар молнии",        "element": "lightning",  "base_power": 14},
    "frost_bite":       {"name": "Ледяной укус",       "element": "ice",        "base_power": 11},
    "shadow_step":      {"name": "Шаг тени",           "element": "shadow",     "base_power": 13},
    "radiant_glow":     {"name": "Сияние",             "element": "light",      "base_power": 9},
    "gale_force":       {"name": "Порыв ветра",        "element": "wind",       "base_power": 10},
}

# ──────────────────────────────────────────────────────────────────────────
# ВИДЫ ДРАКОНОВ — полный ростер: 8 стихий × 6 редкостей × 3 боевых варианта
# (Агрессивный / Сбалансированный / Стойкий) = 144 уникальных вида.
# Полная таблица с подробностями — в файле dragon_bot_full_roster.xlsx
# ──────────────────────────────────────────────────────────────────────────
SPECIES = {
    "fire_common_aggro": {"name": "Огненный детёныш", "element": "fire", "rarity": "common", "base_power": 15.0, "base_defense": 5.6, "base_speed": 9.0},
    "fire_common_balanced": {"name": "Огненный птенец", "element": "fire", "rarity": "common", "base_power": 12.0, "base_defense": 7.0, "base_speed": 9.0},
    "fire_common_tanky": {"name": "Огненный малыш", "element": "fire", "rarity": "common", "base_power": 10.2, "base_defense": 9.1, "base_speed": 8.1},
    "fire_uncommon_aggro": {"name": "Огненный дракончик", "element": "fire", "rarity": "uncommon", "base_power": 15.0, "base_defense": 5.6, "base_speed": 9.0},
    "fire_uncommon_balanced": {"name": "Огненный змеёныш", "element": "fire", "rarity": "uncommon", "base_power": 12.0, "base_defense": 7.0, "base_speed": 9.0},
    "fire_uncommon_tanky": {"name": "Огненный ящер", "element": "fire", "rarity": "uncommon", "base_power": 10.2, "base_defense": 9.1, "base_speed": 8.1},
    "fire_rare_aggro": {"name": "Огненный страж", "element": "fire", "rarity": "rare", "base_power": 15.0, "base_defense": 5.6, "base_speed": 9.0},
    "fire_rare_balanced": {"name": "Огненный охотник", "element": "fire", "rarity": "rare", "base_power": 12.0, "base_defense": 7.0, "base_speed": 9.0},
    "fire_rare_tanky": {"name": "Огненный хищник", "element": "fire", "rarity": "rare", "base_power": 10.2, "base_defense": 9.1, "base_speed": 8.1},
    "fire_epic_aggro": {"name": "Огненный вирм", "element": "fire", "rarity": "epic", "base_power": 15.0, "base_defense": 5.6, "base_speed": 9.0},
    "fire_epic_balanced": {"name": "Огненный колосс", "element": "fire", "rarity": "epic", "base_power": 12.0, "base_defense": 7.0, "base_speed": 9.0},
    "fire_epic_tanky": {"name": "Огненный разрушитель", "element": "fire", "rarity": "epic", "base_power": 10.2, "base_defense": 9.1, "base_speed": 8.1},
    "fire_legendary_aggro": {"name": "Огненный архонт", "element": "fire", "rarity": "legendary", "base_power": 15.0, "base_defense": 5.6, "base_speed": 9.0},
    "fire_legendary_balanced": {"name": "Огненный титан", "element": "fire", "rarity": "legendary", "base_power": 12.0, "base_defense": 7.0, "base_speed": 9.0},
    "fire_legendary_tanky": {"name": "Огненный владыка", "element": "fire", "rarity": "legendary", "base_power": 10.2, "base_defense": 9.1, "base_speed": 8.1},
    "fire_mythic_aggro": {"name": "Огненный император", "element": "fire", "rarity": "mythic", "base_power": 15.0, "base_defense": 5.6, "base_speed": 9.0},
    "fire_mythic_balanced": {"name": "Огненный повелитель", "element": "fire", "rarity": "mythic", "base_power": 12.0, "base_defense": 7.0, "base_speed": 9.0},
    "fire_mythic_tanky": {"name": "Огненный первородный", "element": "fire", "rarity": "mythic", "base_power": 10.2, "base_defense": 9.1, "base_speed": 8.1},
    "water_common_aggro": {"name": "Морской детёныш", "element": "water", "rarity": "common", "base_power": 11.2, "base_defense": 8.0, "base_speed": 9.0},
    "water_common_balanced": {"name": "Морской птенец", "element": "water", "rarity": "common", "base_power": 9.0, "base_defense": 10.0, "base_speed": 9.0},
    "water_common_tanky": {"name": "Морской малыш", "element": "water", "rarity": "common", "base_power": 7.6, "base_defense": 13.0, "base_speed": 8.1},
    "water_uncommon_aggro": {"name": "Морской дракончик", "element": "water", "rarity": "uncommon", "base_power": 11.2, "base_defense": 8.0, "base_speed": 9.0},
    "water_uncommon_balanced": {"name": "Морской змеёныш", "element": "water", "rarity": "uncommon", "base_power": 9.0, "base_defense": 10.0, "base_speed": 9.0},
    "water_uncommon_tanky": {"name": "Морской ящер", "element": "water", "rarity": "uncommon", "base_power": 7.6, "base_defense": 13.0, "base_speed": 8.1},
    "water_rare_aggro": {"name": "Морской страж", "element": "water", "rarity": "rare", "base_power": 11.2, "base_defense": 8.0, "base_speed": 9.0},
    "water_rare_balanced": {"name": "Морской охотник", "element": "water", "rarity": "rare", "base_power": 9.0, "base_defense": 10.0, "base_speed": 9.0},
    "water_rare_tanky": {"name": "Морской хищник", "element": "water", "rarity": "rare", "base_power": 7.6, "base_defense": 13.0, "base_speed": 8.1},
    "water_epic_aggro": {"name": "Морской вирм", "element": "water", "rarity": "epic", "base_power": 11.2, "base_defense": 8.0, "base_speed": 9.0},
    "water_epic_balanced": {"name": "Морской колосс", "element": "water", "rarity": "epic", "base_power": 9.0, "base_defense": 10.0, "base_speed": 9.0},
    "water_epic_tanky": {"name": "Морской разрушитель", "element": "water", "rarity": "epic", "base_power": 7.6, "base_defense": 13.0, "base_speed": 8.1},
    "water_legendary_aggro": {"name": "Морской архонт", "element": "water", "rarity": "legendary", "base_power": 11.2, "base_defense": 8.0, "base_speed": 9.0},
    "water_legendary_balanced": {"name": "Морской титан", "element": "water", "rarity": "legendary", "base_power": 9.0, "base_defense": 10.0, "base_speed": 9.0},
    "water_legendary_tanky": {"name": "Морской владыка", "element": "water", "rarity": "legendary", "base_power": 7.6, "base_defense": 13.0, "base_speed": 8.1},
    "water_mythic_aggro": {"name": "Морской император", "element": "water", "rarity": "mythic", "base_power": 11.2, "base_defense": 8.0, "base_speed": 9.0},
    "water_mythic_balanced": {"name": "Морской повелитель", "element": "water", "rarity": "mythic", "base_power": 9.0, "base_defense": 10.0, "base_speed": 9.0},
    "water_mythic_tanky": {"name": "Морской первородный", "element": "water", "rarity": "mythic", "base_power": 7.6, "base_defense": 13.0, "base_speed": 8.1},
    "earth_common_aggro": {"name": "Каменный детёныш", "element": "earth", "rarity": "common", "base_power": 10.0, "base_defense": 11.2, "base_speed": 6.0},
    "earth_common_balanced": {"name": "Каменный птенец", "element": "earth", "rarity": "common", "base_power": 8.0, "base_defense": 14.0, "base_speed": 6.0},
    "earth_common_tanky": {"name": "Каменный малыш", "element": "earth", "rarity": "common", "base_power": 6.8, "base_defense": 18.2, "base_speed": 5.4},
    "earth_uncommon_aggro": {"name": "Каменный дракончик", "element": "earth", "rarity": "uncommon", "base_power": 10.0, "base_defense": 11.2, "base_speed": 6.0},
    "earth_uncommon_balanced": {"name": "Каменный змеёныш", "element": "earth", "rarity": "uncommon", "base_power": 8.0, "base_defense": 14.0, "base_speed": 6.0},
    "earth_uncommon_tanky": {"name": "Каменный ящер", "element": "earth", "rarity": "uncommon", "base_power": 6.8, "base_defense": 18.2, "base_speed": 5.4},
    "earth_rare_aggro": {"name": "Каменный страж", "element": "earth", "rarity": "rare", "base_power": 10.0, "base_defense": 11.2, "base_speed": 6.0},
    "earth_rare_balanced": {"name": "Каменный охотник", "element": "earth", "rarity": "rare", "base_power": 8.0, "base_defense": 14.0, "base_speed": 6.0},
    "earth_rare_tanky": {"name": "Каменный хищник", "element": "earth", "rarity": "rare", "base_power": 6.8, "base_defense": 18.2, "base_speed": 5.4},
    "earth_epic_aggro": {"name": "Каменный вирм", "element": "earth", "rarity": "epic", "base_power": 10.0, "base_defense": 11.2, "base_speed": 6.0},
    "earth_epic_balanced": {"name": "Каменный колосс", "element": "earth", "rarity": "epic", "base_power": 8.0, "base_defense": 14.0, "base_speed": 6.0},
    "earth_epic_tanky": {"name": "Каменный разрушитель", "element": "earth", "rarity": "epic", "base_power": 6.8, "base_defense": 18.2, "base_speed": 5.4},
    "earth_legendary_aggro": {"name": "Каменный архонт", "element": "earth", "rarity": "legendary", "base_power": 10.0, "base_defense": 11.2, "base_speed": 6.0},
    "earth_legendary_balanced": {"name": "Каменный титан", "element": "earth", "rarity": "legendary", "base_power": 8.0, "base_defense": 14.0, "base_speed": 6.0},
    "earth_legendary_tanky": {"name": "Каменный владыка", "element": "earth", "rarity": "legendary", "base_power": 6.8, "base_defense": 18.2, "base_speed": 5.4},
    "earth_mythic_aggro": {"name": "Каменный император", "element": "earth", "rarity": "mythic", "base_power": 10.0, "base_defense": 11.2, "base_speed": 6.0},
    "earth_mythic_balanced": {"name": "Каменный повелитель", "element": "earth", "rarity": "mythic", "base_power": 8.0, "base_defense": 14.0, "base_speed": 6.0},
    "earth_mythic_tanky": {"name": "Каменный первородный", "element": "earth", "rarity": "mythic", "base_power": 6.8, "base_defense": 18.2, "base_speed": 5.4},
    "lightning_common_aggro": {"name": "Грозовой детёныш", "element": "lightning", "rarity": "common", "base_power": 13.8, "base_defense": 4.8, "base_speed": 13.0},
    "lightning_common_balanced": {"name": "Грозовой птенец", "element": "lightning", "rarity": "common", "base_power": 11.0, "base_defense": 6.0, "base_speed": 13.0},
    "lightning_common_tanky": {"name": "Грозовой малыш", "element": "lightning", "rarity": "common", "base_power": 9.4, "base_defense": 7.8, "base_speed": 11.7},
    "lightning_uncommon_aggro": {"name": "Грозовой дракончик", "element": "lightning", "rarity": "uncommon", "base_power": 13.8, "base_defense": 4.8, "base_speed": 13.0},
    "lightning_uncommon_balanced": {"name": "Грозовой змеёныш", "element": "lightning", "rarity": "uncommon", "base_power": 11.0, "base_defense": 6.0, "base_speed": 13.0},
    "lightning_uncommon_tanky": {"name": "Грозовой ящер", "element": "lightning", "rarity": "uncommon", "base_power": 9.4, "base_defense": 7.8, "base_speed": 11.7},
    "lightning_rare_aggro": {"name": "Грозовой страж", "element": "lightning", "rarity": "rare", "base_power": 13.8, "base_defense": 4.8, "base_speed": 13.0},
    "lightning_rare_balanced": {"name": "Грозовой охотник", "element": "lightning", "rarity": "rare", "base_power": 11.0, "base_defense": 6.0, "base_speed": 13.0},
    "lightning_rare_tanky": {"name": "Грозовой хищник", "element": "lightning", "rarity": "rare", "base_power": 9.4, "base_defense": 7.8, "base_speed": 11.7},
    "lightning_epic_aggro": {"name": "Грозовой вирм", "element": "lightning", "rarity": "epic", "base_power": 13.8, "base_defense": 4.8, "base_speed": 13.0},
    "lightning_epic_balanced": {"name": "Грозовой колосс", "element": "lightning", "rarity": "epic", "base_power": 11.0, "base_defense": 6.0, "base_speed": 13.0},
    "lightning_epic_tanky": {"name": "Грозовой разрушитель", "element": "lightning", "rarity": "epic", "base_power": 9.4, "base_defense": 7.8, "base_speed": 11.7},
    "lightning_legendary_aggro": {"name": "Грозовой архонт", "element": "lightning", "rarity": "legendary", "base_power": 13.8, "base_defense": 4.8, "base_speed": 13.0},
    "lightning_legendary_balanced": {"name": "Грозовой титан", "element": "lightning", "rarity": "legendary", "base_power": 11.0, "base_defense": 6.0, "base_speed": 13.0},
    "lightning_legendary_tanky": {"name": "Грозовой владыка", "element": "lightning", "rarity": "legendary", "base_power": 9.4, "base_defense": 7.8, "base_speed": 11.7},
    "lightning_mythic_aggro": {"name": "Грозовой император", "element": "lightning", "rarity": "mythic", "base_power": 13.8, "base_defense": 4.8, "base_speed": 13.0},
    "lightning_mythic_balanced": {"name": "Грозовой повелитель", "element": "lightning", "rarity": "mythic", "base_power": 11.0, "base_defense": 6.0, "base_speed": 13.0},
    "lightning_mythic_tanky": {"name": "Грозовой первородный", "element": "lightning", "rarity": "mythic", "base_power": 9.4, "base_defense": 7.8, "base_speed": 11.7},
    "ice_common_aggro": {"name": "Ледяной детёныш", "element": "ice", "rarity": "common", "base_power": 12.5, "base_defense": 8.8, "base_speed": 7.0},
    "ice_common_balanced": {"name": "Ледяной птенец", "element": "ice", "rarity": "common", "base_power": 10.0, "base_defense": 11.0, "base_speed": 7.0},
    "ice_common_tanky": {"name": "Ледяной малыш", "element": "ice", "rarity": "common", "base_power": 8.5, "base_defense": 14.3, "base_speed": 6.3},
    "ice_uncommon_aggro": {"name": "Ледяной дракончик", "element": "ice", "rarity": "uncommon", "base_power": 12.5, "base_defense": 8.8, "base_speed": 7.0},
    "ice_uncommon_balanced": {"name": "Ледяной змеёныш", "element": "ice", "rarity": "uncommon", "base_power": 10.0, "base_defense": 11.0, "base_speed": 7.0},
    "ice_uncommon_tanky": {"name": "Ледяной ящер", "element": "ice", "rarity": "uncommon", "base_power": 8.5, "base_defense": 14.3, "base_speed": 6.3},
    "ice_rare_aggro": {"name": "Ледяной страж", "element": "ice", "rarity": "rare", "base_power": 12.5, "base_defense": 8.8, "base_speed": 7.0},
    "ice_rare_balanced": {"name": "Ледяной охотник", "element": "ice", "rarity": "rare", "base_power": 10.0, "base_defense": 11.0, "base_speed": 7.0},
    "ice_rare_tanky": {"name": "Ледяной хищник", "element": "ice", "rarity": "rare", "base_power": 8.5, "base_defense": 14.3, "base_speed": 6.3},
    "ice_epic_aggro": {"name": "Ледяной вирм", "element": "ice", "rarity": "epic", "base_power": 12.5, "base_defense": 8.8, "base_speed": 7.0},
    "ice_epic_balanced": {"name": "Ледяной колосс", "element": "ice", "rarity": "epic", "base_power": 10.0, "base_defense": 11.0, "base_speed": 7.0},
    "ice_epic_tanky": {"name": "Ледяной разрушитель", "element": "ice", "rarity": "epic", "base_power": 8.5, "base_defense": 14.3, "base_speed": 6.3},
    "ice_legendary_aggro": {"name": "Ледяной архонт", "element": "ice", "rarity": "legendary", "base_power": 12.5, "base_defense": 8.8, "base_speed": 7.0},
    "ice_legendary_balanced": {"name": "Ледяной титан", "element": "ice", "rarity": "legendary", "base_power": 10.0, "base_defense": 11.0, "base_speed": 7.0},
    "ice_legendary_tanky": {"name": "Ледяной владыка", "element": "ice", "rarity": "legendary", "base_power": 8.5, "base_defense": 14.3, "base_speed": 6.3},
    "ice_mythic_aggro": {"name": "Ледяной император", "element": "ice", "rarity": "mythic", "base_power": 12.5, "base_defense": 8.8, "base_speed": 7.0},
    "ice_mythic_balanced": {"name": "Ледяной повелитель", "element": "ice", "rarity": "mythic", "base_power": 10.0, "base_defense": 11.0, "base_speed": 7.0},
    "ice_mythic_tanky": {"name": "Ледяной первородный", "element": "ice", "rarity": "mythic", "base_power": 8.5, "base_defense": 14.3, "base_speed": 6.3},
    "shadow_common_aggro": {"name": "Тёмный детёныш", "element": "shadow", "rarity": "common", "base_power": 15.0, "base_defense": 5.6, "base_speed": 12.0},
    "shadow_common_balanced": {"name": "Тёмный птенец", "element": "shadow", "rarity": "common", "base_power": 12.0, "base_defense": 7.0, "base_speed": 12.0},
    "shadow_common_tanky": {"name": "Тёмный малыш", "element": "shadow", "rarity": "common", "base_power": 10.2, "base_defense": 9.1, "base_speed": 10.8},
    "shadow_uncommon_aggro": {"name": "Тёмный дракончик", "element": "shadow", "rarity": "uncommon", "base_power": 15.0, "base_defense": 5.6, "base_speed": 12.0},
    "shadow_uncommon_balanced": {"name": "Тёмный змеёныш", "element": "shadow", "rarity": "uncommon", "base_power": 12.0, "base_defense": 7.0, "base_speed": 12.0},
    "shadow_uncommon_tanky": {"name": "Тёмный ящер", "element": "shadow", "rarity": "uncommon", "base_power": 10.2, "base_defense": 9.1, "base_speed": 10.8},
    "shadow_rare_aggro": {"name": "Тёмный страж", "element": "shadow", "rarity": "rare", "base_power": 15.0, "base_defense": 5.6, "base_speed": 12.0},
    "shadow_rare_balanced": {"name": "Тёмный охотник", "element": "shadow", "rarity": "rare", "base_power": 12.0, "base_defense": 7.0, "base_speed": 12.0},
    "shadow_rare_tanky": {"name": "Тёмный хищник", "element": "shadow", "rarity": "rare", "base_power": 10.2, "base_defense": 9.1, "base_speed": 10.8},
    "shadow_epic_aggro": {"name": "Тёмный вирм", "element": "shadow", "rarity": "epic", "base_power": 15.0, "base_defense": 5.6, "base_speed": 12.0},
    "shadow_epic_balanced": {"name": "Тёмный колосс", "element": "shadow", "rarity": "epic", "base_power": 12.0, "base_defense": 7.0, "base_speed": 12.0},
    "shadow_epic_tanky": {"name": "Тёмный разрушитель", "element": "shadow", "rarity": "epic", "base_power": 10.2, "base_defense": 9.1, "base_speed": 10.8},
    "shadow_legendary_aggro": {"name": "Тёмный архонт", "element": "shadow", "rarity": "legendary", "base_power": 15.0, "base_defense": 5.6, "base_speed": 12.0},
    "shadow_legendary_balanced": {"name": "Тёмный титан", "element": "shadow", "rarity": "legendary", "base_power": 12.0, "base_defense": 7.0, "base_speed": 12.0},
    "shadow_legendary_tanky": {"name": "Тёмный владыка", "element": "shadow", "rarity": "legendary", "base_power": 10.2, "base_defense": 9.1, "base_speed": 10.8},
    "shadow_mythic_aggro": {"name": "Тёмный император", "element": "shadow", "rarity": "mythic", "base_power": 15.0, "base_defense": 5.6, "base_speed": 12.0},
    "shadow_mythic_balanced": {"name": "Тёмный повелитель", "element": "shadow", "rarity": "mythic", "base_power": 12.0, "base_defense": 7.0, "base_speed": 12.0},
    "shadow_mythic_tanky": {"name": "Тёмный первородный", "element": "shadow", "rarity": "mythic", "base_power": 10.2, "base_defense": 9.1, "base_speed": 10.8},
    "light_common_aggro": {"name": "Солнечный детёныш", "element": "light", "rarity": "common", "base_power": 11.2, "base_defense": 8.8, "base_speed": 11.0},
    "light_common_balanced": {"name": "Солнечный птенец", "element": "light", "rarity": "common", "base_power": 9.0, "base_defense": 11.0, "base_speed": 11.0},
    "light_common_tanky": {"name": "Солнечный малыш", "element": "light", "rarity": "common", "base_power": 7.6, "base_defense": 14.3, "base_speed": 9.9},
    "light_uncommon_aggro": {"name": "Солнечный дракончик", "element": "light", "rarity": "uncommon", "base_power": 11.2, "base_defense": 8.8, "base_speed": 11.0},
    "light_uncommon_balanced": {"name": "Солнечный змеёныш", "element": "light", "rarity": "uncommon", "base_power": 9.0, "base_defense": 11.0, "base_speed": 11.0},
    "light_uncommon_tanky": {"name": "Солнечный ящер", "element": "light", "rarity": "uncommon", "base_power": 7.6, "base_defense": 14.3, "base_speed": 9.9},
    "light_rare_aggro": {"name": "Солнечный страж", "element": "light", "rarity": "rare", "base_power": 11.2, "base_defense": 8.8, "base_speed": 11.0},
    "light_rare_balanced": {"name": "Солнечный охотник", "element": "light", "rarity": "rare", "base_power": 9.0, "base_defense": 11.0, "base_speed": 11.0},
    "light_rare_tanky": {"name": "Солнечный хищник", "element": "light", "rarity": "rare", "base_power": 7.6, "base_defense": 14.3, "base_speed": 9.9},
    "light_epic_aggro": {"name": "Солнечный вирм", "element": "light", "rarity": "epic", "base_power": 11.2, "base_defense": 8.8, "base_speed": 11.0},
    "light_epic_balanced": {"name": "Солнечный колосс", "element": "light", "rarity": "epic", "base_power": 9.0, "base_defense": 11.0, "base_speed": 11.0},
    "light_epic_tanky": {"name": "Солнечный разрушитель", "element": "light", "rarity": "epic", "base_power": 7.6, "base_defense": 14.3, "base_speed": 9.9},
    "light_legendary_aggro": {"name": "Солнечный архонт", "element": "light", "rarity": "legendary", "base_power": 11.2, "base_defense": 8.8, "base_speed": 11.0},
    "light_legendary_balanced": {"name": "Солнечный титан", "element": "light", "rarity": "legendary", "base_power": 9.0, "base_defense": 11.0, "base_speed": 11.0},
    "light_legendary_tanky": {"name": "Солнечный владыка", "element": "light", "rarity": "legendary", "base_power": 7.6, "base_defense": 14.3, "base_speed": 9.9},
    "light_mythic_aggro": {"name": "Солнечный император", "element": "light", "rarity": "mythic", "base_power": 11.2, "base_defense": 8.8, "base_speed": 11.0},
    "light_mythic_balanced": {"name": "Солнечный повелитель", "element": "light", "rarity": "mythic", "base_power": 9.0, "base_defense": 11.0, "base_speed": 11.0},
    "light_mythic_tanky": {"name": "Солнечный первородный", "element": "light", "rarity": "mythic", "base_power": 7.6, "base_defense": 14.3, "base_speed": 9.9},
    "wind_common_aggro": {"name": "Ветряной детёныш", "element": "wind", "rarity": "common", "base_power": 10.0, "base_defense": 5.6, "base_speed": 15.0},
    "wind_common_balanced": {"name": "Ветряной птенец", "element": "wind", "rarity": "common", "base_power": 8.0, "base_defense": 7.0, "base_speed": 15.0},
    "wind_common_tanky": {"name": "Ветряной малыш", "element": "wind", "rarity": "common", "base_power": 6.8, "base_defense": 9.1, "base_speed": 13.5},
    "wind_uncommon_aggro": {"name": "Ветряной дракончик", "element": "wind", "rarity": "uncommon", "base_power": 10.0, "base_defense": 5.6, "base_speed": 15.0},
    "wind_uncommon_balanced": {"name": "Ветряной змеёныш", "element": "wind", "rarity": "uncommon", "base_power": 8.0, "base_defense": 7.0, "base_speed": 15.0},
    "wind_uncommon_tanky": {"name": "Ветряной ящер", "element": "wind", "rarity": "uncommon", "base_power": 6.8, "base_defense": 9.1, "base_speed": 13.5},
    "wind_rare_aggro": {"name": "Ветряной страж", "element": "wind", "rarity": "rare", "base_power": 10.0, "base_defense": 5.6, "base_speed": 15.0},
    "wind_rare_balanced": {"name": "Ветряной охотник", "element": "wind", "rarity": "rare", "base_power": 8.0, "base_defense": 7.0, "base_speed": 15.0},
    "wind_rare_tanky": {"name": "Ветряной хищник", "element": "wind", "rarity": "rare", "base_power": 6.8, "base_defense": 9.1, "base_speed": 13.5},
    "wind_epic_aggro": {"name": "Ветряной вирм", "element": "wind", "rarity": "epic", "base_power": 10.0, "base_defense": 5.6, "base_speed": 15.0},
    "wind_epic_balanced": {"name": "Ветряной колосс", "element": "wind", "rarity": "epic", "base_power": 8.0, "base_defense": 7.0, "base_speed": 15.0},
    "wind_epic_tanky": {"name": "Ветряной разрушитель", "element": "wind", "rarity": "epic", "base_power": 6.8, "base_defense": 9.1, "base_speed": 13.5},
    "wind_legendary_aggro": {"name": "Ветряной архонт", "element": "wind", "rarity": "legendary", "base_power": 10.0, "base_defense": 5.6, "base_speed": 15.0},
    "wind_legendary_balanced": {"name": "Ветряной титан", "element": "wind", "rarity": "legendary", "base_power": 8.0, "base_defense": 7.0, "base_speed": 15.0},
    "wind_legendary_tanky": {"name": "Ветряной владыка", "element": "wind", "rarity": "legendary", "base_power": 6.8, "base_defense": 9.1, "base_speed": 13.5},
    "wind_mythic_aggro": {"name": "Ветряной император", "element": "wind", "rarity": "mythic", "base_power": 10.0, "base_defense": 5.6, "base_speed": 15.0},
    "wind_mythic_balanced": {"name": "Ветряной повелитель", "element": "wind", "rarity": "mythic", "base_power": 8.0, "base_defense": 7.0, "base_speed": 15.0},
    "wind_mythic_tanky": {"name": "Ветряной первородный", "element": "wind", "rarity": "mythic", "base_power": 6.8, "base_defense": 9.1, "base_speed": 13.5},
}

STARTER_SPECIES_KEY = "fire_common_balanced"  # дракон/яйцо, который выдаём в обучении

# ──────────────────────────────────────────────────────────────────────────
# БРОНЯ — даёт бонус к защите, надевается на активного дракона
# ──────────────────────────────────────────────────────────────────────────
ARMOR_CATALOG = {
    "leather_scale":  {"name": "Кожаная чешуя",      "price": 80,  "defense_bonus": 3},
    "iron_plate":     {"name": "Железная пластина",   "price": 220, "defense_bonus": 7},
    "mythic_shell":   {"name": "Мифический панцирь",  "price": 600, "defense_bonus": 15},
}

# ──────────────────────────────────────────────────────────────────────────
# ЭКОНОМИКА (черновые числа — подбираются на плейтестах)
# ──────────────────────────────────────────────────────────────────────────
FEED_MEAT_COST = 5          # мяса за одно кормление
FEED_EXP_GAIN = 15          # опыта дракону за кормление
FEED_FATIGUE_DELTA = -3     # кормление немного снимает усталость

TRAIN_COIN_COST = 20
TRAIN_MEAT_COST = 10
TRAIN_EXP_GAIN = 35
TRAIN_FATIGUE_DELTA = 18    # тренировка ощутимо утомляет

FATIGUE_SOFT_CAP = 50       # после этого порога начинают падать статы
FATIGUE_HARD_CAP = 100      # полный бан, нужен отдых
FATIGUE_DECAY_PER_HOUR = 4  # естественное восстановление в покое
FATIGUE_REST_HOURS = 6      # сколько часов отдыхает дракон после 100%

def exp_to_next_level(level: int) -> int:
    """Сколько опыта нужно дракону, чтобы перейти с level на level+1."""
    return 50 + level * 25


# ──────────────────────────────────────────────────────────────────────────
# ЕЖЕДНЕВНЫЕ ЗАДАНИЯ
# ──────────────────────────────────────────────────────────────────────────
# target — фиксированное число или диапазон (min, max), из которого рандомится.
# requires_dragon — задание не выдаётся, если у игрока нет активного дракона
# (поэтому новичок без дракона никогда не получит невыполнимое задание).
QUEST_TEMPLATES = {
    "login":     {"name": "Зайти в бота",                      "target": 1,      "reward_coins": 15, "reward_meat": 5,  "requires_dragon": False},
    "explore":   {"name": "Исследовать {t} локацию(и)",          "target": (1, 2), "reward_coins": 20, "reward_meat": 15, "requires_dragon": False},
    "feed":      {"name": "Покормить дракона {t} раз(а)",        "target": (1, 2), "reward_coins": 15, "reward_meat": 5,  "requires_dragon": True},
    "train":     {"name": "Потренировать дракона {t} раз(а)",    "target": (1, 1), "reward_coins": 25, "reward_meat": 0,  "requires_dragon": True},
    "duel_play": {"name": "Сыграть {t} дуэль(и)",                "target": (1, 1), "reward_coins": 30, "reward_meat": 10, "requires_dragon": True},
}
QUEST_EXTRA_COUNT = 2  # сколько доп. заданий (помимо login) выдаём в день, если хватает доступных

BONUS_ALL_QUESTS_COINS = 40
BONUS_ALL_QUESTS_MEAT = 20

QUEST_STREAK_BONUS_PER_DAY = 0.08   # +8% к награде за каждый день стрика выполнения ВСЕХ заданий
QUEST_STREAK_CAP_DAYS = 14


def quest_streak_multiplier(streak_days: int) -> float:
    return 1 + min(streak_days, QUEST_STREAK_CAP_DAYS) * QUEST_STREAK_BONUS_PER_DAY


# ──────────────────────────────────────────────────────────────────────────
# СЕЗОННЫЙ ТОП (ежемесячный сброс клыков + награды по местам)
# ──────────────────────────────────────────────────────────────────────────
SEASON_TOP_SNAPSHOT_SIZE = 20  # сколько мест сохраняем в истории сезона


def season_reward_for_rank(rank: int) -> tuple[int, int]:
    """Возвращает (монеты, мясо) за место в топе по итогам сезона."""
    if rank == 1:
        return 1000, 300
    if rank <= 3:
        return 600, 200
    if rank <= 10:
        return 300, 100
    if rank <= SEASON_TOP_SNAPSHOT_SIZE:
        return 120, 50
    return 0, 0
