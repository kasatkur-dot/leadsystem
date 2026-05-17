"""Простые брендовые стикеры/плашки для публикаций."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
import textwrap

from agents.agent4_publisher.core.config import FONT_BOLD, OUT_STICKERS


def _slug(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9а-яА-ЯёЁ]+", "-", text).strip("-").lower()
    return cleaned[:48] or "sticker"


def generate_sticker(topic: str, output: str | None = None, dry_run: bool = False) -> Path:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception as exc:
        raise RuntimeError("Для стикеров нужен Pillow. Установи зависимости из requirements.txt.") from exc

    path = Path(output) if output else OUT_STICKERS / f"{datetime.now():%Y%m%d-%H%M%S}-{_slug(topic)}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((26, 90, 486, 422), radius=38, fill=(242, 237, 228, 255), outline=(56, 62, 68, 255), width=5)
    font = ImageFont.truetype(FONT_BOLD, 44) if FONT_BOLD else ImageFont.load_default()
    y = 155
    for line in textwrap.wrap(topic, width=13)[:4]:
        draw.text((64, y), line, fill=(56, 62, 68, 255), font=font)
        y += 58
    img.save(path)
    return path
