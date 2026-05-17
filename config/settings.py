from dotenv import load_dotenv
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# Server environment variables must win over a local .env during deploy.
load_dotenv(PROJECT_ROOT / ".env", override=False)


def _env_int(name: str, default: int = 0) -> int:
    value = os.getenv(name)
    return int(value) if value else default


# LLM router
# Four supported modes:
# - local_codex: current development via Codex/subscription, product backend dry-run;
# - openrouter_free_test: local test mode, product backend calls one free OpenRouter model;
# - demo_server_free: temporary server demo for review, all text LLM routes use one free OpenRouter model;
# - production_server_router: final server mode with task-specific OpenRouter model routes.
LLM_RUNTIME_MODE = os.getenv("LLM_RUNTIME_MODE", "local_codex").strip().lower()
_RAW_LLM_PROVIDER = os.getenv("LLM_PROVIDER", "dry_run").strip().lower()
LLM_MODEL_DEFAULT_FREE = os.getenv(
    "LLM_MODEL_DEFAULT_FREE",
    os.getenv("OPENROUTER_MODEL_DEFAULT_FREE", "deepseek/deepseek-v4-flash:free"),
)
LLM_MODEL_DEMO_FREE = os.getenv("LLM_MODEL_DEMO_FREE", LLM_MODEL_DEFAULT_FREE)

if LLM_RUNTIME_MODE == "local_codex":
    LLM_PROVIDER = "dry_run"
elif LLM_RUNTIME_MODE in {"openrouter_free_test", "demo_server_free", "production_server_router"}:
    LLM_PROVIDER = "openrouter"
else:
    LLM_PROVIDER = _RAW_LLM_PROVIDER

if LLM_RUNTIME_MODE in {"openrouter_free_test", "demo_server_free"}:
    LLM_MODEL_DEVELOPMENT = LLM_MODEL_DEMO_FREE
    LLM_MODEL_MARKETING = LLM_MODEL_DEMO_FREE
    LLM_MODEL_AGENT_CONTROL = LLM_MODEL_DEMO_FREE
    LLM_MODEL_KNOWLEDGE = LLM_MODEL_DEMO_FREE
    LLM_MODEL_ANALYSIS = LLM_MODEL_DEMO_FREE
    LLM_MODEL_REPLY = LLM_MODEL_DEMO_FREE
    LLM_MODEL_CONTENT = LLM_MODEL_DEMO_FREE
else:
    LLM_MODEL_DEVELOPMENT = os.getenv(
        "LLM_MODEL_DEVELOPMENT",
        os.getenv("OPENROUTER_MODEL_DEVELOPMENT", "anthropic/claude-opus-4.7"),
    )
    LLM_MODEL_MARKETING = os.getenv(
        "LLM_MODEL_MARKETING",
        os.getenv("OPENROUTER_MODEL_MARKETING", "google/gemini-2.5-flash"),
    )
    LLM_MODEL_AGENT_CONTROL = os.getenv(
        "LLM_MODEL_AGENT_CONTROL",
        os.getenv("OPENROUTER_MODEL_AGENT_CONTROL", "minimax/minimax-2.7"),
    )
    LLM_MODEL_KNOWLEDGE = os.getenv(
        "LLM_MODEL_KNOWLEDGE",
        os.getenv("OPENROUTER_MODEL_KNOWLEDGE", LLM_MODEL_DEFAULT_FREE),
    )
    LLM_MODEL_ANALYSIS = os.getenv("LLM_MODEL_ANALYSIS", LLM_MODEL_DEFAULT_FREE)
    LLM_MODEL_REPLY = os.getenv("LLM_MODEL_REPLY", LLM_MODEL_AGENT_CONTROL)
    LLM_MODEL_CONTENT = os.getenv("LLM_MODEL_CONTENT", LLM_MODEL_MARKETING)

_LIVE_DEFAULT = "1" if LLM_RUNTIME_MODE in {"openrouter_free_test", "demo_server_free", "production_server_router"} else "0"
AGENT_CONTROL_LIVE_LLM = os.getenv("AGENT_CONTROL_LIVE_LLM", _LIVE_DEFAULT) == "1"

# Voice / image / knowledge-search model routes. These are configured as
# routes now; actual external calls stay disabled unless a specific module is
# enabled later.
WHISPER_PROVIDER = os.getenv("WHISPER_PROVIDER", "local").strip().lower()
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-1")
IMAGE_MODEL_PROVIDER = os.getenv("IMAGE_MODEL_PROVIDER", "openrouter").strip().lower()
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "google/gemini-2.5-flash-image-preview")
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "gemini").strip().lower()
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")

# Claude / Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Telegram бот
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_MANAGER_CHAT_ID = _env_int("TELEGRAM_MANAGER_CHAT_ID")

# Telegram user account (Telethon)
TELEGRAM_API_ID = _env_int("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE")

# Bitrix24
BITRIX24_WEBHOOK_URL = os.getenv("BITRIX24_WEBHOOK_URL")
# Отдельный webhook с imopenlines-правами для отправки MAX/Telegram-сообщений
BITRIX24_IMOPENLINES_WEBHOOK_URL = os.getenv("BITRIX24_IMOPENLINES_WEBHOOK_URL")

# Email / IMAP source for tender letters.
# Historical GMAIL_* names are kept for compatibility with existing agents,
# but the mailbox can be Gmail, Yandex Mail, or another IMAP provider.
IMAP_HOST = os.getenv("IMAP_HOST", "imap.gmail.com")
IMAP_PORT = _env_int("IMAP_PORT", 993)
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

# === Agent 4 Publisher (контент-движок) ===
# Текстовая LLM через OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "")
OPENROUTER_APP_TITLE = os.getenv("OPENROUTER_APP_TITLE", "VPP Lead Engine")
# DALL-E 3 для иллюстраций
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
# Голос
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "")
# Видео и Luma Ray
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
# Telegram-канал паблишера (отдельный от уведомительного TELEGRAM_BOT_TOKEN)
PUBLISHER_TELEGRAM_BOT_TOKEN = os.getenv("PUBLISHER_TELEGRAM_BOT_TOKEN", "")
PUBLISHER_TELEGRAM_CHANNEL_ID = os.getenv("PUBLISHER_TELEGRAM_CHANNEL_ID", "")
# Instagram через Postmypost
POSTMYPOST_TOKEN = os.getenv("POSTMYPOST_TOKEN", "")
POSTMYPOST_PROJECT_ID = _env_int("POSTMYPOST_PROJECT_ID")
POSTMYPOST_INSTAGRAM_ACCOUNT_ID = _env_int("POSTMYPOST_INSTAGRAM_ACCOUNT_ID")

# MAX Bot API — публикация в MAX-канал/чат
MAX_BOT_TOKEN = os.getenv("MAX_BOT_TOKEN", "")
MAX_CHAT_ID = _env_int("MAX_CHAT_ID")
MAX_API_BASE_URL = os.getenv("MAX_API_BASE_URL", "https://platform-api.max.ru").rstrip("/")
