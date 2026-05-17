"""Run one controlled Agent 3 Redis processing test with real LLM.

This test pushes exactly one synthetic RawLead into Redis, calls only
agents.agent3_processor.run(), verifies that one QualifiedLead is produced with
real scorer/offer_gen LLM calls, and then removes that QualifiedLead from
leads:qualified.

It does not call Agent 5, Bitrix24, Telegram, IMAP, scheduler, or mass
collection. If relevant queues already contain data, the script stops before
adding the test lead.
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
from agents.agent3_processor.offer_gen import _COLD_TEMPLATE  # noqa: E402
from config import settings  # noqa: E402
from shared.models import RawLead  # noqa: E402
from shared.redis_client import (  # noqa: E402
    ping,
    pop_qualified,
    pop_raw,
    push_raw,
    queue_sizes,
)


REPORT_PATH = PROJECT_ROOT / "data" / "reports" / "agent3_redis_processing_llm_test.json"
REPORT_DRY_RUN_PATH = PROJECT_ROOT / "data" / "reports" / "agent3_redis_processing_llm_test_dry_run.json"
QUEUE_KEYS = ("raw", "qualified", "outreach", "content_events")


def _utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _secret_status(value: str | None) -> str:
    return "SET" if value else "EMPTY"


def _llm_config_status() -> str:
    provider = settings.LLM_PROVIDER
    if provider in {"dry_run", "none", "disabled"}:
        return "FAILED_PROVIDER_DISABLED"
    if provider == "anthropic":
        return "OK" if settings.ANTHROPIC_API_KEY else "FAILED_ANTHROPIC_API_KEY_EMPTY"
    if provider == "openrouter":
        return "OK" if settings.OPENROUTER_API_KEY else "FAILED_OPENROUTER_API_KEY_EMPTY"
    return "FAILED_UNKNOWN_PROVIDER"


def build_test_raw_lead() -> RawLead:
    return RawLead(
        source="manual_agent3_redis_llm_test",
        source_type="manual_test",
        traffic_channel="manual",
        first_touch_channel="manual",
        last_touch_channel="manual",
        utm_source="agent3_redis_llm_test",
        utm_medium="manual",
        consent_status="not_required",
        flow="B",
        raw_text=(
            "Краснодар. ТЕСТ Agent 3 Redis + LLM. Нужна проектная и "
            "рабочая документация для складского комплекса 1200 м2. "
            "Есть эскиз АР, нужен подрядчик на КР, КЖ, КМ, старт в "
            "течение двух недель. Контакт: test-agent3-redis-llm@example.invalid"
        ),
        contact="test-agent3-redis-llm@example.invalid",
        author_name="ТЕСТ Agent 3 Redis LLM",
        city="Краснодар",
    )


def _queue_blockers(sizes: dict[str, int]) -> dict[str, int]:
    return {key: sizes.get(key, 0) for key in QUEUE_KEYS if sizes.get(key, 0)}


def _write_report(result: dict[str, Any]) -> Path:
    path = REPORT_DRY_RUN_PATH if result.get("dry_run") else REPORT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _base_result(dry_run: bool, raw: RawLead) -> dict[str, Any]:
    return {
        "dry_run": dry_run,
        "test_type": "agent3_redis_processing_llm",
        "raw_lead_id_prefix": raw.id[:8],
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model_analysis": settings.LLM_MODEL_ANALYSIS,
        "llm_model_reply": settings.LLM_MODEL_REPLY,
        "anthropic_api_key_status": _secret_status(settings.ANTHROPIC_API_KEY),
        "openrouter_api_key_status": _secret_status(settings.OPENROUTER_API_KEY),
        "llm_config_status": _llm_config_status(),
        "external_calls": {
            "redis_ping": False,
            "redis_push_raw": False,
            "agent3_run": False,
            "llm_score": False,
            "llm_offer": False,
            "redis_pop_qualified_cleanup": False,
            "bitrix24": False,
            "telegram_send": False,
            "imap": False,
            "scheduler": False,
        },
        "redis_ping_status": "NOT_RUN",
        "queue_guard_status": "NOT_RUN",
        "redis_push_raw_status": "NOT_RUN",
        "agent3_run_status": "NOT_RUN",
        "qualified_output_status": "NOT_RUN",
        "cleanup_status": "NOT_RUN",
        "processed_count": None,
        "qualified_lead_id_prefix": None,
        "qualified_score": None,
        "qualified_score_reason": None,
        "qualified_flow": None,
        "qualified_source": None,
        "qualified_offer_chars": None,
        "qualified_recommended_action": None,
        "queue_sizes_before": None,
        "queue_sizes_after_push": None,
        "queue_sizes_after_run": None,
        "queue_sizes_after_cleanup": None,
        "created_at": _utc_now(),
    }


def run(dry_run: bool = False) -> dict[str, Any]:
    raw = build_test_raw_lead()
    result = _base_result(dry_run=dry_run, raw=raw)

    if dry_run:
        result["redis_ping_status"] = "DRY_RUN"
        result["queue_guard_status"] = "DRY_RUN"
        result["redis_push_raw_status"] = "DRY_RUN"
        result["agent3_run_status"] = "DRY_RUN"
        result["qualified_output_status"] = "DRY_RUN"
        result["cleanup_status"] = "DRY_RUN"
        _write_report(result)
        return result

    if result["llm_config_status"] != "OK":
        result["agent3_run_status"] = "FAILED_CONFIG"
        result["cleanup_status"] = "NOT_NEEDED"
        result["error_type"] = "RuntimeError"
        result["error"] = result["llm_config_status"]
        _write_report(result)
        return result

    original_is_duplicate = agent3_processor.is_duplicate
    original_score = agent3_processor.score
    original_generate = agent3_processor.generate

    def tracked_score(lead: RawLead) -> tuple[str, str]:
        result["external_calls"]["llm_score"] = True
        try:
            return original_score(lead, raise_errors=True)
        except Exception as exc:
            result["llm_score_error_type"] = type(exc).__name__
            result["llm_score_error"] = str(exc)[:500]
            raise

    def tracked_generate(lead: RawLead, lead_score: str, enriched: dict) -> tuple[str, str]:
        if lead_score in {"hot", "warm"}:
            result["external_calls"]["llm_offer"] = True
        try:
            return original_generate(lead, lead_score, enriched, raise_errors=True)
        except Exception as exc:
            result["llm_offer_error_type"] = type(exc).__name__
            result["llm_offer_error"] = str(exc)[:500]
            raise

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
        result["queue_sizes_after_push"] = queue_sizes()

        # Keep duplicate fingerprint storage untouched while still exercising
        # the real Agent 3 Redis, enrichment, score, offer, and queue path.
        agent3_processor.is_duplicate = lambda lead: False
        agent3_processor.score = tracked_score
        agent3_processor.generate = tracked_generate

        result["external_calls"]["agent3_run"] = True
        processed_count = agent3_processor.run()
        result["processed_count"] = processed_count
        result["agent3_run_status"] = "OK" if processed_count == 1 else "FAILED"
        result["queue_sizes_after_run"] = queue_sizes()

        qualified = pop_qualified()
        result["external_calls"]["redis_pop_qualified_cleanup"] = True
        if qualified:
            result["qualified_output_status"] = "OK"
            result["qualified_lead_id_prefix"] = qualified.id[:8]
            result["qualified_score"] = qualified.score
            result["qualified_score_reason"] = qualified.score_reason
            result["qualified_flow"] = qualified.flow
            result["qualified_source"] = qualified.source
            result["qualified_offer_chars"] = len(qualified.offer_text)
            result["qualified_recommended_action"] = qualified.recommended_action
            if qualified.score_reason == "ошибка скоринга":
                result["qualified_output_status"] = "FAILED_SCORE_FALLBACK"
            if qualified.score not in {"hot", "warm"}:
                result["qualified_output_status"] = "FAILED_SCORE_NOT_HOT_WARM"
            if qualified.offer_text in _COLD_TEMPLATE.values():
                result["qualified_output_status"] = "FAILED_OFFER_FALLBACK"
        else:
            result["qualified_output_status"] = "FAILED"

        result["queue_sizes_after_cleanup"] = queue_sizes()
        result["cleanup_status"] = "OK" if result["queue_sizes_after_cleanup"] == before else "CHECK_QUEUE_SIZES"

    except Exception as exc:
        if result["redis_ping_status"] == "FAILED":
            result["agent3_run_status"] = "NOT_RUN"
            result["cleanup_status"] = "NOT_NEEDED"
        else:
            result["agent3_run_status"] = "FAILED"
        result["error_type"] = type(exc).__name__
        result["error"] = str(exc)[:500]
        if result["redis_push_raw_status"] == "OK" or result["external_calls"]["agent3_run"]:
            try:
                pop_raw()
                pop_qualified()
                result["queue_sizes_after_cleanup"] = queue_sizes()
            except Exception as cleanup_exc:
                result["cleanup_error_type"] = type(cleanup_exc).__name__
                result["cleanup_error"] = str(cleanup_exc)[:500]

    finally:
        agent3_processor.is_duplicate = original_is_duplicate
        agent3_processor.score = original_score
        agent3_processor.generate = original_generate

    _write_report(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one Agent 3 Redis processing test with real LLM.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    result = run(dry_run=args.dry_run)
    for key in [
        "test_type",
        "llm_provider",
        "llm_config_status",
        "anthropic_api_key_status",
        "openrouter_api_key_status",
        "redis_ping_status",
        "queue_guard_status",
        "redis_push_raw_status",
        "agent3_run_status",
        "qualified_output_status",
        "cleanup_status",
        "processed_count",
        "qualified_score",
        "qualified_flow",
        "qualified_recommended_action",
        "qualified_offer_chars",
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
    report_path = REPORT_DRY_RUN_PATH if args.dry_run else REPORT_PATH
    print(f"report_file={report_path.relative_to(PROJECT_ROOT)}")

    ok = (
        result["agent3_run_status"] in {"OK", "DRY_RUN"}
        and result["qualified_output_status"] in {"OK", "DRY_RUN"}
        and result["cleanup_status"] in {"OK", "DRY_RUN"}
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
