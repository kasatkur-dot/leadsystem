"""
Агент 6 — tg_monitor
Реалтайм мониторинг Telegram-чатов по ключевым словам через Telethon user account.
При матче → outreach:candidates → relevance → responder → approver → sender.
reply_handler: если ответили на наше сообщение → lead_detector → Агент 5.
"""
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import Message

from shared.redis_client import is_blocked, push_outreach_candidate, get_sent_tracking
from shared.logger import get_logger
from config.settings import (
    TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE,
    KEYWORDS_FLOW_A, KEYWORDS_FLOW_B,
    OUTREACH_ACTIVE_HOURS,
)

log = get_logger("tg_monitor")

# Чаты для мониторинга — добавлять username или invite-ссылки
TARGET_CHATS = [
    # Краснодар — недвижимость и ремонт (Поток А)
    "krasnodar_remont",
    "krasnodar_nedvizhimost",
    "krasnodar_kvartiry",
    # Строительство и проектирование (Поток Б)
    "stroitelstvo_russia",
    "proektirovanie_ru",
    "gip_club",
]

SESSION_FILE = "data/tg_monitor_session"


def _detect_flow(text: str) -> str | None:
    text_lower = text.lower()
    if any(kw in text_lower for kw in KEYWORDS_FLOW_A):
        return "A"
    if any(kw in text_lower for kw in KEYWORDS_FLOW_B):
        return "B"
    return None


def _is_active_hours() -> bool:
    from datetime import datetime
    now = datetime.now()
    h_start, m_start, h_end, m_end = OUTREACH_ACTIVE_HOURS
    start = h_start * 60 + m_start
    end = h_end * 60 + m_end
    current = now.hour * 60 + now.minute
    return start <= current <= end


async def _run_monitor():
    client = TelegramClient(SESSION_FILE, TELEGRAM_API_ID, TELEGRAM_API_HASH)
    await client.start(phone=TELEGRAM_PHONE)
    log.info("Telethon подключён, мониторинг запущен")

    @client.on(events.NewMessage(chats=TARGET_CHATS))
    async def handler(event: events.NewMessage.Event):
        msg: Message = event.message
        text = msg.message or ""
        if not text:
            return

        flow = _detect_flow(text)
        if not flow:
            return

        if not _is_active_hours():
            return

        sender = await event.get_sender()
        contact = f"@{sender.username}" if getattr(sender, "username", None) else None
        author = getattr(sender, "first_name", "") or ""

        if contact and is_blocked(contact):
            return

        chat = await event.get_chat()
        chat_id = getattr(chat, "id", None)
        chat_username = getattr(chat, "username", None)
        chat_name = getattr(chat, "title", "") or chat_username or "unknown"
        source_url = f"https://t.me/{chat_username}/{msg.id}" if chat_username else None

        # Кандидат для аутрич-цепочки (relevance → responder → approver → sender)
        candidate = {
            "id": str(msg.id),
            "source": "tg_chat",
            "flow": flow,
            "raw_text": text,
            "contact": contact,
            "author_name": author,
            "chat_name": chat_name,
            "chat_id": chat_id,
            "message_id": msg.id,
            "source_url": source_url,
        }
        push_outreach_candidate(candidate)
        log.info(f"кандидат [{flow}] в '{chat_name}' от {contact or author} | {text[:80]}")

    @client.on(events.NewMessage)
    async def reply_handler(event: events.NewMessage.Event):
        """Отслеживает ответы на наши отправленные сообщения."""
        msg: Message = event.message
        if not msg.is_reply:
            return
        chat = await event.get_chat()
        chat_id = getattr(chat, "id", None)
        if not chat_id:
            return
        tracking_key = f"{chat_id}_{msg.reply_to_msg_id}"
        tracking = get_sent_tracking(tracking_key)
        if not tracking:
            return  # Не наше сообщение

        # Передаём в lead_detector
        from agents.agent6_outreach.lead_detector import handle_reply
        sender_user = await event.get_sender()
        contact = f"@{sender_user.username}" if getattr(sender_user, "username", None) else None
        handle_reply(
            tracking=tracking,
            reply_text=msg.message or "",
            contact=contact or tracking.get("contact"),
        )

    await client.run_until_disconnected()


def run():
    """Запускает мониторинг (блокирующий вызов). Оркестратор вызывает в отдельном потоке."""
    if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
        log.warning("TELEGRAM_API_ID/HASH не заданы — пропуск")
        return
    asyncio.run(_run_monitor())
