"""Postmypost-адаптер для Instagram.

Минимальная версия умеет dry-run и проверку конфигурации. Реальная публикация
оставлена через Postmypost API после заполнения токенов.
"""

from __future__ import annotations

from pathlib import Path

from config import settings
from agents.agent4_publisher.core.event_bus import publish_content_event


def publish_file(path: str | Path, lead_id: str | None = None, dry_run: bool = False) -> dict:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Файл для Instagram не найден: {file_path}")

    if dry_run:
        return {
            "dry_run": True,
            "file": str(file_path),
            "message": "Postmypost не вызван. Это безопасная проверка маршрута.",
        }

    if not settings.POSTMYPOST_TOKEN:
        raise RuntimeError("POSTMYPOST_TOKEN пустой. Для Instagram заполни `.env`.")
    if not settings.POSTMYPOST_PROJECT_ID:
        raise RuntimeError("POSTMYPOST_PROJECT_ID пустой. Для Instagram заполни `.env`.")
    if not settings.POSTMYPOST_INSTAGRAM_ACCOUNT_ID:
        raise RuntimeError("POSTMYPOST_INSTAGRAM_ACCOUNT_ID пустой. Для Instagram заполни `.env`.")

    raise NotImplementedError(
        "Instagram API подключён как адаптер, но боевую отправку нужно включать отдельной проверкой "
        "Postmypost-аккаунта, чтобы случайно не опубликовать тестовый контент."
    )


def record_instagram_publication(post_url: str, topic: str, lead_id: str | None = None) -> dict:
    return publish_content_event(
        channel="instagram",
        content_type="post",
        topic=topic,
        post_url=post_url,
        lead_id=lead_id,
    )
