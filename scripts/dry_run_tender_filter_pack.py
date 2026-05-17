"""Build a local dry-run report for VPP tender filters.

No tender platforms are opened or queried. This only validates the local filter
pack and produces a checklist report.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FILTER_PATH = PROJECT_ROOT / "content" / "library" / "sources" / "tender-filter-pack-vpp.csv"
REPORT_JSON_PATH = PROJECT_ROOT / "data" / "reports" / "tender_filter_pack_dry_run.json"
REPORT_MD_PATH = PROJECT_ROOT / "data" / "reports" / "tender_filter_pack_dry_run.md"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _relative(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return [
            {key: (value or "").strip() for key, value in row.items()}
            for row in csv.DictReader(file)
            if any((value or "").strip() for value in row.values())
        ]


def _validate(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    checks = []
    required = ["filter_id", "segment", "query_keywords", "include_words", "exclude_words", "priority", "owner_agent"]
    for row in rows:
        missing = [field for field in required if not row.get(field)]
        checks.append(
            {
                "filter_id": row.get("filter_id", ""),
                "segment": row.get("segment", ""),
                "priority": row.get("priority", ""),
                "status": "OK" if not missing else "MISSING_FIELDS",
                "missing_fields": missing,
                "bitrix_tags": [
                    "source:tender",
                    f"segment:{row.get('segment', '')}",
                    f"priority:{row.get('priority', '')}",
                    "mode:read_only",
                ],
                "stop_rule": "Не подавать заявку, не оплачивать площадку и не создавать сделку без approval.",
            }
        )
    return checks


def _write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Tender Filter Pack Dry Run",
        "",
        f"Generated at: `{report['generated_at']}`",
        "",
        "Статус: локальный dry-run. Тендерные площадки не открывались, заявки не подавались.",
        "",
        "| Filter | Segment | Priority | Status | Stop rule |",
        "|---|---|---|---|---|",
    ]
    for item in report["checks"]:
        lines.append(
            "| {filter_id} | {segment} | {priority} | {status} | {stop_rule} |".format(**item)
        )
    lines.extend(["", "## Approval Required Before", ""])
    for item in report["approval_required_before"]:
        lines.append(f"- `{item}`")
    lines.append("")
    REPORT_MD_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = _read_rows(FILTER_PATH)
    checks = _validate(rows)
    report = {
        "status": "READY" if rows and all(item["status"] == "OK" for item in checks) else "NEEDS_REVIEW",
        "generated_at": _utc_now(),
        "filter_file": _relative(FILTER_PATH),
        "filter_count": len(rows),
        "checks": checks,
        "approval_required_before": [
            "open_paid_aggregator",
            "register_tender_platform",
            "upload_documents",
            "submit_bid",
            "create_bitrix_deal",
            "create_manager_task",
        ],
        "external_calls": {
            "tender_platform": False,
            "bitrix24": False,
            "ads": False,
            "llm": False,
            "scheduler": False,
            "publisher": False,
        },
    }
    REPORT_JSON_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_markdown(report)
    print(f"tender_filter_pack_status={report['status']}")
    print(f"filter_count={report['filter_count']}")
    print(f"report_file={_relative(REPORT_JSON_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
