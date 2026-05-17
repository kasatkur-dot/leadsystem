"""
Агент 3 — Процессор лидов
Пайплайн: cleaner → enricher → scorer → offer_gen → push_qualified → Агент 5
Запускается оркестратором каждые 5 минут.

Ожидаемый конечный результат:
Превращает `RawLead` из Redis `leads:raw` в понятный `QualifiedLead`:
поток A/B, контакт, город, объект, score, причина score, оффер и следующий шаг.

Суброли:
- Cleaner: шум, мусор, оффтопик.
- Enricher: город, тип объекта, площадь, контакт.
- Scorer: hot/warm/cold/off и `score_reason`.
- Offer/Next-Step Architect: оффер и следующий шаг.
- QA Classifier: проверка завышенного score.

Метрики:
- Сквозной тест лида обработан: 1 из 1 тестов закрыт по маршруту RawLead -> QualifiedLead -> Agent 5.
- Покрытие первой волны источников: цель 9 из 9 тестовых лидов, по одному на каждый wave_1 канал.
- Режимы скоринга проверены: 2 из 2 — dry_run и настоящий LLM-тест.
- CRM-handoff проверен: 1 из 1 — Agent 3 передал QualifiedLead в Agent 5.
- Категории score проверены: цель 4 из 4 — hot, warm, cold, off; сейчас доказан минимум hot.
- Защитная метрика: доля ошибочных hot-лидов должна быть не выше 10% после появления реальной выборки.

Физическая память OKR: этот файл + `docs/agent-okr-and-checker-map.md`.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from shared.models import RawLead, QualifiedLead
from shared.redis_client import pop_raw, push_qualified
from shared.logger import get_logger

from agents.agent3_processor.cleaner import is_duplicate, is_offtopic
from agents.agent3_processor.enricher import enrich
from agents.agent3_processor.scorer import score
from agents.agent3_processor.offer_gen import generate

log = get_logger("agent3_processor")


def _process_one(lead: RawLead) -> QualifiedLead | None:
    # 1. Дедупликация
    if is_duplicate(lead):
        log.debug(f"дубль пропущен | {lead.id[:8]}")
        return None

    # 2. Фильтр нецелевых (без Claude)
    if is_offtopic(lead):
        log.info(f"нецелевой | {lead.id[:8]} | {lead.raw_text[:60]}")
        return None

    # 3. Определяем поток если не задан
    flow = lead.flow
    if not flow:
        from config.settings import KEYWORDS_FLOW_B
        flow = "B" if any(kw in lead.raw_text.lower() for kw in KEYWORDS_FLOW_B) else "A"

    lead_with_flow = lead.model_copy(update={"flow": flow})

    # 4. Обогащение (regex, без Claude)
    enriched = enrich(lead_with_flow)

    # 5. Скоринг (Claude API)
    lead_score, score_reason = score(lead_with_flow)

    # 6. Оффер (Claude API, только для hot/warm)
    offer_text, recommended_action = generate(lead_with_flow, lead_score, enriched)

    qualified = QualifiedLead(
        id=str(uuid.uuid4()),
        raw_lead_id=lead.id,
        source=lead.source,
        flow=flow,
        contact=enriched.get("contact") or lead.contact,
        contact_type=enriched.get("contact_type"),
        company_name=lead.author_name,
        city=enriched.get("city") or lead.city,
        object_type=enriched.get("object_type"),
        area_m2=enriched.get("area_m2"),
        score=lead_score,
        score_reason=score_reason,
        offer_text=offer_text,
        recommended_action=recommended_action,
        source_url=lead.source_url,
        source_type=lead.source_type,
        traffic_channel=lead.traffic_channel,
        first_touch_channel=lead.first_touch_channel,
        last_touch_channel=lead.last_touch_channel,
        utm_source=lead.utm_source,
        utm_medium=lead.utm_medium,
        utm_campaign=lead.utm_campaign,
        landing_page=lead.landing_page,
        lead_magnet_path=lead.lead_magnet_path,
        consent_status=lead.consent_status,
        raw_text=lead.raw_text,
        processed_at=datetime.utcnow(),
    )
    return qualified


def run() -> int:
    """Обрабатывает все лиды в очереди raw. Возвращает кол-во обработанных."""
    processed = 0
    while True:
        lead = pop_raw()
        if not lead:
            break
        try:
            qualified = _process_one(lead)
            if qualified:
                push_qualified(qualified)
                log.info(f"→ qualified [{qualified.score}] | {qualified.source} | {qualified.id[:8]}")
                processed += 1
        except Exception as e:
            log.error(f"ошибка обработки лида {lead.id[:8]}: {e}")

    if processed:
        log.info(f"итого обработано: {processed}")
    return processed
