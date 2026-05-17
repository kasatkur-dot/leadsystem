"""Retry Telegram notification for the last Agent 5 Redis queue test.

This script reads data/reports/agent5_redis_queue_handoff_test.json and sends
only one Telegram notification for the already-created Bitrix24 test lead.

It does not call Bitrix24, Redis, IMAP, LLM APIs, scheduler, or mass collection.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
import sys
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from agents.agent5_crm.notifier import build_message, notify  # noqa: E402
from scripts.test_agent5_redis_queue_handoff import build_test_lead  # noqa: E402


SOURCE_REPORT_PATH = PROJECT_ROOT / "data" / "reports" / "agent5_redis_queue_handoff_test.json"
REPORT_PATH = PROJECT_ROOT / "data" / "reports" / "agent5_redis_telegram_retry_test.json"


def _utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _read_source_report() -> dict[str, Any]:
    return json.loads(SOURCE_REPORT_PATH.read_text(encoding="utf-8"))


def _write_report(result: dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def run(dry_run: bool = False) -> dict[str, Any]:
    source = _read_source_report()
    bitrix_id = source.get("bitrix_id")
    lead_id_prefix = source.get("lead_id_prefix") or "unknown"

    lead = build_test_lead().model_copy(
        update={
            "id": f"{lead_id_prefix}-telegram-retry",
            "score_reason": (
                "ТЕСТ: повторяем только Telegram-уведомление после исправления "
                "HTML-форматирования. Bitrix24-лид уже создан."
            ),
            "offer_text": (
                f"ТЕСТ: это не реальный лид. Повтор уведомления для уже созданного "
                f"Bitrix24 лида #{bitrix_id}. Новые лиды в Bitrix24 не создаются."
            ),
        }
    )
    message = build_message(lead)

    result: dict[str, Any] = {
        "dry_run": dry_run,
        "test_type": "agent5_redis_telegram_retry",
        "source_report": str(SOURCE_REPORT_PATH.relative_to(PROJECT_ROOT)),
        "bitrix_id": bitrix_id,
        "lead_id_prefix": lead_id_prefix,
        "external_calls": {
            "telegram_attempted": False,
            "telegram_send": False,
            "bitrix24": False,
            "redis": False,
            "llm": False,
            "imap": False,
            "scheduler": False,
        },
        "telegram_payload_status": "OK",
        "telegram_send_status": "DRY_RUN" if dry_run else "NOT_RUN",
        "telegram_message_chars": len(message),
        "created_at": _utc_now(),
    }

    if dry_run:
        _write_report(result)
        return result

    sent = notify(lead)
    result["external_calls"]["telegram_attempted"] = True
    result["external_calls"]["telegram_send"] = sent
    result["telegram_send_status"] = "OK" if sent else "FAILED"
    _write_report(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Retry one Telegram notification for Bitrix24 lead from Redis test.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    result = run(dry_run=args.dry_run)
    for key in [
        "test_type",
        "bitrix_id",
        "telegram_payload_status",
        "telegram_send_status",
        "telegram_message_chars",
        "lead_id_prefix",
    ]:
        print(f"{key}={result[key]}")
    print(
        "external_calls="
        + ",".join(f"{key}:{value}" for key, value in result["external_calls"].items())
    )
    print(f"report_file={REPORT_PATH.relative_to(PROJECT_ROOT)}")
    return 0 if result["telegram_send_status"] in {"OK", "DRY_RUN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
