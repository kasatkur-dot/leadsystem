import redis
import json
from config.settings import REDIS_URL
from shared.models import RawLead, QualifiedLead

_client = redis.from_url(REDIS_URL, decode_responses=True)

# Имена очередей
QUEUE_RAW = "leads:raw"           # Агент 2 → Агент 3
QUEUE_QUALIFIED = "leads:qualified"  # Агент 3 → Агент 5
QUEUE_OUTREACH = "leads:outreach"    # Агент 6 → Агент 5


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


def queue_sizes() -> dict:
    return {
        "raw": _client.llen(QUEUE_RAW),
        "qualified": _client.llen(QUEUE_QUALIFIED),
        "outreach": _client.llen(QUEUE_OUTREACH),
    }


def ping() -> bool:
    try:
        return _client.ping()
    except Exception:
        return False
