"""
Агент 2 — tender_collector
Читает IMAP-папку с тендерными письмами → RawLead → Redis.
Запускается по расписанию каждые 15 минут.
Использует: imap-tools (500+ stars, MIT).
"""
from imap_tools import MailBox, AND
from bs4 import BeautifulSoup

from shared.models import RawLead
from shared.redis_client import push_raw
from shared.logger import get_logger
from config.settings import (
    GMAIL_APP_PASSWORD,
    GMAIL_TENDER_FOLDER,
    GMAIL_USER,
    IMAP_HOST,
    IMAP_PORT,
)

log = get_logger("tender_collector")

FETCH_LIMIT = 50  # за один проход не больше 50 писем


def _extract_body(msg) -> str:
    if msg.text:
        return msg.text.strip()
    if msg.html:
        return BeautifulSoup(msg.html, "lxml").get_text(separator="\n").strip()
    return ""


def run() -> int:
    """Забирает непрочитанные тендерные письма. Возвращает количество новых лидов."""
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        log.warning("почтовый логин или пароль приложения не заданы — пропуск")
        return 0

    count = 0
    try:
        with MailBox(IMAP_HOST, port=IMAP_PORT).login(
            GMAIL_USER, GMAIL_APP_PASSWORD, initial_folder=GMAIL_TENDER_FOLDER
        ) as mailbox:
            for msg in mailbox.fetch(AND(seen=False), limit=FETCH_LIMIT, mark_seen=True):
                body = _extract_body(msg)
                if not body:
                    continue

                sender_name = msg.from_values.name if msg.from_values else ""
                sender_email = msg.from_ or ""

                lead = RawLead(
                    source="tender_email",
                    source_type="tender",
                    traffic_channel="tender",
                    first_touch_channel="email",
                    last_touch_channel="email",
                    utm_source="email",
                    utm_medium="email",
                    consent_status="not_required",
                    flow="B",  # тендеры всегда Поток Б — инженерное проектирование
                    raw_text=f"Тема: {msg.subject}\nОт: {sender_email}\n\n{body}",
                    contact=sender_email,
                    author_name=sender_name or sender_email,
                )
                push_raw(lead)
                count += 1
                log.info(f"новый лид {lead.id[:8]} | {sender_email} | {msg.subject[:60]}")

    except Exception as e:
        log.error(f"ошибка IMAP: {e}")

    if count:
        log.info(f"итого новых тендеров: {count}")
    return count
