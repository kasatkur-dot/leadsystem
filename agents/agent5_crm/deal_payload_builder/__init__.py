"""Safe Bitrix24 deal payload builder for Agent 5.

This module only prepares a local payload preview for `crm.deal.add`.
It does not import the Bitrix24 client and does not call external services.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from shared.models import QualifiedLead


DEFAULT_DEAL_CATEGORY_ID = "0"
DEFAULT_DEAL_STAGE_ID = "NEW"
DEFAULT_DEAL_TYPE_ID = "SALE"
DEFAULT_AI_MANAGER_STATUS = "first_reply_needed"
DEFAULT_ASSIGNED_BY_ID = "1"

DEAL_ROUTE_BY_FLOW = {
    "A": {
        "category_id": "4",
        "stage_id": "C4:NEW",
        "label": "Перепланировка",
    },
    "B": {
        "category_id": DEFAULT_DEAL_CATEGORY_ID,
        "stage_id": DEFAULT_DEAL_STAGE_ID,
        "label": "Новый проект",
    },
}

CUSTOM_FIELD_IDS = {
    "site_source": "UF_CRM_VPP_SITE_SRC",
    "flow": "UF_CRM_VPP_FLOW",
    "score": "UF_CRM_VPP_SCORE",
    "object_type": "UF_CRM_VPP_OBJ_TYPE",
    "area_m2": "UF_CRM_VPP_AREA_M2",
    "first_touch_channel": "UF_CRM_VPP_FIRST_CH",
    "last_touch_channel": "UF_CRM_VPP_LAST_CH",
    "landing_page": "UF_CRM_VPP_LAND_URL",
    "ai_manager_status": "UF_CRM_VPP_AI_STATUS",
}

CUSTOM_FIELD_ENUM_VALUE_IDS = {
    "flow": {
        "A": "100",
        "B": "102",
    },
    "score": {
        "hot": "104",
        "warm": "106",
        "cold": "108",
        "off": "110",
    },
}


SOURCE_ID_BY_SITE_SOURCE = {
    "site_phone": "CALL",
    "site_service_phone": "CALL",
    "site_email": "EMAIL",
    "site_service_email": "EMAIL",
    "site_max": "2|MAX",
    "site_max_channel": "2|MAX",
    "site_service_max": "2|MAX",
    "site_telegram": "2|TELEGRAM",
    "site_service_telegram": "2|TELEGRAM",
    "site_yandex_maps": "WEB",
    "site_2gis": "WEB",
    "yandex_maps": "WEB",
    "2gis": "WEB",
}


FIELDS_TO_CONFIRM_BEFORE_REAL_SEND = [
    "точный SOURCE_ID для MAX и Telegram в Bitrix24 Open Lines",
    "маршрут flow A -> CATEGORY_ID=4 / STAGE_ID=C4:NEW",
    "маршрут flow B -> CATEGORY_ID=0 / STAGE_ID=NEW",
    "ASSIGNED_BY_ID=1 остаётся администратором/человеком-контролёром для первых AI-сделок",
    "созданы ли пользовательские поля UF_CRM_VPP_* в Bitrix24",
    "как хранить контакт: создать/привязать CONTACT_ID или временно писать контакт в комментарий",
    "нужно ли ставить сумму OPPORTUNITY=0 или оставлять поле пустым до расчёта",
]


def infer_site_source(lead: QualifiedLead) -> str:
    """Infer our site source label from the qualified lead metadata."""
    if lead.source.startswith("site_"):
        return lead.source
    if lead.last_touch_channel:
        channel = lead.last_touch_channel.lower()
        if channel in {"max", "telegram", "email"}:
            return f"site_{channel}"
        if channel in {"phone", "call", "телефон"}:
            return "site_phone"
    return "site_unknown"


def infer_source_id(site_source: str, lead: QualifiedLead) -> str:
    """Pick the safest known Bitrix24 SOURCE_ID for the channel."""
    if site_source in SOURCE_ID_BY_SITE_SOURCE:
        return SOURCE_ID_BY_SITE_SOURCE[site_source]
    if lead.last_touch_channel:
        channel = lead.last_touch_channel.lower()
        if channel == "email":
            return "EMAIL"
        if channel == "telegram":
            return "2|TELEGRAM"
        if channel == "max":
            return "2|MAX"
        if channel in {"phone", "call", "телефон"}:
            return "CALL"
    return "WEB"


def infer_deal_route(lead: QualifiedLead) -> dict[str, str]:
    """Return the safest MVP deal route by lead flow."""
    flow = (lead.flow or "").upper()
    return DEAL_ROUTE_BY_FLOW.get(flow, DEAL_ROUTE_BY_FLOW["B"])


def _enum_value_id(field_key: str, value: str | None) -> str | None:
    if value is None:
        return None
    return CUSTOM_FIELD_ENUM_VALUE_IDS.get(field_key, {}).get(str(value).strip())


def _area_label(area_m2: float | None) -> str:
    if area_m2 is None:
        return ""
    if float(area_m2).is_integer():
        return f"{int(area_m2)} м2"
    return f"{area_m2} м2"


def _title(lead: QualifiedLead, site_source: str) -> str:
    city = lead.city or "город не указан"
    object_part = lead.object_type or "объект"
    area = _area_label(lead.area_m2)
    tail = f"{object_part} {area}".strip()
    return f"[{lead.flow}] {site_source.upper()} — {lead.score.upper()} | {city} | {tail}"


def _comments(lead: QualifiedLead, site_source: str) -> str:
    contact = lead.contact or "контакт не указан"
    rows = [
        "Первый входящий запрос с сайта.",
        f"Сайтовая метка: {site_source}",
        f"Flow: {lead.flow}",
        f"Скор: {lead.score} — {lead.score_reason}",
        f"Город: {lead.city or 'не указан'}",
        f"Тип объекта: {lead.object_type or 'не указан'}",
        f"Площадь: {_area_label(lead.area_m2) or 'не указана'}",
        f"Первое касание: {lead.first_touch_channel or 'не указано'}",
        f"Последнее касание: {lead.last_touch_channel or 'не указано'}",
        f"Страница входа: {lead.landing_page or 'не указана'}",
        f"Контакт для связи: {contact}",
        f"Оффер: {lead.offer_text}",
        f"Следующий шаг: {lead.recommended_action}",
        "",
        "Исходный текст:",
        lead.raw_text[:1200],
    ]
    return "\n".join(rows)


def build_deal_fields(
    lead: QualifiedLead,
    *,
    site_source: str | None = None,
    category_id: str | None = None,
    stage_id: str | None = None,
    assigned_by_id: str | None = None,
) -> dict[str, Any]:
    """Build only local Bitrix24 deal fields. No network calls."""
    resolved_site_source = site_source or infer_site_source(lead)
    route = infer_deal_route(lead)
    resolved_category_id = category_id if category_id is not None else route["category_id"]
    resolved_stage_id = stage_id if stage_id is not None else route["stage_id"]
    resolved_assigned_by_id = assigned_by_id if assigned_by_id is not None else DEFAULT_ASSIGNED_BY_ID
    fields: dict[str, Any] = {
        "TITLE": _title(lead, resolved_site_source),
        "TYPE_ID": DEFAULT_DEAL_TYPE_ID,
        "CATEGORY_ID": resolved_category_id,
        "STAGE_ID": resolved_stage_id,
        "ASSIGNED_BY_ID": resolved_assigned_by_id,
        "SOURCE_ID": infer_source_id(resolved_site_source, lead),
        "COMMENTS": _comments(lead, resolved_site_source),
        CUSTOM_FIELD_IDS["site_source"]: resolved_site_source,
        CUSTOM_FIELD_IDS["flow"]: _enum_value_id("flow", lead.flow),
        CUSTOM_FIELD_IDS["score"]: _enum_value_id("score", lead.score),
        CUSTOM_FIELD_IDS["object_type"]: lead.object_type,
        CUSTOM_FIELD_IDS["area_m2"]: lead.area_m2,
        CUSTOM_FIELD_IDS["first_touch_channel"]: lead.first_touch_channel,
        CUSTOM_FIELD_IDS["last_touch_channel"]: lead.last_touch_channel,
        CUSTOM_FIELD_IDS["landing_page"]: lead.landing_page,
        CUSTOM_FIELD_IDS["ai_manager_status"]: DEFAULT_AI_MANAGER_STATUS,
    }

    return {key: value for key, value in fields.items() if value is not None}


def build_deal_payload(
    lead: QualifiedLead,
    *,
    site_source: str | None = None,
    category_id: str | None = None,
    stage_id: str | None = None,
    assigned_by_id: str | None = None,
) -> dict[str, Any]:
    """Build a complete local preview payload for Bitrix24 `crm.deal.add`."""
    resolved_site_source = site_source or infer_site_source(lead)
    fields = build_deal_fields(
        lead,
        site_source=resolved_site_source,
        category_id=category_id,
        stage_id=stage_id,
        assigned_by_id=assigned_by_id,
    )
    return {
        "method": "crm.deal.add",
        "params": {"fields": fields},
        "entity_type": "deal",
        "site_source": resolved_site_source,
        "source_id": fields.get("SOURCE_ID"),
        "category_id": fields.get("CATEGORY_ID"),
        "stage_id": fields.get("STAGE_ID"),
        "assigned_by_id": fields.get("ASSIGNED_BY_ID"),
        "contact_strategy": (
            "До подтверждения CRM-схемы контакт хранится в COMMENTS. "
            "Для production нужно решить: создавать CONTACT_ID или использовать пользовательское поле."
        ),
        "fields_to_confirm_before_real_send": FIELDS_TO_CONFIRM_BEFORE_REAL_SEND,
        "send_status": "DRY_RUN_NOT_SENT",
    }


def redact_payload_for_report(payload: dict[str, Any], contact: str | None = None) -> dict[str, Any]:
    """Return a safe report copy without exposing a real contact if one appears later."""
    safe = deepcopy(payload)
    if contact:
        text = str(contact)

        def _redact(value: Any) -> Any:
            if isinstance(value, str):
                return value.replace(text, "REDACTED_CONTACT")
            if isinstance(value, list):
                return [_redact(item) for item in value]
            if isinstance(value, dict):
                return {key: _redact(item) for key, item in value.items()}
            return value

        safe = _redact(safe)
    return safe
