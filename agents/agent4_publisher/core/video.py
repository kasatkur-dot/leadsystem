"""Видео-запросы через Replicate.

Реальная генерация требует `REPLICATE_API_TOKEN` и установленный пакет `replicate`.
Dry-run сохраняет JSON-задание без обращения к API.
"""

from __future__ import annotations

from datetime import datetime
import json
import os
from pathlib import Path
import re

from config import settings
from agents.agent4_publisher.core.config import OUT_VIDEO

DEFAULT_MODEL = "luma/ray"


def _slug(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9а-яА-ЯёЁ]+", "-", text).strip("-").lower()
    return cleaned[:48] or "video"


def generate_video(prompt: str, output: str | None = None, dry_run: bool = False) -> Path:
    path = Path(output) if output else OUT_VIDEO / f"{datetime.now():%Y%m%d-%H%M%S}-{_slug(prompt)}.json"
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "model": DEFAULT_MODEL,
        "prompt": (
            "Architectural project studio video, calm premium visuals, drawings, plans, "
            f"construction documentation, topic: {prompt}"
        ),
    }
    if dry_run:
        path.write_text(json.dumps({"dry_run": True, **payload}, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    if not settings.REPLICATE_API_TOKEN:
        raise RuntimeError("REPLICATE_API_TOKEN пустой. Для видео заполни `.env`.")

    try:
        import replicate
    except Exception as exc:
        raise RuntimeError("Для видео нужен пакет replicate из requirements.txt.") from exc

    os.environ["REPLICATE_API_TOKEN"] = settings.REPLICATE_API_TOKEN
    result = replicate.run(DEFAULT_MODEL, input={"prompt": payload["prompt"]})
    path.write_text(json.dumps({"dry_run": False, "result": result}, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
