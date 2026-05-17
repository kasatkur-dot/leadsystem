"""
Агент 6 — sender
Telethon отправка одобренных ответов в TG-чаты.
Задержка 2–15 мин + рандом для имитации живого человека.
Отдельная Telethon-сессия data/tg_sender_session (первый запуск требует SMS-кода).
run() — блокирующий. Оркестратор запускает в daemon-потоке.
"""
import asyncio
import json
import random
from datetime import datetime
from telethon import TelegramClient
from shared.logger import get_logger
from shared.redis_client import pop_approved, track_sent
from config.settings import (
    TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE,
    OUTREACH_MIN_DELAY_SEC, OUTREACH_MAX_DELAY_SEC,
    OUTREACH_MAX_REPLIES_PER_DAY, REDIS_URL,
)

log = get_logger("sender")

SESSION_FILE = "data/tg_sender_session"  # Отдельная сессия — при первом запуске нужна авторизация (SMS)
SENT_COUNT_KEY = "outreach:sent_today"


async def _send_one(client: TelegramClient, payload: dict, redis_client) -> None:
    cand = payload["candidate"]
    reply_text = payload["reply_text"]
    chat_name = cand.get("chat_name")
    chat_id = cand.get("chat_id")
    message_id = cand.get("message_id")

    if not chat_name or not message_id:
        log.warning(f"Нет chat_name или message_id у {payload['id']} — пропуск")
        return

    delay = random.randint(OUTREACH_MIN_DELAY_SEC, OUTREACH_MAX_DELAY_SEC)
    log.info(f"Отправка {payload['id']} через {delay // 60}м {delay % 60}с в '{chat_name}'")
    await asyncio.sleep(delay)

    try:
        sent = await client.send_message(
            chat_name,
            reply_text,
            reply_to=message_id,
        )
        tracking_key = f"{chat_id or chat_name}_{sent.id}"
        tracking_data = {
            "approval_id": payload["id"],
            "our_msg_id": sent.id,
            "original_post": cand.get("raw_text", ""),
            "our_reply": reply_text,
            "contact": cand.get("contact"),
            "author_name": cand.get("author_name"),
            "flow": cand.get("flow"),
            "chat_name": chat_name,
            "chat_id": chat_id,
            "sent_at": datetime.utcnow().isoformat(),
        }
        track_sent(tracking_key, tracking_data)
        redis_client.incr(SENT_COUNT_KEY)
        redis_client.expire(SENT_COUNT_KEY, 86400)
        log.info(f"Отправлено: {payload['id']} в '{chat_name}' reply_to={message_id}")
    except Exception as e:
        log.error(f"Ошибка отправки {payload['id']}: {e}")


async def _run() -> None:
    import redis as redis_lib
    r = redis_lib.from_url(REDIS_URL, decode_responses=True)

    client = TelegramClient(SESSION_FILE, TELEGRAM_API_ID, TELEGRAM_API_HASH)
    await client.start(phone=TELEGRAM_PHONE)
    log.info("Sender Telethon подключён")

    while True:
        sent_today = int(r.get(SENT_COUNT_KEY) or 0)
        if sent_today >= OUTREACH_MAX_REPLIES_PER_DAY:
            log.info(f"Дневной лимит {OUTREACH_MAX_REPLIES_PER_DAY} достигнут — пауза 5 мин")
            await asyncio.sleep(300)
            continue

        payload = pop_approved()
        if payload:
            await _send_one(client, payload, r)
        else:
            await asyncio.sleep(30)


def run() -> None:
    """Запускает sender (блокирующий). Оркестратор вызывает в daemon-потоке."""
    if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
        log.warning("TELEGRAM_API_ID/HASH не заданы — sender не запущен")
        return
    asyncio.run(_run())
