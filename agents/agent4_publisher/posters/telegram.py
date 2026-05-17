"""Telegram-публикация для Агента 4."""

from __future__ import annotations

import json
from pathlib import Path
import urllib.error
import urllib.request

from config import settings
from agents.agent4_publisher.core.event_bus import publish_content_event


def publish_markdown_file(path: str | Path, lead_id: str | None = None, dry_run: bool = False) -> dict:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Файл для публикации не найден: {file_path}")

    text = file_path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Файл пустой: {file_path}")

    if dry_run:
        return {
            "dry_run": True,
            "file": str(file_path),
            "chars": len(text),
            "message": "Telegram API не вызван. Это безопасная проверка маршрута.",
        }

    if not settings.PUBLISHER_TELEGRAM_BOT_TOKEN:
        raise RuntimeError("PUBLISHER_TELEGRAM_BOT_TOKEN пустой. Заполни `.env`.")
    if not settings.PUBLISHER_TELEGRAM_CHANNEL_ID:
        raise RuntimeError("PUBLISHER_TELEGRAM_CHANNEL_ID пустой. Заполни `.env`.")

    url = f"https://api.telegram.org/bot{settings.PUBLISHER_TELEGRAM_BOT_TOKEN}/sendMessage"
    request = urllib.request.Request(
        url,
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "chat_id": settings.PUBLISHER_TELEGRAM_CHANNEL_ID,
            "text": text,
            "disable_web_page_preview": False,
        }).encode("utf-8"),
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram вернул ошибку {exc.code}: {body}") from exc
    message = data.get("result", {})
    post_id = str(message.get("message_id", ""))

    event = publish_content_event(
        channel="telegram",
        content_type="post",
        topic=file_path.stem,
        post_id=post_id,
        lead_id=lead_id,
        extra={"source_file": str(file_path)},
    )
    return {"telegram": data, "event": event}
