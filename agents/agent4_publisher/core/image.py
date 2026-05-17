"""Генерация архитектурных изображений для студии.

Это чистая студийная версия: без Jarvis, киберпанка и курса.
"""

from __future__ import annotations

import base64
from datetime import datetime
import json
from pathlib import Path
import re
import urllib.error
import urllib.request

from config import settings
from agents.agent4_publisher.core.config import OUT_POSTS

OPENAI_IMAGES_URL = "https://api.openai.com/v1/images/generations"


def _slug(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9а-яА-ЯёЁ]+", "-", text).strip("-").lower()
    return cleaned[:60] or "image"


def build_image_prompt(topic: str) -> str:
    return (
        "Architectural studio visual, clean premium Russian design bureau style. "
        "Topic: "
        f"{topic}. "
        "Show realistic architecture, floor plans, structural details, renovation documents, "
        "warm natural light, beige graphite accents, trustworthy professional mood. "
        "No cyberpunk, no neon, no Jarvis, no robots, no course branding, no text overlays."
    )


def _dry_placeholder(path: Path, topic: str) -> Path:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        path = path.with_suffix(".txt")
        path.write_text(f"DRY-RUN IMAGE PLACEHOLDER\n{topic}\n", encoding="utf-8")
        return path

    img = Image.new("RGB", (1080, 1080), (238, 232, 220))
    draw = ImageDraw.Draw(img)
    try:
        font_big = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 52)
        font_small = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 32)
    except Exception:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()
    draw.rectangle((80, 80, 1000, 1000), outline=(64, 71, 78), width=6)
    draw.line((160, 720, 920, 720), fill=(64, 71, 78), width=4)
    draw.rectangle((220, 300, 860, 720), outline=(136, 111, 82), width=5)
    draw.text((140, 130), "ВПП / визуал поста", fill=(64, 71, 78), font=font_big)
    draw.text((140, 800), topic[:95], fill=(64, 71, 78), font=font_small)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    return path


def generate_image(topic: str, output: str | None = None, dry_run: bool = False) -> Path:
    if output:
        path = Path(output)
    else:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = OUT_POSTS / f"{stamp}-{_slug(topic)}.png"

    if dry_run:
        return _dry_placeholder(path, topic)

    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY пустой. Для реальной генерации изображения заполни `.env`.")

    request = urllib.request.Request(
        OPENAI_IMAGES_URL,
        headers={
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": "dall-e-3",
            "prompt": build_image_prompt(topic),
            "size": "1024x1024",
            "quality": "standard",
            "n": 1,
            "response_format": "b64_json",
        }).encode("utf-8"),
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI Images вернул ошибку {exc.code}: {body}") from exc

    b64_data = data["data"][0]["b64_json"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(base64.b64decode(b64_data))
    return path
