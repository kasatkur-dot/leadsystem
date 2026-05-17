"""Send one real Agent 5 Telegram test notification.

This is the first controlled external test after dry-run checks.
It sends exactly one Telegram bot message and does not touch Bitrix24,
IMAP, Redis queues, LLM APIs, or the scheduler.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
import sys
import uuid

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from agents.agent5_crm.notifier import build_message, notify
from shared.models import QualifiedLead


REPORT_PATH = PROJECT_ROOT / "data" / "reports" / "agent5_telegram_notify_test.json"


def build_test_lead() -> QualifiedLead:
    return QualifiedLead(
        id=str(uuid.uuid4()),
        raw_lead_id=str(uuid.uuid4()),
        source="tender_email",
        flow="B",
        contact=None,
        contact_type=None,
        company_name="ТЕСТ Agent 5",
        city="Краснодар",
        object_type="склад",
        area_m2=1200,
        score="hot",
        score_reason="Тестовое уведомление: проверяем, что Agent 5 доставляет сообщение менеджеру.",
        offer_text=(
            "ТЕСТ: это не реальный лид. Проверяем только доставку Telegram-уведомления "
            "после успешного dry-run payload."
        ),
        recommended_action="ничего не делать, это тест",
        source_type="manual_test",
        traffic_channel="manual",
        first_touch_channel="manual",
        last_touch_channel="manual",
        utm_source="agent5_test",
        utm_medium="manual",
        consent_status="not_required",
        raw_text=(
            "ТЕСТ Agent 5. Один безопасный внешний тест Telegram-уведомления. "
            "Bitrix24, IMAP, Redis-очереди, LLM и scheduler не запускаются."
        ),
    )


def run() -> dict:
    lead = build_test_lead()
    message = build_message(lead)
    sent = notify(lead)
    result = {
        "dry_run": False,
        "test_type": "agent5_telegram_notification",
        "external_calls": {
            "telegram_send": bool(sent),
            "bitrix24": False,
            "redis": False,
            "llm": False,
            "imap": False,
            "scheduler": False,
        },
        "telegram_payload_status": "OK",
        "telegram_send_status": "OK" if sent else "FAILED",
        "telegram_message_chars": len(message),
        "lead_id_prefix": lead.id[:8],
        "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    result = run()
    for key in [
        "test_type",
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
    return 0 if result["telegram_send_status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
