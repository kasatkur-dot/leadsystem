"""Create one real test Bitrix24 lead and send one Telegram notification.

This controlled external test covers the Agent 5 handoff:
QualifiedLead -> Bitrix24 `crm.lead.add` -> Telegram manager notification.

It does not touch IMAP, Redis queues, LLM APIs, scheduler, or mass collection.
The created lead is clearly marked as TEST.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
import sys
import uuid

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from agents.agent5_crm.bitrix import build_lead_fields, create_lead
from agents.agent5_crm.notifier import build_message, notify
from shared.models import QualifiedLead


REPORT_PATH = PROJECT_ROOT / "data" / "reports" / "agent5_full_handoff_test.json"


def build_test_lead() -> QualifiedLead:
    return QualifiedLead(
        id=str(uuid.uuid4()),
        raw_lead_id=str(uuid.uuid4()),
        source="tender_email",
        flow="B",
        contact="test-agent5@example.invalid",
        contact_type="email",
        company_name="ТЕСТ Agent 5 full handoff — удалить после проверки",
        city="Краснодар",
        object_type="склад",
        area_m2=1200,
        score="hot",
        score_reason=(
            "ТЕСТ: проверяем полный handoff Agent 5 — создание лида Bitrix24 "
            "и Telegram-уведомление менеджеру."
        ),
        offer_text=(
            "ТЕСТ: это не реальный лид. Проверяем только связку "
            "Bitrix24 + Telegram."
        ),
        recommended_action="ничего не делать, это тест",
        source_type="manual_test",
        traffic_channel="manual",
        first_touch_channel="manual",
        last_touch_channel="manual",
        utm_source="agent5_full_handoff_test",
        utm_medium="manual",
        consent_status="not_required",
        raw_text=(
            "ТЕСТ Agent 5 full handoff. Это не реальный клиент. "
            "Проверяем создание тестового лида в Bitrix24 и уведомление в Telegram."
        ),
    )


def run() -> dict:
    lead = build_test_lead()
    fields = build_lead_fields(lead)
    message = build_message(lead)
    bitrix_id = create_lead(lead)
    telegram_ok = notify(lead)

    result = {
        "dry_run": False,
        "test_type": "agent5_full_handoff",
        "external_calls": {
            "bitrix24_attempted": True,
            "bitrix24_created": bool(bitrix_id),
            "telegram_attempted": True,
            "telegram_send": telegram_ok,
            "redis": False,
            "llm": False,
            "imap": False,
            "scheduler": False,
        },
        "bitrix_payload_status": "OK",
        "bitrix_send_status": "OK" if bitrix_id else "FAILED",
        "telegram_payload_status": "OK",
        "telegram_send_status": "OK" if telegram_ok else "FAILED",
        "bitrix_method": "crm.lead.add",
        "bitrix_id": bitrix_id,
        "title": fields.get("TITLE"),
        "name": fields.get("NAME"),
        "lead_id_prefix": lead.id[:8],
        "telegram_message_chars": len(message),
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
        "bitrix_payload_status",
        "bitrix_send_status",
        "telegram_payload_status",
        "telegram_send_status",
        "bitrix_method",
        "bitrix_id",
        "lead_id_prefix",
    ]:
        print(f"{key}={result[key]}")
    print(
        "external_calls="
        + ",".join(f"{key}:{value}" for key, value in result["external_calls"].items())
    )
    print(f"report_file={REPORT_PATH.relative_to(PROJECT_ROOT)}")
    return 0 if (
        result["bitrix_send_status"] == "OK"
        and result["telegram_send_status"] == "OK"
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
