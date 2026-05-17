"""Redis-события Агента 4 для связи контента с CRM."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Any

from shared.redis_client import _client
from shared.redis_client import push_content_event

CHANNEL_CONTENT_PUBLISHED = "content_published"


def publish_content_event(
    *,
    channel: str,
    content_type: str,
    topic: str,
    post_url: str | None = None,
    post_id: str | None = None,
    lead_id: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "event": "content_published",
        "ts": datetime.now(timezone.utc).isoformat(),
        "brand": "studio",
        "channel": channel,
        "content_type": content_type,
        "topic": topic,
        "post_url": post_url,
        "post_id": post_id,
        "lead_id": lead_id,
        "utm": {
            "source": channel,
            "medium": "post",
            "campaign": "studio_education",
        },
    }
    if extra:
        payload.update(extra)

    # Pub/Sub нужен живым слушателям, очередь нужна Агенту 5, если он запустится позже.
    _client.publish(CHANNEL_CONTENT_PUBLISHED, json.dumps(payload, ensure_ascii=False))
    push_content_event(payload)
    return payload
