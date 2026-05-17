"""Локальная генерация сторис 1080x1920 для студии."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
import textwrap

from agents.agent4_publisher.core.config import FONT_BOLD, FONT_REG, OUT_STORIES

W, H = 1080, 1920
BG = (37, 43, 48)
PAPER = (239, 232, 219)
GOLD = (194, 153, 95)


def _slug(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9а-яА-ЯёЁ]+", "-", text).strip("-").lower()
    return cleaned[:48] or "stories"


def generate_stories(topic: str, output: str | None = None, dry_run: bool = False) -> Path:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception as exc:
        raise RuntimeError("Для сторис нужен Pillow. Установи зависимости из requirements.txt.") from exc

    base_dir = Path(output) if output else OUT_STORIES / f"{datetime.now():%Y%m%d-%H%M%S}-{_slug(topic)}"
    base_dir.mkdir(parents=True, exist_ok=True)

    font_big = ImageFont.truetype(FONT_BOLD, 78) if FONT_BOLD else ImageFont.load_default()
    font_mid = ImageFont.truetype(FONT_REG, 48) if FONT_REG else ImageFont.load_default()
    font_small = ImageFont.truetype(FONT_REG, 34) if FONT_REG else ImageFont.load_default()

    cards = [
        ("До проекта", f"{topic}: что важно понять до первого платежа подрядчику."),
        ("Главный риск", "Самые дорогие ошибки обычно не видно на красивой картинке. Их видно в конструктиве и документах."),
        ("Что делать", "Собрать исходные данные, проверить ограничения и только потом принимать планировочное решение."),
        ("Мягкий вход", "Можно просто написать вопрос в личные сообщения. Без анкет, форм и обязательных полей."),
    ]

    for idx, (title, body) in enumerate(cards, 1):
        img = Image.new("RGB", (W, H), BG)
        draw = ImageDraw.Draw(img)
        draw.rectangle((85, 130, W - 85, H - 130), outline=GOLD, width=5)
        draw.text((120, 210), title, fill=GOLD, font=font_big)
        y = 470
        for line in textwrap.wrap(body, width=28):
            draw.text((120, y), line, fill=PAPER, font=font_mid)
            y += 72
        draw.text((120, H - 250), "ВПП / студия проектирования", fill=PAPER, font=font_small)
        img.save(base_dir / f"{idx:02d}_story.png")

    return base_dir
