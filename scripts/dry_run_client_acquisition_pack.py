"""Build a local client acquisition pack from prepared sources and routes.

No external systems are called. The report connects the lecture method to VPP
routes, content assets, UTM tags, Bitrix tags, and approval gates.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ROUTES_PATH = PROJECT_ROOT / "content" / "growth" / "acquisition-route-pack-vpp.csv"
REPORT_JSON_PATH = PROJECT_ROOT / "data" / "reports" / "client_acquisition_pack_dry_run.json"
REPORT_MD_PATH = PROJECT_ROOT / "data" / "reports" / "client_acquisition_pack_dry_run.md"


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


def _status(row: dict[str, str]) -> str:
    required = ["route_id", "segment", "priority", "primary_source", "offer", "asset", "utm_source", "utm_campaign", "bitrix_tags", "stop_rule"]
    missing = [field for field in required if not row.get(field)]
    return "OK" if not missing else "MISSING_FIELDS"


def _build_report(rows: list[dict[str, str]]) -> dict[str, Any]:
    routes = []
    for row in rows:
        routes.append(
            {
                **row,
                "status": _status(row),
                "approval_gate": "APPROVAL_REQUIRED" if row.get("approval_required") == "yes" else "CHECK_REQUIRED",
                "external_action_status": "NOT_STARTED",
            }
        )

    priorities: dict[str, int] = {}
    sources: dict[str, int] = {}
    for route in routes:
        priorities[route["priority"]] = priorities.get(route["priority"], 0) + 1
        sources[route["primary_source"]] = sources.get(route["primary_source"], 0) + 1

    return {
        "status": "READY" if routes and all(route["status"] == "OK" for route in routes) else "NEEDS_REVIEW",
        "generated_at": _utc_now(),
        "route_file": _relative(ROUTES_PATH),
        "route_count": len(routes),
        "summary": {
            "by_priority": dict(sorted(priorities.items())),
            "by_primary_source": dict(sorted(sources.items())),
            "approval_required_routes": sum(1 for route in routes if route["approval_gate"] == "APPROVAL_REQUIRED"),
        },
        "routes": routes,
        "supporting_assets": [
            "docs/client-acquisition-operating-system-from-lecture.md",
            "content/growth/approved-only-outreach-templates-vpp.md",
            "site/landing-drafts/b2b-segment-landing-blueprints.md",
            "content/pipeline/drafts/max-b2b-first-wave-2026-05-16.md",
            "docs/tender-readonly-filter-and-decision-pack.md",
        ],
        "external_calls": {
            "bitrix24": False,
            "max": False,
            "telegram_send": False,
            "vk": False,
            "tender_platform": False,
            "ads": False,
            "llm": False,
            "scheduler": False,
            "publisher": False,
        },
    }


def _write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Client Acquisition Pack Dry Run",
        "",
        f"Generated at: `{report['generated_at']}`",
        "",
        "Статус: локальный dry-run. Внешние действия не запускались.",
        "",
        "## Summary",
        "",
        f"- Routes: {report['route_count']}",
        f"- Approval required: {report['summary']['approval_required_routes']}",
        f"- By priority: {json.dumps(report['summary']['by_priority'], ensure_ascii=False)}",
        f"- By source: {json.dumps(report['summary']['by_primary_source'], ensure_ascii=False)}",
        "",
        "## Routes",
        "",
        "| Route | Segment | Priority | Source | Offer | Asset | Approval | Stop rule |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for route in report["routes"]:
        lines.append(
            "| {route_id} | {segment} | {priority} | {primary_source} | {offer} | {asset} | {approval_gate} | {stop_rule} |".format(**route)
        )
    lines.extend(["", "## Supporting Assets", ""])
    for asset in report["supporting_assets"]:
        lines.append(f"- `{asset}`")
    lines.append("")
    REPORT_MD_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = _read_rows(ROUTES_PATH)
    report = _build_report(rows)
    REPORT_JSON_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_markdown(report)
    print(f"client_acquisition_pack_status={report['status']}")
    print(f"route_count={report['route_count']}")
    print(f"approval_required_routes={report['summary']['approval_required_routes']}")
    print(f"report_file={_relative(REPORT_JSON_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
