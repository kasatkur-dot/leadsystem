"""Build a local dry-run report for the first 3 qualified leads sprint."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SPRINT_PATH = PROJECT_ROOT / "content" / "growth" / "three-qualified-leads-sprint.csv"
REPORT_JSON_PATH = PROJECT_ROOT / "data" / "reports" / "three_qualified_leads_sprint.json"
REPORT_MD_PATH = PROJECT_ROOT / "data" / "reports" / "three_qualified_leads_sprint.md"


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


def _count_by(rows: list[dict[str, str]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = row.get(key, "") or "EMPTY"
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def _build_report(rows: list[dict[str, str]]) -> dict[str, Any]:
    lead_targets = [
        row for row in rows
        if row.get("goal_metric") == "qualified_leads"
    ]
    ready_items = [
        row for row in rows
        if row.get("status") in {"ready", "draft", "partial_limited_audit"}
    ]
    approval_items = [
        row for row in rows
        if row.get("approval_required") == "yes"
    ]
    return {
        "status": "READY",
        "generated_at": _utc_now(),
        "sprint_file": _relative(SPRINT_PATH),
        "goal": "3 qualified leads",
        "sprint_items_count": len(rows),
        "qualified_lead_target_count": sum(int(row.get("target_count") or 0) for row in lead_targets),
        "ready_or_draft_items": len(ready_items),
        "approval_required_items": len(approval_items),
        "by_week": _count_by(rows, "week"),
        "by_segment": _count_by(rows, "segment"),
        "by_agent": _count_by(rows, "agent_owner"),
        "items": rows,
        "astrology_method_mapping": {
            "expert": "ВПП: СРО, 10+ лет, проектирование, перепланировки, реконструкция",
            "product": "AI-проверка исходных данных к КП",
            "content_factory": "MAX B2B posts + future landing pages + tender filters",
            "traffic_sources": "MAX, Tender, Bitrix old base, future Telegram/VK/ABM",
            "warmup": "серия экспертных постов и approved-only ответы",
            "conversion": "Bitrix24 -> КП -> договор",
        },
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
        "# Three Qualified Leads Sprint",
        "",
        f"Generated at: `{report['generated_at']}`",
        "",
        "Статус: локальный dry-run. Внешние действия не запускались.",
        "",
        "## Goal",
        "",
        f"- Цель: {report['goal']}",
        f"- Sprint items: {report['sprint_items_count']}",
        f"- Target qualified leads: {report['qualified_lead_target_count']}",
        f"- Ready/draft items: {report['ready_or_draft_items']}",
        f"- Approval required items: {report['approval_required_items']}",
        "",
        "## Astrology Method Mapping",
        "",
    ]
    for key, value in report["astrology_method_mapping"].items():
        lines.append(f"- `{key}`: {value}")

    lines.extend(["", "## Sprint Items", "", "| ID | Week | Segment | Agent | Source | Metric | Target | Status | Next |", "|---|---:|---|---|---|---|---:|---|---|"])
    for item in report["items"]:
        lines.append(
            "| {sprint_item_id} | {week} | {segment} | {agent_owner} | {source} | {goal_metric} | {target_count} | {status} | {next_action} |".format(**item)
        )
    lines.append("")
    REPORT_MD_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = _read_rows(SPRINT_PATH)
    report = _build_report(rows)
    REPORT_JSON_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_markdown(report)
    print("three_qualified_leads_sprint_status=READY")
    print(f"sprint_items_count={report['sprint_items_count']}")
    print(f"qualified_lead_target_count={report['qualified_lead_target_count']}")
    print(f"approval_required_items={report['approval_required_items']}")
    print(f"report_file={_relative(REPORT_JSON_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
