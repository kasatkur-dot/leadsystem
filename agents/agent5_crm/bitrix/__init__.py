"""
Агент 5 — bitrix
Создаёт и обновляет карточки лидов в Bitrix24 CRM.
Использует: fast-bitrix24 (104 stars, MIT, российский автор).
"""
from __future__ import annotations

from fast_bitrix24 import Bitrix

from shared.models import QualifiedLead
from shared.logger import get_logger
from config.settings import BITRIX24_WEBHOOK_URL

log = get_logger("bitrix")

# Инициализируем клиент один раз при импорте
_bx: Bitrix | None = None


def _get_client() -> Bitrix:
    global _bx
    if _bx is None:
        if not BITRIX24_WEBHOOK_URL:
            raise RuntimeError("BITRIX24_WEBHOOK_URL не задан в .env")
        _bx = Bitrix(BITRIX24_WEBHOOK_URL)
    return _bx


# Маппинг нашего скора на приоритет Bitrix24
_PRIORITY = {"hot": "HIGH", "warm": "NORMAL", "cold": "LOW", "off": "LOW"}

# Маппинг источника на SOURCE_ID Bitrix24
_SOURCE = {
    "tender_email": "EMAIL",
    "avito": "WEB",
    "profi": "WEB",
    "tg_chat": "SOCIAL",
    "vk": "SOCIAL",
    "hh": "RECOMMENDATION",
    "yandex_services": "WEB",
    "hunter_tg": "SOCIAL",
    "hunter_vk": "SOCIAL",
    "yandex_direct": "WEB",
    "google_ads": "WEB",
    "vk_ads": "WEB",
    "meta_ads": "WEB",
    "telegram_ads": "WEB",
    "dzen_rsy": "WEB",
    "influencer_tg": "WEB",
    "seo_organic": "WEB",
    "referral": "RECOMMENDATION",
    "outbound": "OTHER",
    "outreach_telegram": "SOCIAL",
    "outreach_vk": "SOCIAL",
    "outreach_forum": "OTHER",
    "outreach_max": "SOCIAL",
    "outreach_tenchat": "SOCIAL",
    "outreach_yandex_q": "WEB",
    "outreach_email": "EMAIL",
}


def _analytics_comment(lead: QualifiedLead) -> str:
    """Короткий блок аналитики, чтобы не потерять источник даже без custom fields."""
    rows = [
        ("Источник", lead.source),
        ("Тип источника", lead.source_type),
        ("Канал трафика", lead.traffic_channel),
        ("Первое касание", lead.first_touch_channel),
        ("Последнее касание", lead.last_touch_channel),
        ("UTM source", lead.utm_source),
        ("UTM medium", lead.utm_medium),
        ("UTM campaign", lead.utm_campaign),
        ("Лендинг", lead.landing_page),
        ("Лид-магнит", lead.lead_magnet_path),
        ("Согласие/контекст", lead.consent_status),
    ]
    filled = [f"{label}: {value}" for label, value in rows if value]
    return "\n".join(filled) if filled else f"Источник: {lead.source}"


def build_lead_fields(lead: QualifiedLead) -> dict:
    """Собрать legacy lead-поля Bitrix24 без отправки API-запроса.

    Новый сайтовый MVP использует `deal_payload_builder` и `crm.deal.add`.
    Этот путь оставлен для старых тестов, поэтому не пишет несуществующие
    пользовательские поля лида.
    """
    title = f"[{lead.flow}] {lead.source.upper()} — {lead.score.upper()} | {lead.city or 'город не указан'}"
    display_name = lead.company_name or lead.object_type or f"Лид из {lead.source}"

    fields = {
        "TITLE": title,
        "NAME": display_name,
        "COMMENTS": (
            f"Скор: {lead.score} — {lead.score_reason}\n\n"
            f"Flow: {lead.flow}\n\n"
            f"Тип объекта: {lead.object_type or 'не указан'}\n\n"
            f"Оффер: {lead.offer_text}\n\n"
            f"Действие: {lead.recommended_action}\n\n"
            f"Сквозная аналитика:\n{_analytics_comment(lead)}\n\n"
            f"Ссылка/источник: {lead.source_url or lead.source}\n\n"
            f"Текст лида:\n{lead.raw_text[:1000]}"
        ),
        "SOURCE_ID": _SOURCE.get(lead.source, "WEB"),
        "PRIORITY": _PRIORITY.get(lead.score, "NORMAL"),
    }

    if lead.contact:
        if lead.contact_type == "phone":
            fields["PHONE"] = [{"VALUE": lead.contact, "VALUE_TYPE": "WORK"}]
        elif lead.contact_type == "email":
            fields["EMAIL"] = [{"VALUE": lead.contact, "VALUE_TYPE": "WORK"}]
        else:
            fields["IM"] = [{"VALUE": lead.contact, "VALUE_TYPE": "TELEGRAM"}]

    if lead.company_name:
        fields["COMPANY_TITLE"] = lead.company_name
    if lead.city:
        fields["ADDRESS_CITY"] = lead.city
    return fields


def create_lead(lead: QualifiedLead) -> str | None:
    """Создать лид в Bitrix24. Возвращает ID созданного лида или None при ошибке."""
    try:
        bx = _get_client()
        fields = build_lead_fields(lead)

        result = bx.call("crm.lead.add", {"fields": fields})
        bitrix_id = str(result)
        log.info(f"создан лид #{bitrix_id} | {lead.score} | {lead.source} | {lead.id[:8]}")
        return bitrix_id

    except Exception as e:
        log.error(f"create_lead ошибка: {e} | lead_id={lead.id[:8]}")
        return None


def add_note(bitrix_id: str, text: str) -> bool:
    """Добавить комментарий к лиду в Bitrix24."""
    try:
        bx = _get_client()
        bx.call("crm.timeline.comment.add", {
            "fields": {
                "ENTITY_ID": bitrix_id,
                "ENTITY_TYPE": "lead",
                "COMMENT": text,
            }
        })
        log.info(f"добавлен комментарий к лиду #{bitrix_id}")
        return True
    except Exception as e:
        log.error(f"add_note ошибка: {e}")
        return False


def update_lead(bitrix_id: str, updates: dict) -> bool:
    """Обновить поля лида в Bitrix24."""
    try:
        bx = _get_client()
        bx.call("crm.lead.update", {"id": bitrix_id, "fields": updates})
        log.info(f"обновлён лид #{bitrix_id}")
        return True
    except Exception as e:
        log.error(f"update_lead ошибка: {e}")
        return False
