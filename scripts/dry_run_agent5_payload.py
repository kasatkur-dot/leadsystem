"""Safe Agent 5 dry-run for one synthetic QualifiedLead.

This script builds the Bitrix24 fields and Telegram manager message locally.
It does not call Bitrix24, Telegram, Redis, IMAP, LLM APIs, or the scheduler.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from agents.agent5_crm.bitrix import build_lead_fields
from agents.agent5_crm.notifier import build_message
from scripts.dry_run_synthetic_lead import build_qualified_lead


REPORT_PATH = PROJECT_ROOT / "data" / "reports" / "agent5_payload_dry_run.json"


def _redact_value(value, secrets: set[str]):
    if isinstance(value, str):
        redacted = value
        for secret in secrets:
            if secret:
                redacted = redacted.replace(secret, "REDACTED")
        return redacted
    if isinstance(value, list):
        return [_redact_value(item, secrets) for item in value]
    if isinstance(value, dict):
        return {key: _redact_value(item, secrets) for key, item in value.items()}
    return value


def _redact_contact_fields(fields: dict, contact: str | None) -> dict:
    safe = _redact_value(fields, {contact or "", "test@example.com"})
    if "PHONE" in safe:
        safe["PHONE"] = [{"VALUE": "REDACTED", "VALUE_TYPE": item.get("VALUE_TYPE", "WORK")} for item in safe["PHONE"]]
    if "EMAIL" in safe:
        safe["EMAIL"] = [{"VALUE": "REDACTED", "VALUE_TYPE": item.get("VALUE_TYPE", "WORK")} for item in safe["EMAIL"]]
    if "IM" in safe:
        safe["IM"] = [{"VALUE": "REDACTED", "VALUE_TYPE": item.get("VALUE_TYPE", "TELEGRAM")} for item in safe["IM"]]
    return safe


def run() -> dict:
    _raw, qualified, _enriched = build_qualified_lead()
    bitrix_fields = build_lead_fields(qualified)
    telegram_message = build_message(qualified)

    result = {
        "dry_run": True,
        "external_calls": {
            "redis": False,
            "llm": False,
            "bitrix24": False,
            "telegram_send": False,
            "imap": False,
            "scheduler": False,
        },
        "qualified_lead_status": "OK",
        "bitrix_payload_status": "OK",
        "telegram_payload_status": "OK",
        "bitrix_method": "crm.lead.add",
        "bitrix_fields": _redact_contact_fields(bitrix_fields, qualified.contact),
        "telegram_message_preview": telegram_message.replace(qualified.contact or "", "REDACTED")[:1200],
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    result = run()
    print(f"dry_run={result['dry_run']}")
    print(
        "external_calls="
        + ",".join(f"{key}:{value}" for key, value in result["external_calls"].items())
    )
    print(f"qualified_lead_status={result['qualified_lead_status']}")
    print(f"bitrix_payload_status={result['bitrix_payload_status']}")
    print(f"telegram_payload_status={result['telegram_payload_status']}")
    print(f"bitrix_method={result['bitrix_method']}")
    print(f"bitrix_field_count={len(result['bitrix_fields'])}")
    print(f"telegram_message_chars={len(result['telegram_message_preview'])}")
    print(f"report_file={REPORT_PATH.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
