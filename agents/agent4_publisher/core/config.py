"""Пути и шрифты для контент-движка Агента 4.

API-ключи и токены каналов держим централизованно в `config.settings`,
этот файл — только про файловую систему, чтобы posters/ и core/ не знали
о структуре репозитория и не плодили `os.getenv`.
"""

from __future__ import annotations

from pathlib import Path

# agents/agent4_publisher/
AGENT_ROOT = Path(__file__).resolve().parent.parent
# Корень проекта design-studio-lead-engine/
PROJECT_ROOT = AGENT_ROOT.parent.parent

# Контент студии — каноничное место (общая «знаниевая база» бренда)
STUDIO_BRAND_DIR = PROJECT_ROOT / "content" / "studio_brand"
SYSTEM_PROMPT_FILE = STUDIO_BRAND_DIR / "system_prompt.md"
AUDIENCE_FEARS_FILE = STUDIO_BRAND_DIR / "audience_fears.md"
CUSTOMER_PROFILES_FILE = STUDIO_BRAND_DIR / "customer_profiles.md"
STYLE_NOTES_FILE = PROJECT_ROOT / "docs" / "blogger-style-notes-for-vpp-posts.md"
CONTENT_PATTERNS_FILE = STUDIO_BRAND_DIR / "content_patterns.md"

# Локальные ассеты Агента 4
ASSETS_DIR = AGENT_ROOT / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
PHOTOS_DIR = ASSETS_DIR / "photos"

# Выходные папки (создаются автоматически)
OUTPUT_DIR = AGENT_ROOT / "output"
OUT_POSTS = OUTPUT_DIR / "posts"
OUT_CAROUSEL = OUTPUT_DIR / "carousel"
OUT_STORIES = OUTPUT_DIR / "stories"
OUT_VOICE = OUTPUT_DIR / "voice"
OUT_VIDEO = OUTPUT_DIR / "video"
OUT_STICKERS = OUTPUT_DIR / "stickers"

for _d in (PHOTOS_DIR, OUT_POSTS, OUT_CAROUSEL, OUT_STORIES, OUT_VOICE, OUT_VIDEO, OUT_STICKERS):
    _d.mkdir(parents=True, exist_ok=True)


def _find_font(*candidates: str | Path) -> str:
    """Возвращает первый существующий путь, иначе пустую строку (PIL подставит дефолт)."""
    for p in candidates:
        if Path(p).exists():
            return str(p)
    return ""


# Шрифты: сначала локальные (если положили в assets/fonts/), иначе системные
FONT_BOLD = _find_font(
    FONTS_DIR / "Inter-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",
)
FONT_REG = _find_font(
    FONTS_DIR / "Inter-Regular.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
)
FONT_IMPACT = _find_font(
    "/System/Library/Fonts/Supplemental/Impact.ttf",
    "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf",
)
