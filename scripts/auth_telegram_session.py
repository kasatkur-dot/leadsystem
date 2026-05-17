"""Authorize a Telethon user session for monitor or sender."""

import argparse
import asyncio
from pathlib import Path
import sys
from typing import Optional

from telethon import TelegramClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import TELEGRAM_API_HASH, TELEGRAM_API_ID, TELEGRAM_PHONE


SESSIONS = {
    "monitor": "data/tg_monitor_session",
    "sender": "data/tg_sender_session",
}


def _status(value, *, positive_number: bool = False) -> str:
    if positive_number:
        return "SET" if value and int(value) > 0 else "INVALID_OR_EMPTY"
    return "SET" if value else "EMPTY"


def _normalize_phone(value: Optional[str]) -> str:
    if not value:
        return ""
    stripped = value.strip()
    digits = "".join(ch for ch in stripped if ch.isdigit())
    if stripped.startswith("+"):
        return f"+{digits}"
    return digits


def _phone_status(value: Optional[str]) -> str:
    phone = _normalize_phone(value)
    digits = "".join(ch for ch in phone if ch.isdigit())
    if not phone:
        return "EMPTY"
    if not phone.startswith("+"):
        return "INVALID_NO_PLUS"
    if len(digits) < 10:
        return "INVALID_TOO_SHORT"
    if len(digits) > 15:
        return "INVALID_TOO_LONG"
    return "SET"


async def auth(session_name: str) -> None:
    phone = _normalize_phone(TELEGRAM_PHONE)
    phone_status = _phone_status(TELEGRAM_PHONE)

    if not TELEGRAM_API_ID or not TELEGRAM_API_HASH or phone_status != "SET":
        raise SystemExit(
            "Нужны TELEGRAM_API_ID, TELEGRAM_API_HASH и TELEGRAM_PHONE в .env\n"
            f"Статусы: TELEGRAM_API_ID={_status(TELEGRAM_API_ID, positive_number=True)}, "
            f"TELEGRAM_API_HASH={_status(TELEGRAM_API_HASH)}, "
            f"TELEGRAM_PHONE={phone_status}"
        )

    session_file = SESSIONS[session_name]
    Path(session_file).parent.mkdir(parents=True, exist_ok=True)

    client = TelegramClient(session_file, TELEGRAM_API_ID, TELEGRAM_API_HASH)
    try:
        await client.start(phone=phone)
        me = await client.get_me()
        username = f"@{me.username}" if me and me.username else "без username"
        print(f"{session_name} авторизован: {username}")
    finally:
        await client.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Authorize Telethon session")
    parser.add_argument(
        "session",
        choices=sorted(SESSIONS),
        help="Which session to authorize",
    )
    args = parser.parse_args()
    asyncio.run(auth(args.session))


if __name__ == "__main__":
    main()
