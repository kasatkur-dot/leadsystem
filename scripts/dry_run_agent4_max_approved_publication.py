"""Approved-only dry-run for Agent 4 MAX publication.

This script never calls MAX API. It reads the publication tracker, verifies that
the selected content is approved for MAX, prepares the public post body, runs the
MAX poster in dry-run mode, and writes a local report.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.agent4_publisher.posters.max import publish_file

TRACKER_PATH = ROOT / "content/pipeline/publication-tracker-mvp.csv"
REPORT_DIR = ROOT / "data/reports"
DEFAULT_CONTENT_ID = "lead-post-001"
PUBLICATION_HEADING = "## Пост для ручной публикации"


def _read_tracker_row(content_id: str) -> dict[str, str]:
    if not TRACKER_PATH.exists():
        raise FileNotFoundError(f"Tracker not found: {TRACKER_PATH}")

    with TRACKER_PATH.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row.get("content_id") == content_id:
                return row

    raise ValueError(f"content_id not found in tracker: {content_id}")


def _extract_public_post(markdown: str) -> str:
    lines = markdown.splitlines()
    start_index: int | None = None

    for index, line in enumerate(lines):
        if line.strip() == PUBLICATION_HEADING:
            start_index = index + 1
            break

    if start_index is None:
        raise ValueError(f"Publication heading not found: {PUBLICATION_HEADING}")

    body_lines: list[str] = []
    for line in lines[start_index:]:
        if line.startswith("## "):
            break
        body_lines.append(line)

    body = "\n".join(body_lines).strip()
    if not body:
        raise ValueError("Publication body is empty")
    return body


def _validate_row(row: dict[str, str]) -> list[str]:
    errors: list[str] = []
    if row.get("status") != "approved":
        errors.append(f"status must be approved, got {row.get('status')!r}")
    if row.get("channel") != "MAX":
        errors.append(f"channel must be MAX, got {row.get('channel')!r}")
    if not row.get("source_file"):
        errors.append("source_file is empty")
    if not row.get("funnel_arc"):
        errors.append("funnel_arc is empty")
    if not row.get("offer_id"):
        errors.append("offer_id is empty")
    if not row.get("main_cta"):
        errors.append("main_cta is empty")
    return errors


def run(content_id: str = DEFAULT_CONTENT_ID) -> dict[str, Any]:
    row = _read_tracker_row(content_id)
    errors = _validate_row(row)

    source_file = ROOT / row.get("source_file", "")
    if row.get("source_file") and not source_file.exists():
        errors.append(f"source_file does not exist: {source_file}")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    prepared_path = REPORT_DIR / f"{content_id}_max_dry_run_message.md"
    report_path = REPORT_DIR / f"{content_id}_max_approved_dry_run.json"

    public_text = ""
    poster_result: dict[str, Any] | None = None
    if not errors:
        markdown = source_file.read_text(encoding="utf-8")
        public_text = _extract_public_post(markdown)
        prepared_path.write_text(public_text + "\n", encoding="utf-8")
        poster_result = publish_file(prepared_path, lead_id=None, dry_run=True)

    report: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "OK" if not errors else "BLOCKED",
        "content_id": content_id,
        "checks": {
            "tracker_exists": TRACKER_PATH.exists(),
            "row_found": True,
            "status_is_approved": row.get("status") == "approved",
            "channel_is_max": row.get("channel") == "MAX",
            "source_file_exists": source_file.exists(),
            "funnel_arc_present": bool(row.get("funnel_arc")),
            "offer_id_present": bool(row.get("offer_id")),
            "main_cta_present": bool(row.get("main_cta")),
        },
        "tracker_row": {
            "channel": row.get("channel"),
            "status": row.get("status"),
            "source_file": row.get("source_file"),
            "funnel_arc": row.get("funnel_arc"),
            "funnel_stage": row.get("funnel_stage"),
            "offer_id": row.get("offer_id"),
            "main_cta": row.get("main_cta"),
            "next_bridge": row.get("next_bridge"),
        },
        "prepared_publication": {
            "path": str(prepared_path) if public_text else None,
            "chars": len(public_text),
            "heading_used": PUBLICATION_HEADING,
        },
        "poster_result": poster_result,
        "external_calls": {
            "max_api": False,
            "telegram": False,
            "bitrix24": False,
            "redis": False,
            "llm": False,
            "paid_api": False,
            "scheduler": False,
        },
        "errors": errors,
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"report": report, "report_path": report_path}


def main() -> int:
    parser = argparse.ArgumentParser(description="Approved-only MAX dry-run for Agent 4")
    parser.add_argument("--content-id", default=DEFAULT_CONTENT_ID)
    args = parser.parse_args()

    result = run(args.content_id)
    report = result["report"]
    print(f"agent4_max_approved_dry_run_status={report['status']}")
    print(f"report_path={result['report_path'].relative_to(ROOT)}")
    if report["status"] != "OK":
        for error in report["errors"]:
            print(f"error={error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
