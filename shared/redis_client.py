from __future__ import annotations

import redis
import json
from config.settings import REDIS_URL
from shared.models import RawLead, QualifiedLead

_client = redis.from_url(REDIS_URL, decode_responses=True)

# Имена очередей
QUEUE_RAW = "leads:raw"           # Агент 2 → Агент 3
QUEUE_QUALIFIED = "leads:qualified"  # Агент 3 → Агент 5
QUEUE_OUTREACH = "leads:outreach"    # Агент 6 → Агент 5
QUEUE_CONTENT_EVENTS = "content:published"  # Агент 4 → Агент 5


def push_raw(lead: RawLead) -> None:
    _client.rpush(QUEUE_RAW, lead.model_dump_json())


def pop_raw() -> RawLead | None:
    data = _client.lpop(QUEUE_RAW)
    return RawLead.model_validate_json(data) if data else None


def push_qualified(lead: QualifiedLead) -> None:
    _client.rpush(QUEUE_QUALIFIED, lead.model_dump_json())


def pop_qualified() -> QualifiedLead | None:
    data = _client.lpop(QUEUE_QUALIFIED)
    return QualifiedLead.model_validate_json(data) if data else None


def push_outreach(data: dict) -> None:
    _client.rpush(QUEUE_OUTREACH, json.dumps(data, ensure_ascii=False))


def pop_outreach() -> dict | None:
    data = _client.lpop(QUEUE_OUTREACH)
    return json.loads(data) if data else None


def push_content_event(event: dict) -> None:
    _client.rpush(QUEUE_CONTENT_EVENTS, json.dumps(event, ensure_ascii=False))


def pop_content_event() -> dict | None:
    data = _client.lpop(QUEUE_CONTENT_EVENTS)
    return json.loads(data) if data else None


def queue_sizes() -> dict:
    return {
        "raw": _client.llen(QUEUE_RAW),
        "qualified": _client.llen(QUEUE_QUALIFIED),
        "outreach": _client.llen(QUEUE_OUTREACH),
        "content_events": _client.llen(QUEUE_CONTENT_EVENTS),
    }


def ping() -> bool:
    try:
        return _client.ping()
    except Exception:
        return False


# --- Blocklist: конкуренты, боты, спамеры ---
BLOCKLIST_KEY = "leads:blocklist"


def add_to_blocklist(identifier: str) -> None:
    """Добавить username/email/phone в blocklist."""
    _client.sadd(BLOCKLIST_KEY, identifier.lower())


def is_blocked(identifier: str) -> bool:
    """Проверить находится ли контакт в blocklist."""
    return bool(_client.sismember(BLOCKLIST_KEY, identifier.lower()))


def blocklist_size() -> int:
    return _client.scard(BLOCKLIST_KEY)


# --- Outreach pipeline queues ---
QUEUE_OUTREACH_CANDIDATES = "outreach:candidates"   # tg_monitor → relevance
QUEUE_FOR_APPROVAL = "outreach:for_approval"        # relevance → approver bot
QUEUE_APPROVED = "outreach:approved"                # approver → sender
HASH_SENT = "outreach:sent"                         # sender → lead_detector tracking


def push_outreach_candidate(candidate: dict) -> None:
    _client.rpush(QUEUE_OUTREACH_CANDIDATES, json.dumps(candidate, ensure_ascii=False))


def pop_outreach_candidate() -> dict | None:
    data = _client.lpop(QUEUE_OUTREACH_CANDIDATES)
    return json.loads(data) if data else None


def push_for_approval(payload: dict) -> None:
    _client.rpush(QUEUE_FOR_APPROVAL, json.dumps(payload, ensure_ascii=False))


def pop_for_approval() -> dict | None:
    data = _client.lpop(QUEUE_FOR_APPROVAL)
    return json.loads(data) if data else None


def push_approved(payload: dict) -> None:
    _client.rpush(QUEUE_APPROVED, json.dumps(payload, ensure_ascii=False))


def pop_approved() -> dict | None:
    data = _client.lpop(QUEUE_APPROVED)
    return json.loads(data) if data else None


def set_approval(approval_id: str, payload: dict, ttl: int = 1800) -> None:
    """Сохраняет состояние запроса одобрения с TTL (по умолчанию 30 мин)."""
    _client.setex(f"outreach:approval:{approval_id}", ttl, json.dumps(payload, ensure_ascii=False))


def get_approval(approval_id: str) -> dict | None:
    raw = _client.get(f"outreach:approval:{approval_id}")
    return json.loads(raw) if raw else None


def delete_approval(approval_id: str) -> None:
    _client.delete(f"outreach:approval:{approval_id}")


def track_sent(tracking_key: str, data: dict) -> None:
    _client.hset(HASH_SENT, tracking_key, json.dumps(data, ensure_ascii=False))


def get_sent_tracking(tracking_key: str) -> dict | None:
    raw = _client.hget(HASH_SENT, tracking_key)
    return json.loads(raw) if raw else None


def outreach_candidate_size() -> int:
    return _client.llen(QUEUE_OUTREACH_CANDIDATES)


# --- Bot state (approver диалог редактирования) ---
_BOT_STATE_PREFIX = "outreach:bot_state:"


def set_bot_state(chat_id: int, state: dict, ttl: int = 600) -> None:
    _client.setex(f"{_BOT_STATE_PREFIX}{chat_id}", ttl, json.dumps(state, ensure_ascii=False))


def get_bot_state(chat_id: int) -> dict | None:
    raw = _client.get(f"{_BOT_STATE_PREFIX}{chat_id}")
    return json.loads(raw) if raw else None


def delete_bot_state(chat_id: int) -> None:
    _client.delete(f"{_BOT_STATE_PREFIX}{chat_id}")
