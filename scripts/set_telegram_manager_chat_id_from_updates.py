"""Set TELEGRAM_MANAGER_CHAT_ID from the latest Telegram bot update.

Before running this script, send any message to the notification bot from the
Telegram account or chat that should receive manager notifications.

The script does not print the chat id value. It only writes it to `.env`.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
import stat
import sys

import telegram
from telegram.error import TelegramError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import TELEGRAM_BOT_TOKEN


ENV_PATH = PROJECT_ROOT / ".env"


def _set_env_value(path: Path, key: str, value: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    output: list[str] = []
    found = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#") or "=" not in line:
            output.append(line)
            continue
        current_key = line.split("=", 1)[0].strip()
        if current_key == key:
            output.append(f"{key}={value}")
            found = True
        else:
            output.append(line)

    if not found:
        if output and output[-1].strip():
            output.append("")
        output.append(f"{key}={value}")

    path.write_text("\n".join(output).rstrip() + "\n", encoding="utf-8")
    try:
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass


async def _run() -> int:
    if not TELEGRAM_BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN=EMPTY")
        return 1

    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    try:
        updates = await bot.get_updates(limit=20, timeout=10)
    except TelegramError:
        print("TELEGRAM_MANAGER_CHAT_ID=NETWORK_ERROR")
        print("Не удалось обратиться к Telegram API из этой среды. Запусти скрипт в обычном терминале.")
        return 2
    for update in reversed(updates):
        chat = update.effective_chat
        if chat and chat.id:
            _set_env_value(ENV_PATH, "TELEGRAM_MANAGER_CHAT_ID", str(chat.id))
            print("TELEGRAM_MANAGER_CHAT_ID=SET")
            print("Значение записано в .env и не выводилось.")
            return 0

    print("TELEGRAM_MANAGER_CHAT_ID=MISSING")
    print("Сначала отправь любое сообщение боту, потом запусти скрипт ещё раз.")
    return 1


def main() -> int:
    return asyncio.run(_run())


if __name__ == "__main__":
    raise SystemExit(main())
