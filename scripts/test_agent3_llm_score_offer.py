"""Run one controlled Agent 3 LLM score/offer test.

Default mode is safe dry-run. A real LLM call happens only with --execute.

This test builds one synthetic RawLead and calls only Agent 3 scorer and
offer_gen. It does not touch Redis, Bitrix24, Telegram, IMAP, scheduler, or
mass collection.
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

from agents.agent3_processor.cleaner import is_offtopic  # noqa: E402
from agents.agent3_processor.enricher import enrich  # noqa: E402
from agents.agent3_processor.offer_gen import _COLD_TEMPLATE, generate  # noqa: E402
from agents.agent3_processor.scorer import score  # noqa: E402
from config import settings  # noqa: E402
from shared.models import RawLead  # noqa: E402


REPORT_PATH = PROJECT_ROOT / "data" / "reports" / "agent3_llm_score_offer_test.json"
REPORT_DRY_RUN_PATH = PROJECT_ROOT / "data" / "reports" / "agent3_llm_score_offer_test_dry_run.json"


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
        source="manual_agent3_llm_test",
        source_type="manual_test",
        traffic_channel="manual",
        first_touch_channel="manual",
        last_touch_channel="manual",
        utm_source="agent3_llm_test",
        utm_medium="manual",
        consent_status="not_required",
        flow="B",
        raw_text=(
            "Здравствуйте. Нужна проектная и рабочая документация для "
            "складского комплекса 1200 м2 в Краснодаре. Есть эскиз АР, "
            "нужен подрядчик на КР, КЖ, КМ, старт работ в течение двух "
            "недель. Контакт: test-agent3-llm@example.invalid"
        ),
        contact="test-agent3-llm@example.invalid",
        author_name="Синтетический LLM-тест Agent 3",
        city="Краснодар",
    )


def _base_result(dry_run: bool, raw: RawLead) -> dict[str, Any]:
    provider = settings.LLM_PROVIDER
    return {
        "dry_run": dry_run,
        "test_type": "agent3_llm_score_offer",
        "raw_lead_id_prefix": raw.id[:8],
        "llm_provider": provider,
        "llm_model_analysis": settings.LLM_MODEL_ANALYSIS,
        "llm_model_reply": settings.LLM_MODEL_REPLY,
        "anthropic_api_key_status": _secret_status(settings.ANTHROPIC_API_KEY),
        "openrouter_api_key_status": _secret_status(settings.OPENROUTER_API_KEY),
        "llm_config_status": _llm_config_status(),
        "raw_lead_status": "OK",
        "offtopic_status": "NOT_RUN",
        "enrich_status": "NOT_RUN",
        "llm_score_status": "NOT_RUN",
        "llm_offer_status": "NOT_RUN",
        "score": None,
        "score_reason": None,
        "recommended_action": None,
        "offer_chars": None,
        "offer_preview": None,
        "enriched": None,
        "external_calls": {
            "llm_score": False,
            "llm_offer": False,
            "redis": False,
            "bitrix24": False,
            "telegram_send": False,
            "imap": False,
            "scheduler": False,
        },
        "created_at": _utc_now(),
    }


def _write_report(result: dict[str, Any]) -> Path:
    path = REPORT_DRY_RUN_PATH if result.get("dry_run") else REPORT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def run(execute: bool = False) -> dict[str, Any]:
    raw = build_test_raw_lead()
    dry_run = not execute
    result = _base_result(dry_run=dry_run, raw=raw)

    if dry_run:
        result["offtopic_status"] = "DRY_RUN"
        result["enrich_status"] = "DRY_RUN"
        result["llm_score_status"] = "DRY_RUN"
        result["llm_offer_status"] = "DRY_RUN"
        _write_report(result)
        return result

    try:
        if result["llm_config_status"] != "OK":
            result["llm_score_status"] = "FAILED_CONFIG"
            result["llm_offer_status"] = "NOT_RUN"
            raise RuntimeError(result["llm_config_status"])

        if is_offtopic(raw):
            result["offtopic_status"] = "FAILED_OFFTOPIC"
            result["llm_score_status"] = "NOT_RUN"
            result["llm_offer_status"] = "NOT_RUN"
            raise RuntimeError("Synthetic LLM lead was detected as offtopic")
        result["offtopic_status"] = "OK_NOT_OFFTOPIC"

        enriched = enrich(raw)
        result["enriched"] = enriched
        result["enrich_status"] = "OK"

        result["external_calls"]["llm_score"] = True
        lead_score, score_reason = score(raw, raise_errors=True)
        result["score"] = lead_score
        result["score_reason"] = score_reason
        if score_reason == "ошибка скоринга":
            result["llm_score_status"] = "FAILED"
            result["llm_offer_status"] = "NOT_RUN"
            raise RuntimeError("Agent 3 scorer returned fallback error")
        result["llm_score_status"] = "OK"

        if lead_score not in {"hot", "warm"}:
            result["llm_offer_status"] = "SKIPPED_SCORE_NOT_HOT_WARM"
            raise RuntimeError(f"Expected hot/warm synthetic lead score, got {lead_score}")

        result["external_calls"]["llm_offer"] = True
        offer_text, action = generate(raw, lead_score, enriched, raise_errors=True)
        result["recommended_action"] = action
        result["offer_chars"] = len(offer_text)
        result["offer_preview"] = offer_text[:240]
        if not offer_text.strip():
            result["llm_offer_status"] = "FAILED_EMPTY"
            raise RuntimeError("Agent 3 offer_gen returned empty offer")
        if offer_text == _COLD_TEMPLATE.get(raw.flow or "A"):
            result["llm_offer_status"] = "FAILED_FALLBACK_TEMPLATE"
            raise RuntimeError("Agent 3 offer_gen returned fallback template")
        result["llm_offer_status"] = "OK"

    except Exception as exc:
        result["error_type"] = type(exc).__name__
        result["error"] = str(exc)[:500]

    _write_report(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one controlled Agent 3 LLM score/offer test.")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Make exactly one real scorer call and one real offer call when score is hot/warm.",
    )
    args = parser.parse_args()

    result = run(execute=args.execute)
    for key in [
        "test_type",
        "dry_run",
        "llm_provider",
        "llm_config_status",
        "anthropic_api_key_status",
        "openrouter_api_key_status",
        "offtopic_status",
        "enrich_status",
        "llm_score_status",
        "llm_offer_status",
        "score",
        "recommended_action",
        "offer_chars",
        "raw_lead_id_prefix",
    ]:
        print(f"{key}={result[key]}")
    print(
        "external_calls="
        + ",".join(f"{key}:{value}" for key, value in result["external_calls"].items())
    )
    if result.get("error_type"):
        print(f"error_type={result['error_type']}")
    report_path = REPORT_PATH if args.execute else REPORT_DRY_RUN_PATH
    print(f"report_file={report_path.relative_to(PROJECT_ROOT)}")

    ok = (
        result["llm_score_status"] in {"OK", "DRY_RUN"}
        and result["llm_offer_status"] in {"OK", "DRY_RUN"}
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
