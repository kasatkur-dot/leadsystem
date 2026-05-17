"""Create one real test lead in Bitrix24 through Agent 5 mapping.

This controlled external test calls only Bitrix24 `crm.lead.add`.
It does not touch Telegram sending, IMAP, Redis queues, LLM APIs, or scheduler.
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
from shared.models import QualifiedLead


REPORT_PATH = PROJECT_ROOT / "data" / "reports" / "agent5_bitrix_lead_test.json"


def build_test_lead() -> QualifiedLead:
    return QualifiedLead(
        id=str(uuid.uuid4()),
        raw_lead_id=str(uuid.uuid4()),
        source="tender_email",
        flow="B",
        contact=None,
        contact_type=None,
        company_name="ТЕСТ Agent 5 — удалить после проверки",
        city="Краснодар",
        object_type="склад",
        area_m2=1200,
        score="hot",
        score_reason="ТЕСТ: проверяем создание лида Bitrix24 из Agent 5.",
        offer_text="ТЕСТ: это не реальный лид. Проверяем только crm.lead.add.",
        recommended_action="ничего не делать, это тест",
        source_type="manual_test",
        traffic_channel="manual",
        first_touch_channel="manual",
        last_touch_channel="manual",
        utm_source="agent5_bitrix_test",
        utm_medium="manual",
        consent_status="not_required",
        raw_text=(
            "ТЕСТ Agent 5 Bitrix24. Это не реальный клиент. "
            "Проверяем только создание тестового лида через crm.lead.add."
        ),
    )


def run() -> dict:
    lead = build_test_lead()
    fields = build_lead_fields(lead)
    bitrix_id = create_lead(lead)
    result = {
        "dry_run": False,
        "test_type": "agent5_bitrix_lead",
        "external_calls": {
            "bitrix24_attempted": True,
            "bitrix24_created": bool(bitrix_id),
            "telegram_send": False,
            "redis": False,
            "llm": False,
            "imap": False,
            "scheduler": False,
        },
        "bitrix_payload_status": "OK",
        "bitrix_send_status": "OK" if bitrix_id else "FAILED",
        "bitrix_method": "crm.lead.add",
        "bitrix_id": bitrix_id,
        "title": fields.get("TITLE"),
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
        "bitrix_payload_status",
        "bitrix_send_status",
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
    return 0 if result["bitrix_send_status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
