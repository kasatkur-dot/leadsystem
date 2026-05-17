"""Controlled Agent 4 LLM-router test.

Default mode is dry-run. A real LLM call happens only with `--execute`.
The script creates a local draft and never publishes it.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from agents.agent4_publisher.core.llm import generate_post_text, save_post
from config import settings


REPORT_PATH = PROJECT_ROOT / "data" / "reports" / "agent4_unified_llm_router_test.json"
DRY_RUN_OUTPUT = PROJECT_ROOT / "data" / "reports" / "agent4_unified_llm_router_dry_run.md"
EXECUTE_OUTPUT = PROJECT_ROOT / "data" / "reports" / "agent4_unified_llm_router_execute_test.md"
TEST_TOPIC = "Почему проект склада лучше проверить до начала стройки"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _secret_status(value: str | None) -> str:
    return "SET" if value else "EMPTY"


def _env_status() -> dict[str, str]:
    return {
        "LLM_PROVIDER": settings.LLM_PROVIDER or "EMPTY",
        "LLM_MODEL_CONTENT": _secret_status(settings.LLM_MODEL_CONTENT),
        "OPENROUTER_API_KEY": _secret_status(settings.OPENROUTER_API_KEY),
        "OPENROUTER_SITE_URL": _secret_status(settings.OPENROUTER_SITE_URL),
        "OPENROUTER_APP_TITLE": _secret_status(settings.OPENROUTER_APP_TITLE),
        "ANTHROPIC_API_KEY": _secret_status(settings.ANTHROPIC_API_KEY),
    }


def run(*, execute: bool) -> dict[str, Any]:
    load_dotenv(PROJECT_ROOT / ".env", override=True)
    output_path = EXECUTE_OUTPUT if execute else DRY_RUN_OUTPUT
    llm_status = "NOT_RUN"
    error: str | None = None
    text = ""

    try:
        text = generate_post_text(TEST_TOPIC, dry_run=not execute)
        save_post(TEST_TOPIC, text, str(output_path))
        llm_status = "OK" if execute else "DRY_RUN"
    except Exception as exc:
        llm_status = "FAILED"
        error = str(exc)[:1000]

    report = {
        "test_type": "agent4_unified_llm_router_test",
        "created_at": _utc_now(),
        "dry_run": not execute,
        "execute": execute,
        "topic": TEST_TOPIC,
        "env_status": _env_status(),
        "external_calls": {
            "llm": execute and llm_status == "OK",
            "bitrix24": False,
            "redis": False,
            "telegram_send": False,
            "max_publish": False,
            "vk_publish": False,
            "dzen_publish": False,
            "scheduler": False,
            "publisher": False,
        },
        "llm_router": "shared/llm_client.py",
        "agent4_module": "agents/agent4_publisher/core/llm.py",
        "llm_status": llm_status,
        "error": error,
        "output_file": str(output_path.relative_to(PROJECT_ROOT)) if text else None,
        "text_chars": len(text),
        "text_preview": text[:500],
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one controlled Agent 4 LLM-router test")
    parser.add_argument("--execute", action="store_true", help="Call the configured LLM once")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run(execute=args.execute)
    print("agent4_llm_router_test_status=" + result["llm_status"])
    print("execute=" + str(result["execute"]))
    print("LLM_PROVIDER=" + result["env_status"]["LLM_PROVIDER"])
    print("LLM_MODEL_CONTENT=" + result["env_status"]["LLM_MODEL_CONTENT"])
    print("OPENROUTER_API_KEY=" + result["env_status"]["OPENROUTER_API_KEY"])
    print("llm_router=" + result["llm_router"])
    print("output_file=" + str(result["output_file"]))
    print("text_chars=" + str(result["text_chars"]))
    print(
        "external_calls="
        + ",".join(f"{key}:{value}" for key, value in result["external_calls"].items())
    )
    print("report_file=" + str(REPORT_PATH.relative_to(PROJECT_ROOT)))
    return 0 if result["llm_status"] in {"OK", "DRY_RUN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
