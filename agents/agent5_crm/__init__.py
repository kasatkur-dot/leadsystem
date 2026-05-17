"""
Агент 5 — CRM-роутер
Читает два потока из Redis:
  1. leads:qualified (QualifiedLead из Агента 3) → Bitrix24 + TG
  2. leads:outreach (OutreachLead из Агента 6) → Bitrix24 + TG
Запускается оркестратором каждые 5 минут.

Ожидаемый конечный результат:
Маршрутизирует квалифицированный лид в Bitrix24, уведомляет менеджера,
фиксирует события контента и готовит базу для аналитики каналов, сделок и ROMI.

Суброли:
- CRM Router: payload для Bitrix24 лида/сделки.
- Notifier: уведомление человека.
- Attribution Agent: first_touch, last_touch, канал, UTM.
- ROMI Reporter: CPL, CAC, profit, ROMI.
- CRM Hygiene Analyst: дубли, пустые поля, слабые карточки.
- Weekly Digest Owner: недельный итог системы позже.

Метрики:
- Каналы в сквозной аналитике: 17 из 17 каналов есть в registry, costs, facts и channel_report.
- Каналы первой волны отслеживаются: 9 из 9 wave_1 каналов есть в отчёте.
- Сквозной CRM-тест закрыт: 1 из 1 — QualifiedLead -> Bitrix24 -> Telegram -> отчёт.
- CRM-цепочка урока 5 покрыта: цель 6 шагов — новый лид, квалификация, КП/лендинг, CRM-карточка, следующий шаг, аналитика.
- Тестовые Bitrix24-создания: 4 успешных теста зафиксированы в локальных отчётах.
- Метрика лектора CR visit->deal: цель 1 из 1, сейчас не закрыта, потому что нет visit_count/visitor_id.
- Защитная метрика: 0 секретов/webhook/tokens в отчётах и 0 реальных клиентских данных в тестах.

Физическая память OKR: этот файл + `docs/agent-okr-and-checker-map.md`.
"""
import uuid
from shared.redis_client import pop_content_event, pop_qualified, pop_outreach
from shared.models import QualifiedLead, OutreachLead
from shared.logger import get_logger
from agents.agent5_crm.bitrix import create_lead
from agents.agent5_crm.notifier import notify

log = get_logger("agent5_crm")


def _outreach_to_qualified(lead: OutreachLead) -> QualifiedLead:
    """Конвертирует OutreachLead в QualifiedLead для единого пути в Bitrix24."""
    return QualifiedLead(
        id=str(uuid.uuid4()),
        raw_lead_id=lead.id,
        source=f"outreach_{lead.platform}",
        flow=lead.flow or "A",
        contact=lead.contact,
        contact_type="telegram" if (lead.contact or "").startswith("@") else None,
        score="warm",  # минимум warm — человек уже ответил на наш аутрич
        score_reason=f"Ответил на аутрич ВПП в {lead.platform}: «{lead.their_response[:100]}»",
        offer_text=(
            f"Ответил на наш аутрич в чате {lead.chat_name}.\n"
            f"Наш ответ: {lead.our_reply}\n"
            f"Его ответ: {lead.their_response}"
        ),
        recommended_action="написать в ЛС в течение часа",
        source_type=lead.source_type,
        traffic_channel=lead.traffic_channel,
        first_touch_channel=lead.first_touch_channel or lead.platform,
        last_touch_channel=lead.last_touch_channel or lead.platform,
        consent_status=lead.consent_status,
        raw_text=f"Оригинальный пост: {lead.original_post}\nНаш аутрич: {lead.our_reply}\nОтвет: {lead.their_response}",
    )


def run() -> int:
    """Обрабатывает обе очереди лидов. Возвращает суммарное кол-во переданных в CRM."""
    count = 0

    # Поток 0 — события опубликованного контента (Агент 4)
    while True:
        event = pop_content_event()
        if not event:
            break
        log.info(
            "content_published | channel={} | type={} | topic={} | post_id={} | lead_id={}".format(
                event.get("channel"),
                event.get("content_type"),
                event.get("topic"),
                event.get("post_id"),
                event.get("lead_id"),
            )
        )

    # Поток 1 — квалифицированные лиды (Агент 3)
    while True:
        lead = pop_qualified()
        if not lead:
            break
        try:
            bitrix_id = create_lead(lead)
            notify(lead)
            count += 1
            log.info(f"qualified лид в CRM | bitrix_id={bitrix_id} | score={lead.score} | {lead.id[:8]}")
        except Exception as e:
            log.error(f"ошибка CRM qualified | lead={lead.id[:8]} | {e}")

    # Поток 2 — аутрич-лиды (Агент 6)
    while True:
        raw = pop_outreach()
        if not raw:
            break
        try:
            outreach_lead = OutreachLead.model_validate(raw)
            qualified = _outreach_to_qualified(outreach_lead)
            bitrix_id = create_lead(qualified)
            notify(qualified)
            count += 1
            log.info(f"outreach лид в CRM | bitrix_id={bitrix_id} | {outreach_lead.platform} | {outreach_lead.id[:8]}")
        except Exception as e:
            log.error(f"ошибка CRM outreach | {e}")

    if count:
        log.info(f"итого передано в CRM: {count}")
    return count
