"""Configure .env to use OpenRouter as the LLM provider.

This script writes only non-secret LLM provider/model settings. It does not set
or print OPENROUTER_API_KEY. Use scripts/set_env_secret.py for the key.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
import stat
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"
REPORT_PATH = PROJECT_ROOT / "data" / "reports" / "openrouter_provider_config.json"

OPENROUTER_SETTINGS = {
    "LLM_PROVIDER": "openrouter",
    "LLM_MODEL_ANALYSIS": "openai/gpt-4o",
    "LLM_MODEL_REPLY": "openai/gpt-4o",
    "LLM_MODEL_CONTENT": "openai/gpt-4o",
    "OPENROUTER_APP_TITLE": "VPP Lead Engine",
    "OPENROUTER_SITE_URL": "",
}


def _utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _status(value: str | None) -> str:
    return "SET" if value and value.strip() else "EMPTY"


def _read_env_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines() if path.exists() else []


def _env_value(lines: list[str], key: str) -> str | None:
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in line:
            continue
        current_key, value = line.split("=", 1)
        if current_key.strip() == key:
            return value
    return None


def _write_env_values(path: Path, values: dict[str, str]) -> None:
    lines = _read_env_lines(path)
    output: list[str] = []
    seen: set[str] = set()

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#") or "=" not in line:
            output.append(line)
            continue

        current_key = line.split("=", 1)[0].strip()
        if current_key in values:
            output.append(f"{current_key}={values[current_key]}")
            seen.add(current_key)
        else:
            output.append(line)

    missing = [key for key in values if key not in seen]
    if missing and output and output[-1].strip():
        output.append("")
    for key in missing:
        output.append(f"{key}={values[key]}")

    path.write_text("\n".join(output).rstrip() + "\n", encoding="utf-8")
    try:
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass


def run() -> dict[str, Any]:
    before = _read_env_lines(ENV_PATH)
    before_status = {
        "env_file": "SET" if ENV_PATH.exists() else "MISSING",
        "openrouter_api_key_status": _status(_env_value(before, "OPENROUTER_API_KEY")),
    }

    _write_env_values(ENV_PATH, OPENROUTER_SETTINGS)

    after = _read_env_lines(ENV_PATH)
    configured_status = {
        key.lower() + "_status": _status(_env_value(after, key))
        for key in OPENROUTER_SETTINGS
    }
    result: dict[str, Any] = {
        "test_type": "openrouter_provider_config",
        "config_status": "OK",
        **before_status,
        **configured_status,
        "selected_provider": "openrouter",
        "selected_models": {
            "analysis": OPENROUTER_SETTINGS["LLM_MODEL_ANALYSIS"],
            "reply": OPENROUTER_SETTINGS["LLM_MODEL_REPLY"],
            "content": OPENROUTER_SETTINGS["LLM_MODEL_CONTENT"],
        },
        "openrouter_site_url_status": _status(_env_value(after, "OPENROUTER_SITE_URL")),
        "secret_values_printed": False,
        "external_calls": {
            "redis": False,
            "bitrix24": False,
            "telegram_send": False,
            "imap": False,
            "llm": False,
            "scheduler": False,
            "publisher": False,
        },
        "created_at": _utc_now(),
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result["report_file"] = str(REPORT_PATH.relative_to(PROJECT_ROOT))
    return result


def main() -> int:
    result = run()
    for key in [
        "test_type",
        "config_status",
        "env_file",
        "selected_provider",
        "llm_provider_status",
        "llm_model_analysis_status",
        "llm_model_reply_status",
        "llm_model_content_status",
        "openrouter_api_key_status",
        "openrouter_app_title_status",
        "openrouter_site_url_status",
        "secret_values_printed",
    ]:
        print(f"{key}={result[key]}")
    print(
        "external_calls="
        + ",".join(f"{key}:{value}" for key, value in result["external_calls"].items())
    )
    print(f"report_file={result['report_file']}")
    return 0 if result["config_status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
