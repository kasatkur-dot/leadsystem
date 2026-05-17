"""Close one existing Bitrix24 test lead.

Default target: lead 828 from the Agent 5 full handoff test.

The script does not touch Redis, IMAP, LLM APIs, scheduler, or mass collection.
It does not delete the lead. It marks the lead as the Bitrix24 failure/JUNK
status and writes a local JSON report.
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

from agents.agent5_crm.bitrix import _get_client  # noqa: E402
from config.settings import BITRIX24_WEBHOOK_URL  # noqa: E402


DEFAULT_LEAD_ID = "828"
_FAILURE_NAME_MARKERS = (
    "некачествен",
    "отклон",
    "отказ",
    "закрыт",
    "закрыть",
    "неусп",
    "junk",
    "fail",
    "bad",
)


def _utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _report_path(lead_id: str, dry_run: bool = False) -> Path:
    safe_id = "".join(ch for ch in lead_id if ch.isdigit()) or "unknown"
    suffix = "_dry_run" if dry_run else ""
    return PROJECT_ROOT / "data" / "reports" / f"bitrix_close_test_lead_{safe_id}{suffix}.json"


def _get_field(status: dict[str, Any], name: str) -> Any:
    return status.get(name) if name in status else status.get(name.lower())


def _get_extra(status: dict[str, Any]) -> dict[str, Any]:
    extra = _get_field(status, "EXTRA")
    return extra if isinstance(extra, dict) else {}


def _get_semantics(status: dict[str, Any]) -> str:
    extra = _get_extra(status)
    value = (
        _get_field(status, "SEMANTICS")
        or extra.get("SEMANTICS")
        or extra.get("semantics")
        or ""
    )
    return str(value).strip().lower()


def _status_id(status: dict[str, Any]) -> str:
    value = _get_field(status, "STATUS_ID") or _get_field(status, "ID") or ""
    return str(value).strip()


def _status_name(status: dict[str, Any]) -> str:
    value = _get_field(status, "NAME") or _get_field(status, "NAME_INIT") or ""
    return str(value).strip()


def _status_summary(statuses: list[dict[str, Any]]) -> list[dict[str, str]]:
    summary = []
    for status in statuses:
        summary.append(
            {
                "status_id": _status_id(status),
                "name": _status_name(status),
                "semantics": _get_semantics(status),
            }
        )
    return summary


def _normalize_statuses(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, dict)]
    if isinstance(raw, dict):
        result = raw.get("result")
        if isinstance(result, list):
            return [item for item in result if isinstance(item, dict)]
    return []


def _is_failure_status(status: dict[str, Any]) -> bool:
    status_id = _status_id(status).upper()
    semantics = _get_semantics(status)
    name = _status_name(status).lower()
    return status_id == "JUNK" or semantics in {"f", "failure"} or any(
        marker in name for marker in _FAILURE_NAME_MARKERS
    )


def _choose_failure_status_id(
    statuses: list[dict[str, Any]],
    preferred_status_id: str | None = None,
) -> str | None:
    if preferred_status_id:
        return preferred_status_id

    for status in statuses:
        if _status_id(status).upper() == "JUNK":
            return _status_id(status)
    for status in statuses:
        if _is_failure_status(status) and _status_id(status):
            return _status_id(status)
    return None


def _write_report(report_path: Path, result: dict[str, Any]) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def close_test_lead(
    lead_id: str,
    dry_run: bool = False,
    status_id: str | None = None,
) -> dict[str, Any]:
    report_path = _report_path(lead_id, dry_run=dry_run)
    result: dict[str, Any] = {
        "dry_run": dry_run,
        "test_type": "bitrix_close_test_lead",
        "lead_id": lead_id,
        "external_calls": {
            "bitrix24_attempted": False,
            "bitrix_statuses_read": False,
            "bitrix_timeline_comment_added": False,
            "bitrix_lead_updated": False,
            "bitrix_lead_deleted": False,
            "telegram_send": False,
            "redis": False,
            "llm": False,
            "imap": False,
            "scheduler": False,
        },
        "bitrix_webhook_status": "SET" if BITRIX24_WEBHOOK_URL else "EMPTY",
        "bitrix_close_status": "NOT_RUN",
        "bitrix_status_id": None,
        "bitrix_statuses_found": None,
        "bitrix_available_statuses": [],
        "bitrix_methods": [],
        "created_at": _utc_now(),
    }

    if not BITRIX24_WEBHOOK_URL:
        result["bitrix_close_status"] = "FAILED"
        result["error"] = "BITRIX24_WEBHOOK_URL is EMPTY"
        _write_report(report_path, result)
        return result

    if dry_run:
        result["bitrix_close_status"] = "DRY_RUN"
        _write_report(report_path, result)
        return result

    result["external_calls"]["bitrix24_attempted"] = True

    try:
        bx = _get_client()

        result["bitrix_methods"].append("crm.status.list")
        raw_statuses = bx.call(
            "crm.status.list",
            {
                "order": {"SORT": "ASC"},
                "filter": {"ENTITY_ID": "STATUS"},
            },
            raw=True,
        )
        result["external_calls"]["bitrix_statuses_read"] = True
        result["bitrix_raw_status_response_type"] = type(raw_statuses).__name__

        statuses = _normalize_statuses(raw_statuses)
        result["bitrix_statuses_found"] = len(statuses)
        result["bitrix_available_statuses"] = _status_summary(statuses)

        close_status_id = _choose_failure_status_id(
            statuses,
            preferred_status_id=status_id,
        )
        result["bitrix_status_id"] = close_status_id
        if not close_status_id:
            raise RuntimeError("No failure/JUNK lead status found in Bitrix24")

        comment = (
            "ТЕСТ Agent 5: тестовый лид закрыт после успешной проверки "
            "QualifiedLead -> Bitrix24 -> Telegram. Это не реальный клиент."
        )
        result["bitrix_methods"].append("crm.timeline.comment.add")
        bx.call(
            "crm.timeline.comment.add",
            {
                "fields": {
                    "ENTITY_ID": lead_id,
                    "ENTITY_TYPE": "lead",
                    "COMMENT": comment,
                }
            },
        )
        result["external_calls"]["bitrix_timeline_comment_added"] = True

        result["bitrix_methods"].append("crm.lead.update")
        bx.call(
            "crm.lead.update",
            {
                "id": lead_id,
                "fields": {
                    "STATUS_ID": close_status_id,
                },
            },
        )
        result["external_calls"]["bitrix_lead_updated"] = True
        result["bitrix_close_status"] = "OK"

    except Exception as exc:
        result["bitrix_close_status"] = "FAILED"
        result["error_type"] = type(exc).__name__
        result["error"] = str(exc)[:500]

    _write_report(report_path, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Close one Bitrix24 test lead.")
    parser.add_argument("--lead-id", default=DEFAULT_LEAD_ID)
    parser.add_argument(
        "--status-id",
        default=None,
        help="Bitrix24 lead STATUS_ID to use, for example JUNK.",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    result = close_test_lead(
        lead_id=args.lead_id,
        dry_run=args.dry_run,
        status_id=args.status_id,
    )
    for key in [
        "test_type",
        "lead_id",
        "bitrix_webhook_status",
        "bitrix_close_status",
        "bitrix_status_id",
        "bitrix_statuses_found",
    ]:
        print(f"{key}={result[key]}")
    if result["bitrix_available_statuses"]:
        print("available_statuses=" + json.dumps(result["bitrix_available_statuses"], ensure_ascii=False))
    print(
        "external_calls="
        + ",".join(f"{key}:{value}" for key, value in result["external_calls"].items())
    )
    if result.get("error_type"):
        print(f"error_type={result['error_type']}")
    print(f"report_file={_report_path(args.lead_id, dry_run=args.dry_run).relative_to(PROJECT_ROOT)}")
    return 0 if result["bitrix_close_status"] in {"OK", "DRY_RUN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
