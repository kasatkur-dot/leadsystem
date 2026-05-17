"""Local dry-run for VPP AI-manager intake scenarios.

This script does not call Bitrix24, Redis, Telegram, MAX, IMAP, LLM APIs,
scheduler, publisher, ads, or any external service.
It creates local artifacts that show how an incoming message becomes:

source_card -> intake_card -> qualified_lead -> missing_data_note
-> Bitrix24 deal payload preview -> next_action.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from agents.agent5_crm.deal_payload_builder import build_deal_payload, redact_payload_for_report
from shared.models import QualifiedLead, RawLead


REPORT_DIR = PROJECT_ROOT / "data" / "reports" / "vpp_ai_manager_dry_run"
SUMMARY_JSON = PROJECT_ROOT / "data" / "reports" / "vpp_ai_manager_dry_run.json"
SUMMARY_MD = PROJECT_ROOT / "data" / "reports" / "vpp_ai_manager_dry_run.md"


SCENARIOS: list[dict[str, Any]] = [
    {
        "id": "warehouse_angar",
        "title": "Склад / ангар",
        "source": "site_max",
        "source_type": "organic",
        "traffic_channel": "social",
        "first_touch_channel": "MAX",
        "last_touch_channel": "MAX",
        "landing_page": "/landing/sklady-angary/",
        "contact": "+7 900 000-00-01",
        "author_name": "Тестовый клиент ВПП",
        "raw_text": (
            "Здравствуйте. Нужен проект склада в Краснодаре, примерно 1200 м2. "
            "Планируем ПД и РД, конструктив КР/КЖ/КМ, возможно экспертиза. "
            "Есть черновое ТЗ, хотим понять состав работ и сроки."
        ),
    },
    {
        "id": "commercial_replan",
        "title": "Коммерческая перепланировка",
        "source": "site_telegram",
        "source_type": "organic",
        "traffic_channel": "social",
        "first_touch_channel": "Telegram",
        "last_touch_channel": "Telegram",
        "landing_page": "/landing/pereplanirovka-biznes/",
        "contact": "@test_vpp_client",
        "author_name": "Тестовый арендатор",
        "raw_text": (
            "Добрый день. Открываем магазин в торговом центре в Казани, 180 м2. "
            "Нужно поменять перегородки и подготовить проект для арендодателя. "
            "План помещения есть, требования ТЦ частично прислали."
        ),
    },
    {
        "id": "apartment_replan",
        "title": "Перепланировка квартиры",
        "source": "site_max",
        "source_type": "organic",
        "traffic_channel": "social",
        "first_touch_channel": "MAX",
        "last_touch_channel": "MAX",
        "landing_page": "/services/pereplanirovka-kvartiry/",
        "contact": "+7 900 000-00-03",
        "author_name": "Тестовый собственник",
        "raw_text": (
            "Здравствуйте. Купили квартиру в Москве, 64 м2. Хотим объединить кухню "
            "с комнатой и перенести санузел. Ремонт еще не начали. План БТИ пока ищем."
        ),
    },
]


SEGMENT_RULES: list[dict[str, Any]] = [
    {
        "segment": "b2b_warehouse_angar",
        "flow": "B",
        "client_type": "ООО / ИП / девелопер",
        "object_type": "склад / ангар",
        "keywords": ["склад", "ангар", "производ"],
        "required": ["city", "area_m2", "object_type", "project_scope", "stage", "documents", "deadline", "client_type"],
        "offer": "Первичный состав ПД/РД и проектных разделов после проверки исходных данных.",
    },
    {
        "segment": "b2b_commercial_replan",
        "flow": "A",
        "client_type": "ООО / ИП / арендатор",
        "object_type": "коммерческое помещение",
        "keywords": ["магазин", "торгов", "тц", "офис", "арендодател", "перегород"],
        "required": ["city", "area_m2", "object_type", "documents", "landlord_requirements", "planned_changes", "deadline"],
        "offer": "Проект коммерческой перепланировки и пакет для арендодателя/УК после проверки документов.",
    },
    {
        "segment": "b2c_apartment_replan",
        "flow": "A",
        "client_type": "физлицо",
        "object_type": "квартира",
        "keywords": ["квартир", "кухн", "сануз", "бти", "ремонт"],
        "required": ["city", "area_m2", "object_type", "documents", "planned_changes", "repair_status"],
        "offer": "Проверка идеи перепланировки до ремонта и список безопасных следующих шагов.",
    },
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _area_m2(text: str) -> float | None:
    match = re.search(r"(\d+(?:[,.]\d+)?)\s*(?:м2|м²|кв\.?\s*м)", text, flags=re.IGNORECASE)
    if not match:
        return None
    return float(match.group(1).replace(",", "."))


def _city(text: str) -> str | None:
    known = ["Москва", "Казань", "Краснодар", "Санкт-Петербург", "Екатеринбург", "Новосибирск", "Тюмень"]
    lower = text.lower()
    for city in known:
        if city.lower() in lower:
            return city
    return None


def _document_signals(text: str) -> list[str]:
    lower = text.lower()
    docs: list[str] = []
    if "тз" in lower:
        docs.append("ТЗ")
    if "план бти" in lower or "бти" in lower:
        docs.append("план БТИ")
    elif "план" in lower:
        docs.append("план помещения")
    if "требования тц" in lower or "требования" in lower:
        docs.append("требования арендодателя/ТЦ")
    if "фото" in lower:
        docs.append("фото")
    return docs


def _planned_changes(text: str) -> str | None:
    lower = text.lower()
    if "перегород" in lower:
        return "изменение перегородок"
    if "кухн" in lower or "сануз" in lower:
        return "изменение кухни/санузла"
    if "реконструк" in lower:
        return "реконструкция"
    return None


def _project_scope(text: str) -> list[str]:
    lower = text.lower()
    scope: list[str] = []
    for token in ["ПД", "РД", "КР", "КЖ", "КМ", "АР"]:
        if token.lower() in lower:
            scope.append(token)
    if "экспертиз" in lower:
        scope.append("экспертиза при необходимости")
    if "проект" in lower and not scope:
        scope.append("проект")
    return scope


def _stage(text: str) -> str | None:
    lower = text.lower()
    if "чернов" in lower or "тз" in lower:
        return "есть первичное ТЗ"
    if "ремонт еще не начали" in lower:
        return "до ремонта"
    if "открываем" in lower:
        return "подготовка к открытию"
    return None


def _deadline(text: str) -> str | None:
    lower = text.lower()
    if "срок" in lower:
        return "сроки нужно уточнить"
    if "открываем" in lower:
        return "срок открытия нужно уточнить"
    return None


def _repair_status(text: str) -> str | None:
    lower = text.lower()
    if "ремонт еще не начали" in lower:
        return "ремонт не начат"
    if "ремонт" in lower:
        return "статус ремонта нужно уточнить"
    return None


def _pick_rule(text: str) -> dict[str, Any]:
    lower = text.lower()
    for rule in SEGMENT_RULES:
        if any(keyword in lower for keyword in rule["keywords"]):
            return rule
    return SEGMENT_RULES[0]


def _facts(text: str, rule: dict[str, Any]) -> dict[str, Any]:
    docs = _document_signals(text)
    return {
        "city": _city(text),
        "area_m2": _area_m2(text),
        "object_type": rule["object_type"],
        "project_scope": _project_scope(text),
        "stage": _stage(text),
        "documents": docs,
        "landlord_requirements": "требования арендодателя/ТЦ" in docs,
        "planned_changes": _planned_changes(text),
        "deadline": _deadline(text),
        "client_type": rule["client_type"],
        "repair_status": _repair_status(text),
    }


def _is_present(value: Any) -> bool:
    if value is None:
        return False
    if value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value)
    return True


def _missing_data(facts: dict[str, Any], required: list[str]) -> list[str]:
    labels = {
        "city": "город",
        "area_m2": "площадь",
        "object_type": "тип объекта",
        "project_scope": "состав работ или нужные разделы",
        "stage": "стадия задачи",
        "documents": "имеющиеся документы",
        "deadline": "сроки",
        "client_type": "кто заказчик",
        "landlord_requirements": "требования арендодателя/ТЦ",
        "planned_changes": "что именно меняется",
        "repair_status": "начат ли ремонт",
    }
    return [labels[item] for item in required if not _is_present(facts.get(item))]


def _data_completeness(missing: list[str], required: list[str]) -> str:
    if not required:
        return "partial"
    present_count = len(required) - len(missing)
    ratio = present_count / len(required)
    if ratio >= 0.9:
        return "enough_for_kp"
    if ratio >= 0.65:
        return "enough_for_review"
    if ratio > 0:
        return "partial"
    return "empty"


def _next_action(data_completeness: str, segment: str) -> str:
    if data_completeness == "enough_for_kp":
        return "kp_prepare"
    if data_completeness == "enough_for_review":
        if segment == "b2b_warehouse_angar":
            return "engineer_review"
        return "ask_missing_data_then_review"
    if data_completeness == "partial":
        return "ask_data"
    return "manual_contact_needed"


def _score(data_completeness: str, segment: str) -> tuple[str, str]:
    if segment.startswith("b2b") and data_completeness in {"enough_for_kp", "enough_for_review"}:
        return "hot", "B2B-сегмент, объект и площадь понятны, есть часть исходных данных."
    if data_completeness in {"enough_for_kp", "enough_for_review"}:
        return "warm", "Профильный запрос, можно продолжать после проверки документов."
    return "warm", "Профильный запрос, но не хватает исходных данных для следующего шага."


def _contact_type(contact: str | None) -> str | None:
    if not contact:
        return None
    if contact.startswith("@"):
        return "telegram"
    if "@" in contact:
        return "email"
    return "phone"


def _first_reply(scenario_title: str, facts: dict[str, Any], missing: list[str], data_completeness: str) -> str:
    if data_completeness == "enough_for_kp":
        return (
            f"Поняла задачу: {scenario_title}. Данных достаточно для первичной подготовки КП. "
            "Передам инженеру на проверку состава работ и сроков."
        )
    missing_text = ", ".join(missing)
    return (
        f"Поняла задачу: {scenario_title}. Чтобы понять состав работ и можно ли подготовить КП за 24 часа, "
        f"нужно уточнить: {missing_text}."
    )


def _build_raw_lead(scenario: dict[str, Any]) -> RawLead:
    return RawLead(
        source=scenario["source"],
        raw_text=scenario["raw_text"],
        contact=scenario["contact"],
        author_name=scenario["author_name"],
        city=_city(scenario["raw_text"]),
        source_type=scenario["source_type"],
        traffic_channel=scenario["traffic_channel"],
        first_touch_channel=scenario["first_touch_channel"],
        last_touch_channel=scenario["last_touch_channel"],
        landing_page=scenario["landing_page"],
        consent_status="not_required",
    )


def _build_qualified_lead(
    raw_lead: RawLead,
    rule: dict[str, Any],
    facts: dict[str, Any],
    data_completeness: str,
    next_action: str,
) -> QualifiedLead:
    score, reason = _score(data_completeness, rule["segment"])
    return QualifiedLead(
        id=f"ql_{raw_lead.id}",
        raw_lead_id=raw_lead.id,
        source=raw_lead.source,
        flow=rule["flow"],
        contact=raw_lead.contact,
        contact_type=_contact_type(raw_lead.contact),  # type: ignore[arg-type]
        city=facts["city"],
        object_type=facts["object_type"],
        area_m2=facts["area_m2"],
        score=score,  # type: ignore[arg-type]
        score_reason=reason,
        offer_text=rule["offer"],
        recommended_action=next_action,
        source_type=raw_lead.source_type,
        traffic_channel=raw_lead.traffic_channel,
        first_touch_channel=raw_lead.first_touch_channel,
        last_touch_channel=raw_lead.last_touch_channel,
        landing_page=raw_lead.landing_page,
        consent_status=raw_lead.consent_status,
        raw_text=raw_lead.raw_text,
    )


def _redact(value: Any, contacts: list[str | None]) -> Any:
    if isinstance(value, str):
        safe = value
        for contact in contacts:
            if contact:
                safe = safe.replace(contact, "REDACTED_CONTACT")
        return safe
    if isinstance(value, list):
        return [_redact(item, contacts) for item in value]
    if isinstance(value, dict):
        return {key: _redact(item, contacts) for key, item in value.items()}
    return value


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _scenario_artifact(scenario: dict[str, Any]) -> dict[str, Any]:
    raw_lead = _build_raw_lead(scenario)
    rule = _pick_rule(raw_lead.raw_text)
    facts = _facts(raw_lead.raw_text, rule)
    missing = _missing_data(facts, rule["required"])
    completeness = _data_completeness(missing, rule["required"])
    next_action = _next_action(completeness, rule["segment"])
    qualified_lead = _build_qualified_lead(raw_lead, rule, facts, completeness, next_action)
    payload = build_deal_payload(qualified_lead)
    safe_payload = redact_payload_for_report(payload, qualified_lead.contact)
    contacts = [scenario.get("contact"), raw_lead.contact, qualified_lead.contact]

    artifact = {
        "scenario_id": scenario["id"],
        "scenario_title": scenario["title"],
        "dry_run": True,
        "created_at": _utc_now(),
        "external_calls": {
            "redis": False,
            "bitrix24": False,
            "telegram_send": False,
            "max_send": False,
            "imap": False,
            "llm": False,
            "scheduler": False,
            "publisher": False,
            "ads": False,
        },
        "source_card": {
            "source": scenario["source"],
            "source_type": scenario["source_type"],
            "traffic_channel": scenario["traffic_channel"],
            "first_touch_channel": scenario["first_touch_channel"],
            "last_touch_channel": scenario["last_touch_channel"],
            "landing_page": scenario["landing_page"],
        },
        "intake_card": {
            "raw_lead": raw_lead.model_dump(mode="json"),
            "facts": facts,
            "first_reply": _first_reply(scenario["title"], facts, missing, completeness),
        },
        "qualified_lead": qualified_lead.model_dump(mode="json"),
        "vpp_ai_manager": {
            "segment": rule["segment"],
            "client_type": rule["client_type"],
            "data_completeness": completeness,
            "missing_data": missing,
            "next_action": next_action,
            "kp_24h_allowed": completeness == "enough_for_kp",
            "human_control_required": True,
        },
        "bitrix_deal_preview": safe_payload,
    }
    return _redact(artifact, contacts)


def _summary_markdown(result: dict[str, Any]) -> str:
    rows = []
    for scenario in result["scenarios"]:
        ai = scenario["vpp_ai_manager"]
        deal = scenario["bitrix_deal_preview"]
        rows.append(
            "| {title} | `{segment}` | `{flow}` | `{score}` | `{completeness}` | `{next_action}` | `{send_status}` |".format(
                title=scenario["scenario_title"],
                segment=ai["segment"],
                flow=scenario["qualified_lead"]["flow"],
                score=scenario["qualified_lead"]["score"],
                completeness=ai["data_completeness"],
                next_action=ai["next_action"],
                send_status=deal["send_status"],
            )
        )
    return "\n".join(
        [
            "# VPP AI Manager Dry Run",
            "",
            f"Дата: {result['created_at']}",
            "",
            "Статус: локальный dry-run. Внешние сервисы не запускались.",
            "",
            "| Сценарий | Segment | Flow | Score | Data completeness | Next action | Bitrix |",
            "|---|---|---|---|---|---|---|",
            *rows,
            "",
            "## Что проверено",
            "",
            "- входящее сообщение превращается в `source_card` и `intake_card`;",
            "- Agent 3 логика определяет `segment`, `client_type`, `data_completeness`, `missing_data`, `next_action`;",
            "- Agent 5 builder готовит только preview `crm.deal.add`; отправки в Bitrix24 нет;",
            "- контакты в отчетах заредактированы.",
            "",
            "## Следующий шаг",
            "",
            "Добавить показатели dry-run в dashboard и потом вручную выбрать первый сценарий для реального AI-manager MVP.",
            "",
        ]
    )


def run() -> dict[str, Any]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    scenario_artifacts = [_scenario_artifact(scenario) for scenario in SCENARIOS]

    for artifact in scenario_artifacts:
        _write_json(REPORT_DIR / f"{artifact['scenario_id']}.json", artifact)

    result = {
        "test_type": "vpp_ai_manager_dry_run",
        "dry_run": True,
        "created_at": _utc_now(),
        "scenario_count": len(scenario_artifacts),
        "external_calls": {
            "redis": False,
            "bitrix24": False,
            "telegram_send": False,
            "max_send": False,
            "imap": False,
            "llm": False,
            "scheduler": False,
            "publisher": False,
            "ads": False,
        },
        "scenarios": scenario_artifacts,
        "report_files": {
            "summary_json": str(SUMMARY_JSON.relative_to(PROJECT_ROOT)),
            "summary_md": str(SUMMARY_MD.relative_to(PROJECT_ROOT)),
            "scenario_dir": str(REPORT_DIR.relative_to(PROJECT_ROOT)),
        },
    }

    _write_json(SUMMARY_JSON, result)
    SUMMARY_MD.write_text(_summary_markdown(result), encoding="utf-8")
    return result


def main() -> int:
    result = run()
    print(f"test_type={result['test_type']}")
    print(f"dry_run={result['dry_run']}")
    print(f"scenario_count={result['scenario_count']}")
    for scenario in result["scenarios"]:
        ai = scenario["vpp_ai_manager"]
        print(
            "scenario={id} segment={segment} data_completeness={data_completeness} next_action={next_action}".format(
                id=scenario["scenario_id"],
                segment=ai["segment"],
                data_completeness=ai["data_completeness"],
                next_action=ai["next_action"],
            )
        )
    print(
        "external_calls="
        + ",".join(f"{key}:{value}" for key, value in result["external_calls"].items())
    )
    print(f"report_file={SUMMARY_JSON.relative_to(PROJECT_ROOT)}")
    print(f"report_md={SUMMARY_MD.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
