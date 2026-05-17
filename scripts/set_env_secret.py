"""Safely set one secret in .env without printing its value."""

from __future__ import annotations

import argparse
from getpass import getpass
from pathlib import Path
import stat
import sys


ALLOWED_KEYS = {
    "ANTHROPIC_API_KEY",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_MANAGER_CHAT_ID",
    "TELEGRAM_API_ID",
    "TELEGRAM_API_HASH",
    "TELEGRAM_PHONE",
    "BITRIX24_WEBHOOK_URL",
    "IMAP_HOST",
    "IMAP_PORT",
    "GMAIL_USER",
    "GMAIL_APP_PASSWORD",
    "GMAIL_TENDER_FOLDER",
    "REDIS_URL",
    "DATABASE_URL",
    "APP_ENV",
    "MAX_BOT_TOKEN",
    "MAX_CHAT_ID",
    "MAX_API_BASE_URL",
    "OPENROUTER_API_KEY",
    "OPENAI_API_KEY",
    "ELEVENLABS_API_KEY",
    "ELEVENLABS_VOICE_ID",
    "REPLICATE_API_TOKEN",
    "PUBLISHER_TELEGRAM_BOT_TOKEN",
    "PUBLISHER_TELEGRAM_CHANNEL_ID",
    "POSTMYPOST_TOKEN",
    "POSTMYPOST_PROJECT_ID",
    "POSTMYPOST_INSTAGRAM_ACCOUNT_ID",
    "LLM_RUNTIME_MODE",
    "LLM_PROVIDER",
    "AGENT_CONTROL_LIVE_LLM",
    "LLM_MODEL_DEFAULT_FREE",
    "LLM_MODEL_DEMO_FREE",
    "LLM_MODEL_DEVELOPMENT",
    "LLM_MODEL_MARKETING",
    "LLM_MODEL_AGENT_CONTROL",
    "LLM_MODEL_KNOWLEDGE",
    "LLM_MODEL_ANALYSIS",
    "LLM_MODEL_REPLY",
    "LLM_MODEL_CONTENT",
    "WHISPER_PROVIDER",
    "WHISPER_MODEL",
    "IMAGE_MODEL_PROVIDER",
    "IMAGE_MODEL",
    "EMBEDDING_PROVIDER",
    "EMBEDDING_MODEL",
    "OPENROUTER_SITE_URL",
    "OPENROUTER_APP_TITLE",
}

POSITIVE_INTEGER_KEYS = {
    "TELEGRAM_API_ID",
    "IMAP_PORT",
    "POSTMYPOST_PROJECT_ID",
    "POSTMYPOST_INSTAGRAM_ACCOUNT_ID",
}

NON_ZERO_INTEGER_KEYS = {
    "TELEGRAM_MANAGER_CHAT_ID",
    "MAX_CHAT_ID",
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Set one .env secret locally without echoing it to the terminal.",
    )
    parser.add_argument("key", help="Environment variable name to set")
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to env file. Default: .env",
    )
    return parser.parse_args()


def _status(value: str | None) -> str:
    return "SET" if value and value.strip() else "EMPTY"


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


def _validate_value(key: str, value: str) -> str | None:
    if key in POSITIVE_INTEGER_KEYS:
        if not value.isdigit() or int(value) <= 0:
            return f"{key} должен быть положительным числом."
    if key in NON_ZERO_INTEGER_KEYS:
        try:
            parsed = int(value)
        except ValueError:
            return f"{key} должен быть числом."
        if parsed == 0:
            return f"{key} не должен быть 0."
    return None


def main() -> int:
    args = _parse_args()
    key = args.key.strip()
    env_path = Path(args.env_file)

    if not sys.stdin.isatty():
        print(
            "ERROR: запускать этот скрипт нужно только в обычном терминале, "
            "чтобы секрет не попал в историю чата или вывод команды.",
            file=sys.stderr,
        )
        return 2

    if key not in ALLOWED_KEYS:
        print(f"ERROR: ключ {key} не входит в разрешённый список проекта.", file=sys.stderr)
        print("Если это новый ключ, сначала добавь его в .env.example и ALLOWED_KEYS.", file=sys.stderr)
        return 2

    value = getpass(f"Введите значение для {key}. Текст не будет отображаться: ").strip()
    if not value:
        print(f"{key}=EMPTY")
        print("Значение не записано.")
        return 1

    validation_error = _validate_value(key, value)
    if validation_error:
        print(f"ERROR: {validation_error}", file=sys.stderr)
        print("Значение не записано.", file=sys.stderr)
        return 2

    _set_env_value(env_path, key, value)
    print(f"{key}={_status(value)}")
    print(f"Файл обновлён: {env_path}")
    print("Значение не выводилось.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
