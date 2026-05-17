"""
Агент 3 — cleaner
Дедупликация и фильтрация нецелевых лидов.
Fingerprint = hash(source + contact + первые 100 символов текста).
Нецелевые → score "off" без траты токенов Claude.
"""
import hashlib
import re

import redis

from shared.models import RawLead
from shared.logger import get_logger
from config.settings import REDIS_URL

log = get_logger("cleaner")

_redis = redis.from_url(REDIS_URL, decode_responses=True)
SEEN_KEY = "leads:seen_fingerprints"
SEEN_TTL = 60 * 60 * 24 * 30  # 30 дней

# Стоп-слова → лид нецелевой, не тратим токены Claude
_STOP_WORDS = [
    "сдам", "сниму", "аренда", "ищу съёмщика", "посуточно",
    "куплю гараж", "продам гараж", "работа", "вакансия",
    "требуется водитель", "грузчик", "уборщица",
    "спам", "реклама", "займ", "кредит", "страховк",
]


def _fingerprint(lead: RawLead) -> str:
    key = f"{lead.source}|{lead.contact or ''}|{lead.raw_text[:100]}"
    return hashlib.md5(key.encode()).hexdigest()


def _is_offtopic(text: str) -> bool:
    t = text.lower()
    return any(w in t for w in _STOP_WORDS)


def is_duplicate(lead: RawLead) -> bool:
    fp = _fingerprint(lead)
    added = _redis.set(f"{SEEN_KEY}:{fp}", "1", ex=SEEN_TTL, nx=True)
    return not added  # nx=True → False если ключ уже существовал


def is_offtopic(lead: RawLead) -> bool:
    return _is_offtopic(lead.raw_text)
