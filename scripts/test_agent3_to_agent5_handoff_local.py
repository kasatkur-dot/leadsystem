"""Run one controlled RawLead -> Agent 3 -> Agent 5 handoff test.

This script pushes exactly one synthetic RawLead into Redis, runs
agents.agent3_processor.run() with local score/offer functions, then runs only
agents.agent5_crm.run().

It does not call LLM APIs, IMAP, scheduler, mass collection, or real
publications. It does call Bitrix24 and Telegram during the real run because
that is the Agent 5 handoff being tested. If relevant queues already contain
data, the script stops before adding the test lead.
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

import agents.agent3_processor as agent3_processor  # noqa: E402
import agents.agent5_crm as agent5_crm  # noqa: E402
from shared.models import QualifiedLead, RawLead  # noqa: E402
from shared.redis_client import ping, pop_qualified, pop_raw, push_raw, queue_sizes  # noqa: E402


REPORT_BASENAME = "agent3_to_agent5_handoff_local_test"
QUEUE_KEYS = ("raw", "qualified", "outreach", "content_events")


def _utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _report_path(dry_run: bool = False) -> Path:
    suffix = "_dry_run" if dry_run else ""
    return PROJECT_ROOT / "data" / "reports" / f"{REPORT_BASENAME}{suffix}.json"


def build_test_raw_lead() -> RawLead:
    return RawLead(
        source="tender_email",
        source_type="manual_test",
        traffic_channel="manual",
        first_touch_channel="manual",
        last_touch_channel="manual",
        utm_source="agent3_to_agent5_test",
        utm_medium="manual",
        consent_status="not_required",
        flow="B",
        raw_text=(
            "Краснодар. ТЕСТ Agent 3 -> Agent 5 handoff. Нужна проектная "
            "и рабочая документация для склада 1200 м2: КР, КЖ, КМ. "
            "Контакт для теста: test-agent3-agent5@example.invalid"
        ),
        contact="test-agent3-agent5@example.invalid",
        author_name="ТЕСТ Agent 3 to Agent 5 — закрыть после проверки",
        city="Краснодар",
    )


def _queue_blockers(sizes: dict[str, int]) -> dict[str, int]:
    return {key: sizes.get(key, 0) for key in QUEUE_KEYS if sizes.get(key, 0)}


def _write_report(result: dict[str, Any]) -> Path:
    report_path = _report_path(dry_run=bool(result.get("dry_run")))
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report_path


def _local_score(lead: RawLead) -> tuple[str, str]:
    return (
        "hot",
        "local test: есть город, объект, площадь, контакт и разделы КР/КЖ/КМ",
    )


def _local_generate(lead: RawLead, score: str, enriched: dict) -> tuple[str, str]:
    offer = (
        "Local test offer: уточнить исходные данные по складу, проверить "
        "состав разделов КР/КЖ/КМ и назначить короткий созвон. "
        "Это тест, не реальный лид."
    )
    return offer, "ничего не делать, это тест"


def _cleanup_possible_test_items() -> None:
    pop_raw()
    pop_qualified()


def run(dry_run: bool = False) -> dict[str, Any]:
    raw = build_test_raw_lead()
    result: dict[str, Any] = {
        "dry_run": dry_run,
        "test_type": "agent3_to_agent5_handoff_local",
        "raw_lead_id_prefix": raw.id[:8],
        "qualified_lead_id_prefix": None,
        "external_calls": {
            "redis_ping": False,
            "redis_push_raw": False,
            "agent3_run": False,
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
        "redis_push_raw_status": "NOT_RUN",
        "agent3_run_status": "NOT_RUN",
        "agent5_run_status": "NOT_RUN",
        "bitrix_send_status": "NOT_RUN",
        "telegram_send_status": "NOT_RUN",
        "qualified_output_status": "NOT_RUN",
        "cleanup_status": "NOT_RUN",
        "agent3_processed_count": None,
        "agent5_processed_count": None,
        "qualified_score": None,
        "qualified_flow": None,
        "qualified_source": None,
        "bitrix_id": None,
        "queue_sizes_before": None,
        "queue_sizes_after_raw_push": None,
        "queue_sizes_after_agent3": None,
        "queue_sizes_after_agent5": None,
        "queue_sizes_after_cleanup": None,
        "created_at": _utc_now(),
    }

    if dry_run:
        for key in [
            "redis_ping_status",
            "queue_guard_status",
            "redis_push_raw_status",
            "agent3_run_status",
            "agent5_run_status",
            "bitrix_send_status",
            "telegram_send_status",
            "qualified_output_status",
            "cleanup_status",
        ]:
            result[key] = "DRY_RUN"
        _write_report(result)
        return result

    original_is_duplicate = agent3_processor.is_duplicate
    original_score = agent3_processor.score
    original_generate = agent3_processor.generate
    original_create_lead = agent5_crm.create_lead
    original_notify = agent5_crm.notify

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
            result["queue_guard_status"] = "ABORTED_NONEMPTY_QUEUE"
            result["queue_blockers"] = blockers
            _write_report(result)
            return result
        result["queue_guard_status"] = "OK"

        push_raw(raw)
        result["external_calls"]["redis_push_raw"] = True
        result["redis_push_raw_status"] = "OK"
        result["queue_sizes_after_raw_push"] = queue_sizes()

        agent3_processor.is_duplicate = lambda lead: False
        agent3_processor.score = _local_score
        agent3_processor.generate = _local_generate

        result["external_calls"]["agent3_run"] = True
        agent3_count = agent3_processor.run()
        result["agent3_processed_count"] = agent3_count
        result["agent3_run_status"] = "OK" if agent3_count == 1 else "FAILED"
        result["queue_sizes_after_agent3"] = queue_sizes()

        captured_bitrix_ids: list[str | None] = []
        captured_telegram: list[bool] = []
        captured_qualified: list[QualifiedLead] = []

        def tracked_create_lead(qualified: QualifiedLead) -> str | None:
            captured_qualified.append(qualified)
            bitrix_id = original_create_lead(qualified)
            captured_bitrix_ids.append(bitrix_id)
            return bitrix_id

        def tracked_notify(qualified: QualifiedLead) -> bool:
            sent = original_notify(qualified)
            captured_telegram.append(sent)
            return sent

        agent5_crm.create_lead = tracked_create_lead
        agent5_crm.notify = tracked_notify

        result["external_calls"]["agent5_run"] = True
        agent5_count = agent5_crm.run()
        result["agent5_processed_count"] = agent5_count
        result["agent5_run_status"] = "OK" if agent5_count == 1 else "FAILED"
        result["queue_sizes_after_agent5"] = queue_sizes()

        qualified = captured_qualified[0] if captured_qualified else None
        if qualified:
            result["qualified_output_status"] = "OK"
            result["qualified_lead_id_prefix"] = qualified.id[:8]
            result["qualified_score"] = qualified.score
            result["qualified_flow"] = qualified.flow
            result["qualified_source"] = qualified.source
        else:
            result["qualified_output_status"] = "FAILED"

        bitrix_id = captured_bitrix_ids[0] if captured_bitrix_ids else None
        telegram_ok = captured_telegram[0] if captured_telegram else False
        result["bitrix_id"] = bitrix_id
        result["external_calls"]["bitrix24_attempted"] = bool(captured_bitrix_ids)
        result["external_calls"]["bitrix24_created"] = bool(bitrix_id)
        result["external_calls"]["telegram_attempted"] = bool(captured_telegram)
        result["external_calls"]["telegram_send"] = telegram_ok
        result["bitrix_send_status"] = "OK" if bitrix_id else "FAILED"
        result["telegram_send_status"] = "OK" if telegram_ok else "FAILED"

        result["queue_sizes_after_cleanup"] = queue_sizes()
        result["cleanup_status"] = (
            "OK" if result["queue_sizes_after_cleanup"] == before else "CHECK_QUEUE_SIZES"
        )

    except Exception as exc:
        if result["redis_ping_status"] == "FAILED":
            result["agent3_run_status"] = "NOT_RUN"
            result["agent5_run_status"] = "NOT_RUN"
            result["cleanup_status"] = "NOT_NEEDED"
        else:
            result["cleanup_status"] = "ATTEMPTED"
            try:
                _cleanup_possible_test_items()
                result["queue_sizes_after_cleanup"] = queue_sizes()
            except Exception as cleanup_exc:
                result["cleanup_error_type"] = type(cleanup_exc).__name__
                result["cleanup_error"] = str(cleanup_exc)[:500]
        result["error_type"] = type(exc).__name__
        result["error"] = str(exc)[:500]

    finally:
        agent3_processor.is_duplicate = original_is_duplicate
        agent3_processor.score = original_score
        agent3_processor.generate = original_generate
        agent5_crm.create_lead = original_create_lead
        agent5_crm.notify = original_notify

    _write_report(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one RawLead -> Agent 3 -> Agent 5 handoff test without LLM.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    result = run(dry_run=args.dry_run)
    for key in [
        "test_type",
        "redis_ping_status",
        "queue_guard_status",
        "redis_push_raw_status",
        "agent3_run_status",
        "agent5_run_status",
        "qualified_output_status",
        "bitrix_send_status",
        "telegram_send_status",
        "cleanup_status",
        "agent3_processed_count",
        "agent5_processed_count",
        "qualified_score",
        "qualified_flow",
        "bitrix_id",
        "raw_lead_id_prefix",
        "qualified_lead_id_prefix",
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
        result["agent3_run_status"] in {"OK", "DRY_RUN"}
        and result["agent5_run_status"] in {"OK", "DRY_RUN"}
        and result["bitrix_send_status"] in {"OK", "DRY_RUN"}
        and result["telegram_send_status"] in {"OK", "DRY_RUN"}
        and result["cleanup_status"] in {"OK", "DRY_RUN"}
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
