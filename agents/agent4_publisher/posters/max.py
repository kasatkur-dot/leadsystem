"""MAX-публикация через официальный Bot API."""

from __future__ import annotations

import json
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

from config import settings
from agents.agent4_publisher.core.event_bus import publish_content_event

MAX_TEXT_LIMIT = 4000


def publish_file(path: str | Path, lead_id: str | None = None, dry_run: bool = False) -> dict:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Файл для MAX не найден: {file_path}")

    text = file_path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Файл пустой: {file_path}")
    if len(text) > MAX_TEXT_LIMIT:
        raise ValueError(
            f"MAX принимает текст до {MAX_TEXT_LIMIT} символов, сейчас {len(text)}. "
            "Сократи пост или раздели его на несколько публикаций."
        )

    if dry_run:
        return {
            "dry_run": True,
            "channel": "max",
            "file": str(file_path),
            "chars": len(text),
            "message": "MAX API не вызван. Это безопасная проверка маршрута.",
        }

    if not settings.MAX_BOT_TOKEN:
        raise RuntimeError("MAX_BOT_TOKEN пустой. Заполни `.env` после создания MAX-бота.")
    if not settings.MAX_CHAT_ID:
        raise RuntimeError("MAX_CHAT_ID пустой. Укажи ID чата/канала MAX, куда бот может публиковать.")

    query = urllib.parse.urlencode({"chat_id": settings.MAX_CHAT_ID})
    request = urllib.request.Request(
        f"{settings.MAX_API_BASE_URL}/messages?{query}",
        headers={
            "Authorization": settings.MAX_BOT_TOKEN,
            "Content-Type": "application/json",
        },
        data=json.dumps(
            {
                "text": text,
                "format": "markdown",
                "notify": True,
            },
            ensure_ascii=False,
        ).encode("utf-8"),
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"MAX вернул ошибку {exc.code}: {body}") from exc

    message = data.get("message") or {}
    post_id = str(message.get("mid") or message.get("id") or "")
    post_url = message.get("url")

    try:
        event = publish_content_event(
            channel="max",
            content_type="post",
            topic=file_path.stem,
            post_url=post_url,
            post_id=post_id,
            lead_id=lead_id,
            extra={"source_file": str(file_path)},
        )
        event_error = None
    except Exception as exc:  # Публикация уже случилась, не провоцируем повторный пост из-за Redis.
        event = None
        event_error = f"MAX опубликован, но событие content_published не записано: {exc}"

    return {"max": data, "event": event, "event_error": event_error}
