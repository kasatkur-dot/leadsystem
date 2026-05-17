"""Safe local dry-run for one synthetic lead.

This script intentionally avoids Redis, LLM calls, Bitrix24, IMAP, Telegram,
and the scheduler. It checks that the local lead models and lightweight
processing steps can build one QualifiedLead.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
import sys
import uuid

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from agents.agent3_processor.cleaner import is_offtopic
from agents.agent3_processor.enricher import enrich
from shared.models import QualifiedLead, RawLead


REPORT_PATH = PROJECT_ROOT / "data" / "reports" / "synthetic_lead_dry_run.json"


def _local_score(lead: RawLead, enriched: dict) -> tuple[str, str]:
    has_contact = bool(enriched.get("contact") or lead.contact)
    has_object = bool(enriched.get("object_type"))
    has_area = bool(enriched.get("area_m2"))

    if has_contact and has_object and has_area:
        return "hot", "dry-run: есть контакт, тип объекта и площадь"
    if has_contact and has_object:
        return "warm", "dry-run: есть контакт и понятный тип объекта"
    return "cold", "dry-run: данных мало, нужен уточняющий вопрос"


def _local_offer(lead: RawLead, score: str, enriched: dict) -> tuple[str, str]:
    if score == "hot":
        action = "позвонить сегодня"
    elif score == "warm":
        action = "написать в течение дня"
    else:
        action = "отправить при возможности"

    object_type = enriched.get("object_type") or "объект"
    city = enriched.get("city") or lead.city or "город не указан"
    offer = (
        f"Dry-run оффер: уточнить исходные данные по объекту '{object_type}' "
        f"в городе '{city}' и предложить короткий созвон по составу работ."
    )
    return offer, action


def build_synthetic_lead() -> RawLead:
    return RawLead(
        source="manual_synthetic_dry_run",
        source_type="manual_test",
        traffic_channel="manual",
        first_touch_channel="manual",
        last_touch_channel="manual",
        utm_source="dry_run",
        utm_medium="manual",
        consent_status="not_required",
        flow="B",
        raw_text=(
            "Краснодар. Нужна проектная и рабочая документация для склада "
            "площадью 1200 кв. м. Интересует КР/КЖ/КМ и сопровождение "
            "до экспертизы. Контакт для теста: test@example.com"
        ),
        contact="test@example.com",
        author_name="Синтетический тестовый лид",
        city="Краснодар",
    )


def build_qualified_lead() -> tuple[RawLead, QualifiedLead, dict]:
    raw = build_synthetic_lead()
    off_topic = is_offtopic(raw)
    if off_topic:
        raise RuntimeError("Синтетический лид ошибочно определён как нецелевой")

    enriched = enrich(raw)
    score, reason = _local_score(raw, enriched)
    offer, action = _local_offer(raw, score, enriched)

    qualified = QualifiedLead(
        id=str(uuid.uuid4()),
        raw_lead_id=raw.id,
        source=raw.source,
        flow=raw.flow or "B",
        contact=enriched.get("contact") or raw.contact,
        contact_type=enriched.get("contact_type"),
        company_name=raw.author_name,
        city=enriched.get("city") or raw.city,
        object_type=enriched.get("object_type"),
        area_m2=enriched.get("area_m2"),
        score=score,
        score_reason=reason,
        offer_text=offer,
        recommended_action=action,
        source_url=raw.source_url,
        source_type=raw.source_type,
        traffic_channel=raw.traffic_channel,
        first_touch_channel=raw.first_touch_channel,
        last_touch_channel=raw.last_touch_channel,
        utm_source=raw.utm_source,
        utm_medium=raw.utm_medium,
        utm_campaign=raw.utm_campaign,
        landing_page=raw.landing_page,
        lead_magnet_path=raw.lead_magnet_path,
        consent_status=raw.consent_status,
        raw_text=raw.raw_text,
        processed_at=datetime.utcnow(),
    )
    return raw, qualified, enriched


def run() -> dict:
    raw, qualified, enriched = build_qualified_lead()

    result = {
        "dry_run": True,
        "external_calls": {
            "redis": False,
            "llm": False,
            "bitrix24": False,
            "telegram_send": False,
            "imap": False,
            "scheduler": False,
        },
        "raw_lead_status": "OK",
        "offtopic_status": "OK_NOT_OFFTOPIC",
        "enriched_fields": sorted(enriched.keys()),
        "qualified_lead_status": "OK",
        "score": qualified.score,
        "recommended_action": qualified.recommended_action,
        "flow": qualified.flow,
        "source": qualified.source,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    result = run()
    for key, value in result.items():
        if isinstance(value, dict):
            compact = ",".join(f"{k}:{v}" for k, v in value.items())
            print(f"{key}={compact}")
        elif isinstance(value, list):
            print(f"{key}={','.join(value)}")
        else:
            print(f"{key}={value}")
    print(f"report_file={REPORT_PATH.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
