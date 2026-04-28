from dotenv import load_dotenv
import os

load_dotenv()

# Claude
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Telegram бот
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_MANAGER_CHAT_ID = int(os.getenv("TELEGRAM_MANAGER_CHAT_ID", "0"))

# Telegram user account (Telethon)
TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE")

# Bitrix24
BITRIX24_WEBHOOK_URL = os.getenv("BITRIX24_WEBHOOK_URL")

# Gmail
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
GMAIL_TENDER_FOLDER = os.getenv("GMAIL_TENDER_FOLDER", "тендеры")

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

# Прокси
PROXY_URL = os.getenv("PROXY_URL")

# Avito
AVITO_CLIENT_ID = os.getenv("AVITO_CLIENT_ID")
AVITO_CLIENT_SECRET = os.getenv("AVITO_CLIENT_SECRET")

# Режим
APP_ENV = os.getenv("APP_ENV", "debug")
DEBUG = APP_ENV == "debug"

# Скоринг: порог релевантности для Агента 6
RELEVANCE_THRESHOLD = 7

# Агент 6: лимиты поведения
OUTREACH_MAX_REPLIES_PER_DAY = 8
OUTREACH_MIN_DELAY_SEC = 120    # 2 мин минимум перед ответом
OUTREACH_MAX_DELAY_SEC = 900    # 15 мин максимум
OUTREACH_ACTIVE_HOURS = (8, 30, 22, 30)  # с 08:30 до 22:30

# Ключевые слова — Поток А (Перепланировки)
KEYWORDS_FLOW_A = [
    "перепланировка", "снос стены", "объединение квартир",
    "согласование перепланировки", "узаконить перепланировку",
    "самовол", "проект квартиры", "нежилое в жилое",
    "перевод помещения", "кто делает перепланировку",
    "посоветуйте перепланировка", "перепланировку под ключ",
    "проект перепланировки", "техзаключение",
]

# Ключевые слова — Поток Б (Инженерное проектирование)
KEYWORDS_FLOW_B = [
    "проект МКД", "проект здания", "торговый центр проект",
    "склад проект", "ангар проект", "производственное здание",
    "рабочая документация", "нужен проектировщик",
    "субподряд проектирование", "конструктивные решения",
    "КР КЖ КМ", "госэкспертиза", "стадия П", "рабочий проект",
    "BIM проектирование", "Revit проект", "Tekla",
    "кто делает проект", "посоветуйте проектировщика",
    "проектная документация", "конструктив",
]

ALL_KEYWORDS = KEYWORDS_FLOW_A + KEYWORDS_FLOW_B
