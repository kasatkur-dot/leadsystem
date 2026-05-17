"""Check that the content funnel MVP has the required control fields.

This checker is local and read-only. It does not call Redis, Bitrix24,
Telegram, MAX, LLM APIs, scheduler, publisher, or paid services.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = PROJECT_ROOT / "data" / "reports" / "content_funnel_contract_check.json"

PIPELINE = PROJECT_ROOT / "content" / "pipeline"
PUBLICATION_TRACKER = PIPELINE / "publication-tracker-mvp.csv"
TOPIC_RESPONSE_TRACKER = PIPELINE / "topic-response-tracker-mvp.csv"
FUNNEL_ARCS = PIPELINE / "post-funnel-arcs-mvp.csv"
OFFER_READINESS = PIPELINE / "offer-readiness-map-mvp.csv"
SLOT_MATRIX = PIPELINE / "content-slot-matrix-mvp.md"
FUNNEL_OS = PIPELINE / "post-funnel-operating-system.md"
FUTURE_BACKLOG = PIPELINE / "future-opportunities-backlog.md"
TEN_POST_PLAN = PIPELINE / "content-plan-10-posts-lead-mvp-2026-05.md"

REQUIRED_PUBLICATION_FIELDS = [
    "content_id",
    "channel",
    "segment",
    "service_line",
    "funnel_arc",
    "funnel_stage",
    "offer_id",
    "offer_readiness",
    "monetization_role",
    "cta_intensity",
    "main_cta",
    "next_bridge",
    "status",
    "views",
    "lead_count",
    "qualified_count",
    "deal_count",
    "revenue_rub",
    "romi_decision",
    "next_action",
]

REQUIRED_TOPIC_FIELDS = [
    "topic_id",
    "content_id",
    "channel",
    "topic",
    "funnel_arc",
    "funnel_stage",
    "pain_or_intent",
    "main_cta",
    "views",
    "questions",
    "plan_sent_count",
    "lead_count",
    "qualified_count",
    "deal_count",
    "revenue_rub",
    "main_signal",
    "decision",
    "next_action",
]

REQUIRED_FUNNEL_ARC_FIELDS = [
    "arc_id",
    "status",
    "goal",
    "offer_id",
    "posts_min",
    "posts_target",
    "posts_max",
    "primary_cta",
    "next_step",
    "exit_rule",
]

REQUIRED_OFFER_FIELDS = [
    "offer_id",
    "status",
    "can_invite_now",
    "cta_level_max",
    "allowed_cta",
    "delivery_mode",
    "missing_before_public_promo",
]

REQUIRED_TEXT_MARKERS = {
    FUNNEL_OS: [
        "Content ID:",
        "Funnel arc:",
        "Offer readiness:",
        "CTA intensity:",
        "Metric to watch:",
        "Стоп-правила",
    ],
    SLOT_MATRIX: [
        "slot-1-pain",
        "slot-2-diagnosis",
        "slot-3-trust",
        "slot-4-proof",
        "slot-5-b2b",
        "slot-6-seo",
    ],
    FUTURE_BACKLOG: [
        "Postiz",
        "BrightBean Studio",
        "TryPost",
        "LangChain Social Media Agent",
        "Dittofeed",
        "OpenPanel",
        "Keeper.sh",
    ],
    TEN_POST_PLAN: [
        "lead-post-001",
        "lead-post-010",
        "primary-plan-check",
        "content_id",
        "first_touch_channel",
    ],
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        return [], []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _missing_fields(required: list[str], actual: list[str]) -> list[str]:
    return [field for field in required if field not in actual]


def _row_key(row: dict[str, str], *keys: str) -> str:
    parts = [row.get(key, "") for key in keys]
    return " / ".join(part for part in parts if part) or "<unknown>"


def main() -> int:
    pub_fields, pub_rows = _read_csv(PUBLICATION_TRACKER)
    topic_fields, topic_rows = _read_csv(TOPIC_RESPONSE_TRACKER)
    arc_fields, arc_rows = _read_csv(FUNNEL_ARCS)
    offer_fields, offer_rows = _read_csv(OFFER_READINESS)

    offer_ids = {row.get("offer_id", "") for row in offer_rows}
    arc_ids = {row.get("arc_id", "") for row in arc_rows}

    row_issues: list[dict[str, str]] = []
    for row in pub_rows:
        key = _row_key(row, "content_id", "channel")
        if row.get("funnel_arc") not in arc_ids:
            row_issues.append({"row": key, "issue": "unknown_funnel_arc", "value": row.get("funnel_arc", "")})
        if row.get("offer_id") not in offer_ids:
            row_issues.append({"row": key, "issue": "unknown_offer_id", "value": row.get("offer_id", "")})
        for required in ["content_id", "channel", "funnel_stage", "main_cta", "next_bridge", "status"]:
            if not row.get(required):
                row_issues.append({"row": key, "issue": f"empty_{required}", "value": ""})
        try:
            int(row.get("cta_intensity", ""))
        except ValueError:
            row_issues.append({"row": key, "issue": "cta_intensity_not_int", "value": row.get("cta_intensity", "")})

    for row in topic_rows:
        key = _row_key(row, "topic_id", "content_id")
        if row.get("funnel_arc") not in arc_ids:
            row_issues.append({"row": key, "issue": "topic_unknown_funnel_arc", "value": row.get("funnel_arc", "")})
        if not row.get("decision"):
            row_issues.append({"row": key, "issue": "topic_empty_decision", "value": ""})

    missing_text_markers: dict[str, list[str]] = {}
    for path, markers in REQUIRED_TEXT_MARKERS.items():
        text = _read_text(path)
        missing = [marker for marker in markers if marker not in text]
        if missing:
            missing_text_markers[str(path.relative_to(PROJECT_ROOT))] = missing

    report: dict[str, Any] = {
        "generated_at": _utc_now(),
        "status": "OK",
        "external_calls": {
            "redis": False,
            "bitrix24": False,
            "telegram": False,
            "max": False,
            "llm": False,
            "scheduler": False,
            "publisher": False,
            "paid_api": False,
        },
        "files": {
            "publication_tracker_exists": PUBLICATION_TRACKER.exists(),
            "topic_response_tracker_exists": TOPIC_RESPONSE_TRACKER.exists(),
            "funnel_arcs_exists": FUNNEL_ARCS.exists(),
            "offer_readiness_exists": OFFER_READINESS.exists(),
            "slot_matrix_exists": SLOT_MATRIX.exists(),
            "future_backlog_exists": FUTURE_BACKLOG.exists(),
        },
        "counts": {
            "publication_rows": len(pub_rows),
            "topic_response_rows": len(topic_rows),
            "funnel_arc_rows": len(arc_rows),
            "offer_rows": len(offer_rows),
        },
        "missing_fields": {
            "publication_tracker": _missing_fields(REQUIRED_PUBLICATION_FIELDS, pub_fields),
            "topic_response_tracker": _missing_fields(REQUIRED_TOPIC_FIELDS, topic_fields),
            "funnel_arcs": _missing_fields(REQUIRED_FUNNEL_ARC_FIELDS, arc_fields),
            "offer_readiness": _missing_fields(REQUIRED_OFFER_FIELDS, offer_fields),
        },
        "row_issues": row_issues,
        "missing_text_markers": missing_text_markers,
    }

    if any(report["missing_fields"].values()) or row_issues or missing_text_markers or not all(report["files"].values()):
        report["status"] = "FAIL"

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"content_funnel_contract_status={report['status']}")
    print(f"report_path={REPORT_PATH.relative_to(PROJECT_ROOT)}")
    if report["status"] != "OK":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
