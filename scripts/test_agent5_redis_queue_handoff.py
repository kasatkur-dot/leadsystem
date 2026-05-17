"""Run one controlled Agent 5 Redis queue handoff test.

This test pushes exactly one synthetic QualifiedLead into Redis and then calls
only agents.agent5_crm.run().

It does not touch IMAP, LLM APIs, scheduler, mass collection, or real
publications. If Agent 5 queues already contain data, the script stops before
adding the test lead.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
import sys
import uuid
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import agents.agent5_crm as agent5_crm  # noqa: E402
from agents.agent5_crm.bitrix import build_lead_fields  # noqa: E402
from agents.agent5_crm.notifier import build_message  # noqa: E402
from shared.models import QualifiedLead  # noqa: E402
from shared.redis_client import ping, push_qualified, queue_sizes  # noqa: E402


REPORT_BASENAME = "agent5_redis_queue_handoff_test"
AGENT5_QUEUE_KEYS = ("qualified", "outreach", "content_events")


def _utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _report_path(dry_run: bool = False) -> Path:
    suffix = "_dry_run" if dry_run else ""
    return PROJECT_ROOT / "data" / "reports" / f"{REPORT_BASENAME}{suffix}.json"


def build_test_lead() -> QualifiedLead:
    return QualifiedLead(
        id=str(uuid.uuid4()),
        raw_lead_id=str(uuid.uuid4()),
        source="tender_email",
        flow="B",
        contact="test-agent5-redis@example.invalid",
        contact_type="email",
        company_name="ТЕСТ Agent 5 Redis queue — закрыть после проверки",
        city="Краснодар",
        object_type="склад",
        area_m2=1200,
        score="hot",
        score_reason=(
            "ТЕСТ: проверяем путь Redis leads:qualified -> agents.agent5_crm.run() "
            "-> Bitrix24 -> Telegram."
        ),
        offer_text=(
            "ТЕСТ: это не реальный лид. Проверяем только один безопасный "
            "Redis-queue handoff Agent 5."
        ),
        recommended_action="ничего не делать, это тест",
        source_type="manual_test",
        traffic_channel="manual",
        first_touch_channel="manual",
        last_touch_channel="manual",
        utm_source="agent5_redis_queue_test",
        utm_medium="manual",
        consent_status="not_required",
        raw_text=(
            "ТЕСТ Agent 5 Redis queue handoff. Это не реальный клиент. "
            "Проверяем один элемент в Redis-очереди leads:qualified."
        ),
    )


def _queue_blockers(sizes: dict[str, int]) -> dict[str, int]:
    return {key: sizes.get(key, 0) for key in AGENT5_QUEUE_KEYS if sizes.get(key, 0)}


def _write_report(result: dict[str, Any]) -> Path:
    report_path = _report_path(dry_run=bool(result.get("dry_run")))
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report_path


def run(dry_run: bool = False) -> dict[str, Any]:
    lead = build_test_lead()
    fields = build_lead_fields(lead)
    message = build_message(lead)

    result: dict[str, Any] = {
        "dry_run": dry_run,
        "test_type": "agent5_redis_queue_handoff",
        "lead_id_prefix": lead.id[:8],
        "external_calls": {
            "redis_ping": False,
            "redis_push": False,
            "agent5_run": False,
            "bitrix24_attempted": False,
            "bitrix24_created": False,
            "telegram_attempted": False,
            "telegram_send": False,
            "llm": False,
            "imap": False,
            "scheduler": False,
        },
        "redis_ping_status": "NOT_RUN",
        "queue_guard_status": "NOT_RUN",
        "redis_push_status": "NOT_RUN",
        "agent5_run_status": "NOT_RUN",
        "bitrix_payload_status": "OK",
        "telegram_payload_status": "OK",
        "bitrix_send_status": "NOT_RUN",
        "telegram_send_status": "NOT_RUN",
        "bitrix_method": "crm.lead.add",
        "bitrix_id": None,
        "telegram_message_chars": len(message),
        "title": fields.get("TITLE"),
        "name": fields.get("NAME"),
        "queue_sizes_before": None,
        "queue_sizes_after_push": None,
        "queue_sizes_after_run": None,
        "processed_count": None,
        "created_at": _utc_now(),
    }

    if dry_run:
        result["redis_ping_status"] = "DRY_RUN"
        result["queue_guard_status"] = "DRY_RUN"
        result["redis_push_status"] = "DRY_RUN"
        result["agent5_run_status"] = "DRY_RUN"
        result["bitrix_send_status"] = "DRY_RUN"
        result["telegram_send_status"] = "DRY_RUN"
        _write_report(result)
        return result

    try:
        result["external_calls"]["redis_ping"] = True
        redis_ok = ping()
        result["redis_ping_status"] = "OK" if redis_ok else "FAILED"
        if not redis_ok:
            raise RuntimeError("Redis ping failed")

        before = queue_sizes()
        result["queue_sizes_before"] = before
        blockers = _queue_blockers(before)
        if blockers:
            result["queue_guard_status"] = "ABORTED_NONEMPTY_AGENT5_QUEUE"
            result["queue_blockers"] = blockers
            _write_report(result)
            return result
        result["queue_guard_status"] = "OK"

        push_qualified(lead)
        result["external_calls"]["redis_push"] = True
        result["redis_push_status"] = "OK"
        result["queue_sizes_after_push"] = queue_sizes()

        captured_bitrix_ids: list[str | None] = []
        captured_telegram: list[bool] = []
        original_create_lead = agent5_crm.create_lead
        original_notify = agent5_crm.notify

        def tracked_create_lead(qualified: QualifiedLead) -> str | None:
            bitrix_id = original_create_lead(qualified)
            captured_bitrix_ids.append(bitrix_id)
            return bitrix_id

        def tracked_notify(qualified: QualifiedLead) -> bool:
            sent = original_notify(qualified)
            captured_telegram.append(sent)
            return sent

        try:
            agent5_crm.create_lead = tracked_create_lead
            agent5_crm.notify = tracked_notify
            result["external_calls"]["agent5_run"] = True
            processed_count = agent5_crm.run()
        finally:
            agent5_crm.create_lead = original_create_lead
            agent5_crm.notify = original_notify

        result["processed_count"] = processed_count
        result["agent5_run_status"] = "OK" if processed_count == 1 else "FAILED"
        result["queue_sizes_after_run"] = queue_sizes()

        bitrix_id = captured_bitrix_ids[0] if captured_bitrix_ids else None
        telegram_ok = captured_telegram[0] if captured_telegram else False

        result["external_calls"]["bitrix24_attempted"] = bool(captured_bitrix_ids)
        result["external_calls"]["bitrix24_created"] = bool(bitrix_id)
        result["external_calls"]["telegram_attempted"] = bool(captured_telegram)
        result["external_calls"]["telegram_send"] = telegram_ok
        result["bitrix_id"] = bitrix_id
        result["bitrix_send_status"] = "OK" if bitrix_id else "FAILED"
        result["telegram_send_status"] = "OK" if telegram_ok else "FAILED"

    except Exception as exc:
        result["agent5_run_status"] = "FAILED"
        result["error_type"] = type(exc).__name__
        result["error"] = str(exc)[:500]

    _write_report(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one Agent 5 Redis queue handoff test.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    result = run(dry_run=args.dry_run)
    for key in [
        "test_type",
        "redis_ping_status",
        "queue_guard_status",
        "redis_push_status",
        "agent5_run_status",
        "bitrix_payload_status",
        "bitrix_send_status",
        "telegram_payload_status",
        "telegram_send_status",
        "bitrix_method",
        "bitrix_id",
        "processed_count",
        "lead_id_prefix",
    ]:
        print(f"{key}={result[key]}")
    print(
        "external_calls="
        + ",".join(f"{key}:{value}" for key, value in result["external_calls"].items())
    )
    if result.get("queue_blockers"):
        print(f"queue_blockers={json.dumps(result['queue_blockers'], ensure_ascii=False)}")
    if result.get("error_type"):
        print(f"error_type={result['error_type']}")
    print(f"report_file={_report_path(dry_run=args.dry_run).relative_to(PROJECT_ROOT)}")
    ok = (
        result["agent5_run_status"] in {"OK", "DRY_RUN"}
        and result["bitrix_send_status"] in {"OK", "DRY_RUN"}
        and result["telegram_send_status"] in {"OK", "DRY_RUN"}
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
