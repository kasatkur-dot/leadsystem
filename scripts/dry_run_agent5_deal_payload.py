"""Safe local dry-run for Agent 5 Bitrix24 deal payload.

Reads a local QualifiedLead artifact and prepares `crm.deal.add` payload.
It does not call Bitrix24, Redis, Telegram, IMAP, LLM APIs, or scheduler.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from agents.agent5_crm.deal_payload_builder import build_deal_payload, redact_payload_for_report
from shared.models import QualifiedLead


INPUT_PATH = PROJECT_ROOT / "data" / "reports" / "first_inbound_qualified_lead_dry_run.json"
REPORT_PATH = PROJECT_ROOT / "data" / "reports" / "agent5_deal_payload_dry_run.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _read_qualified_lead(path: Path) -> QualifiedLead:
    data = json.loads(path.read_text(encoding="utf-8"))
    lead_data: dict[str, Any] = data["output"]
    return QualifiedLead.model_validate(lead_data)


def run() -> dict[str, Any]:
    lead = _read_qualified_lead(INPUT_PATH)
    payload = build_deal_payload(lead)
    safe_payload = redact_payload_for_report(payload, lead.contact)

    result: dict[str, Any] = {
        "test_type": "agent5_deal_payload_dry_run",
        "dry_run": True,
        "created_at": _utc_now(),
        "input_file": str(INPUT_PATH.relative_to(PROJECT_ROOT)),
        "output_artifact": "crm_payload_preview",
        "external_calls": {
            "redis": False,
            "bitrix24": False,
            "telegram_send": False,
            "imap": False,
            "llm": False,
            "scheduler": False,
            "publisher": False,
        },
        "qualified_lead_status": "OK",
        "deal_payload_status": "OK",
        "bitrix_method": safe_payload["method"],
        "bitrix_send_status": safe_payload["send_status"],
        "entity_type": safe_payload["entity_type"],
        "site_source": safe_payload["site_source"],
        "source_id": safe_payload["source_id"],
        "category_id": safe_payload["category_id"],
        "stage_id": safe_payload["stage_id"],
        "assigned_by_id": safe_payload["assigned_by_id"],
        "field_count": len(safe_payload["params"]["fields"]),
        "payload_preview": safe_payload,
        "fields_to_confirm_before_real_send": safe_payload["fields_to_confirm_before_real_send"],
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
        "dry_run",
        "qualified_lead_status",
        "deal_payload_status",
        "bitrix_method",
        "bitrix_send_status",
        "entity_type",
        "site_source",
        "source_id",
        "category_id",
        "stage_id",
        "assigned_by_id",
        "field_count",
    ]:
        print(f"{key}={result[key]}")
    print(
        "external_calls="
        + ",".join(f"{key}:{value}" for key, value in result["external_calls"].items())
    )
    print(f"report_file={REPORT_PATH.relative_to(PROJECT_ROOT)}")
    return 0 if result["deal_payload_status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
