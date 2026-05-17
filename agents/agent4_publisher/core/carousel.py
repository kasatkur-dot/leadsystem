"""Локальная генерация каруселей 1080x1350 для студии."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
import textwrap

from agents.agent4_publisher.core.config import FONT_BOLD, FONT_REG, OUT_CAROUSEL

W, H = 1080, 1350
BG = (242, 237, 228)
INK = (45, 51, 56)
ACCENT = (145, 114, 78)


def _slug(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9а-яА-ЯёЁ]+", "-", text).strip("-").lower()
    return cleaned[:48] or "carousel"


def _chunks(topic: str) -> list[tuple[str, str]]:
    return [
        ("Проблема", f"{topic}. Обычно ошибка начинается не на стройке, а на этапе решения без проекта."),
        ("Что проверить", "Несущие стены, мокрые зоны, вентиляцию, статус помещения и требования управляющей компании."),
        ("Почему важно", "Проект защищает от переделок, штрафов, отказа банка и проблем при продаже объекта."),
        ("Как работаем", "Сначала собираем исходные данные, потом делаем понятное ТЗ, затем проект и сопровождение."),
        ("Следующий шаг", "Если есть сомнения по объекту, лучше задать вопрос до ремонта, а не после демонтажа."),
    ]


def generate_carousel(topic: str, output: str | None = None, dry_run: bool = False) -> Path:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception as exc:
        raise RuntimeError("Для каруселей нужен Pillow. Установи зависимости из requirements.txt.") from exc

    base_dir = Path(output) if output else OUT_CAROUSEL / f"{datetime.now():%Y%m%d-%H%M%S}-{_slug(topic)}"
    base_dir.mkdir(parents=True, exist_ok=True)

    font_title = ImageFont.truetype(FONT_BOLD, 64) if FONT_BOLD else ImageFont.load_default()
    font_body = ImageFont.truetype(FONT_REG, 42) if FONT_REG else ImageFont.load_default()
    font_mark = ImageFont.truetype(FONT_BOLD, 28) if FONT_BOLD else ImageFont.load_default()

    for idx, (title, body) in enumerate(_chunks(topic), 1):
        img = Image.new("RGB", (W, H), BG)
        draw = ImageDraw.Draw(img)
        draw.rectangle((70, 70, W - 70, H - 70), outline=INK, width=4)
        draw.rectangle((70, 70, W - 70, 170), fill=INK)
        draw.text((105, 100), f"ВПП / {idx:02d}", fill=BG, font=font_mark)
        draw.text((105, 260), title, fill=ACCENT, font=font_title)
        y = 390
        for line in textwrap.wrap(body, width=29):
            draw.text((105, y), line, fill=INK, font=font_body)
            y += 62
        draw.text((105, H - 160), "Студия проектирования. Без форм и навязчивых продаж.", fill=INK, font=font_mark)
        img.save(base_dir / f"{idx:02d}_slide.png")

    caption = (
        f"{topic}\n\n"
        "Сохрани, если планируешь проект, перепланировку или реконструкцию. "
        "Если вопрос уже горит — напиши в личные сообщения, разберём по исходным данным."
    )
    (base_dir / "caption.txt").write_text(caption, encoding="utf-8")
    return base_dir
