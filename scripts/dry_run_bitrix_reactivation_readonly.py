"""Build a read-only Bitrix24 reactivation and cleanup plan from local audit.

This script reads only data/reports/bitrix_readonly_audit.json. It does not call
Bitrix24 and does not create, update, merge, delete, or message anything.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = PROJECT_ROOT / "data" / "reports" / "bitrix_readonly_audit.json"
REPORT_JSON_PATH = PROJECT_ROOT / "data" / "reports" / "bitrix_reactivation_readonly_plan.json"
REPORT_MD_PATH = PROJECT_ROOT / "data" / "reports" / "bitrix_reactivation_readonly_plan.md"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _relative(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _sum_duplicate_groups(duplicates: dict[str, Any]) -> int:
    return sum(
        len(_as_list(duplicates.get(key)))
        for key in ["contacts_by_phone", "contacts_by_email", "leads_by_phone", "leads_by_email"]
    )


def _top_items(items: list[dict[str, Any]], key: str, limit: int = 10) -> list[dict[str, Any]]:
    rows = []
    for item in items[:limit]:
        rows.append(
            {
                key: item.get(key, ""),
                "name": item.get("name", ""),
                "count": item.get("count", 0),
            }
        )
    return rows


def build_plan(audit: dict[str, Any]) -> dict[str, Any]:
    counts = _as_dict(audit.get("counts"))
    quality = _as_dict(audit.get("quality_flags"))
    duplicates = _as_dict(audit.get("duplicates"))
    lead_sources = _as_list(audit.get("lead_sources"))
    lead_statuses = _as_list(audit.get("lead_statuses"))
    deal_stages = _as_list(audit.get("deal_stages"))
    recent_active_leads = _as_list(audit.get("recent_active_leads"))

    contact_phone_dupes = _as_list(duplicates.get("contacts_by_phone"))
    contact_email_dupes = _as_list(duplicates.get("contacts_by_email"))
    lead_phone_dupes = _as_list(duplicates.get("leads_by_phone"))
    lead_email_dupes = _as_list(duplicates.get("leads_by_email"))
    total_duplicate_groups = _sum_duplicate_groups(duplicates)

    cleanup_queue = [
        {
            "queue_id": "cleanup_001",
            "title": "Контакты-дубли по телефону",
            "count": len(contact_phone_dupes),
            "priority": "P1",
            "action": "Ручная проверка групп дублей. Ничего не объединять автоматически.",
            "stop_rule": "Перед merge нужен backup и ручное решение по каждой группе.",
        },
        {
            "queue_id": "cleanup_002",
            "title": "Контакты-дубли по email",
            "count": len(contact_email_dupes),
            "priority": "P1",
            "action": "Проверить, где один клиент создан несколько раз.",
            "stop_rule": "Не объединять разные юрлица только из-за одного домена или общей почты.",
        },
        {
            "queue_id": "cleanup_003",
            "title": "Лиды-дубли по телефону/email",
            "count": len(lead_phone_dupes) + len(lead_email_dupes),
            "priority": "P2",
            "action": "Понять, какие лиды можно связать с контактом или сделкой.",
            "stop_rule": "Не закрывать лиды без проверки истории и ответственного.",
        },
        {
            "queue_id": "cleanup_004",
            "title": "Контакты без телефона/email",
            "count": int(quality.get("contacts_without_phone_or_email") or 0),
            "priority": "P2",
            "action": "Отделить полезные карточки от пустых.",
            "stop_rule": "Не удалять карточки автоматически.",
        },
        {
            "queue_id": "cleanup_005",
            "title": "Лиды без телефона/email",
            "count": int(quality.get("leads_without_phone_or_email") or 0),
            "priority": "P2",
            "action": "Понять, есть ли email/телефон в комментариях или связанной сделке.",
            "stop_rule": "Не списывать как мусор без проверки источника.",
        },
        {
            "queue_id": "cleanup_006",
            "title": "Лиды без источника",
            "count": int(quality.get("leads_without_source") or 0),
            "priority": "P3",
            "action": "Назначить источник по истории только там, где он очевиден.",
            "stop_rule": "Не придумывать источник, если данных нет.",
        },
    ]

    reactivation_buckets = [
        {
            "bucket_id": "reactivation_001",
            "title": "Старые заявки с контактом",
            "basis": "после ручной проверки дублей и истории",
            "priority": "P1",
            "first_message_status": "NOT_PREPARED_APPROVAL_REQUIRED",
        },
        {
            "bucket_id": "reactivation_002",
            "title": "Сделки без понятного следующего шага",
            "basis": "по стадиям сделок и дате изменения",
            "priority": "P1",
            "first_message_status": "NOT_PREPARED_APPROVAL_REQUIRED",
        },
        {
            "bucket_id": "reactivation_003",
            "title": "Лиды без источника, но с контактом",
            "basis": "восстановить источник или пометить unknown",
            "priority": "P2",
            "first_message_status": "NOT_PREPARED_APPROVAL_REQUIRED",
        },
        {
            "bucket_id": "reactivation_004",
            "title": "Пустые карточки",
            "basis": "нет телефона/email",
            "priority": "P4",
            "first_message_status": "DO_NOT_CONTACT",
        },
    ]

    return {
        "status": "READY",
        "generated_at": _utc_now(),
        "source_audit_file": _relative(AUDIT_PATH),
        "readonly": True,
        "limited_by_pages": bool(audit.get("limited_by_pages")),
        "summary": {
            "contacts": counts.get("contacts", 0),
            "leads_total": counts.get("leads_total", 0),
            "leads_active": counts.get("leads_active", 0),
            "deals_total": counts.get("deals_total", 0),
            "total_duplicate_groups": total_duplicate_groups,
            "contacts_without_phone_or_email": quality.get("contacts_without_phone_or_email", 0),
            "leads_without_phone_or_email": quality.get("leads_without_phone_or_email", 0),
            "leads_without_source": quality.get("leads_without_source", 0),
        },
        "cleanup_queue": cleanup_queue,
        "reactivation_buckets": reactivation_buckets,
        "top_lead_sources": _top_items(lead_sources, "source_id"),
        "top_lead_statuses": _top_items(lead_statuses, "status_id"),
        "top_deal_stages": _top_items(deal_stages, "stage_id"),
        "recent_active_leads_preview": recent_active_leads[:10],
        "approval_required_before": [
            "merge_duplicates",
            "update_contact",
            "update_lead",
            "close_lead",
            "create_task",
            "send_message",
            "reactivation_campaign",
        ],
        "external_calls": {
            "bitrix24": False,
            "telegram_send": False,
            "max": False,
            "vk": False,
            "ads": False,
            "llm": False,
            "scheduler": False,
            "publisher": False,
        },
    }


def _write_markdown(plan: dict[str, Any]) -> None:
    summary = _as_dict(plan.get("summary"))
    lines = [
        "# Bitrix Reactivation Readonly Plan",
        "",
        f"Generated at: `{plan['generated_at']}`",
        "",
        "Статус: read-only. Bitrix24 не вызывался, карточки не менялись, сообщения не отправлялись.",
        "",
        "## Summary",
        "",
        "| Метрика | Значение |",
        "|---|---:|",
    ]
    for key, value in summary.items():
        lines.append(f"| {key} | {value} |")

    lines.extend(["", "## Cleanup Queue", "", "| ID | Очередь | Count | Priority | Action | Stop rule |", "|---|---|---:|---|---|---|"])
    for item in plan["cleanup_queue"]:
        lines.append(
            "| {queue_id} | {title} | {count} | {priority} | {action} | {stop_rule} |".format(**item)
        )

    lines.extend(["", "## Reactivation Buckets", "", "| ID | Группа | Priority | Status | Basis |", "|---|---|---|---|---|"])
    for item in plan["reactivation_buckets"]:
        lines.append(
            "| {bucket_id} | {title} | {priority} | {first_message_status} | {basis} |".format(**item)
        )

    lines.extend(["", "## Top Lead Sources", "", "| Source | Name | Count |", "|---|---|---:|"])
    for item in plan["top_lead_sources"]:
        lines.append(f"| {item.get('source_id', '')} | {item.get('name', '')} | {item.get('count', 0)} |")

    lines.extend(["", "## Approval Required Before", ""])
    for item in plan["approval_required_before"]:
        lines.append(f"- `{item}`")
    lines.append("")
    REPORT_MD_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    audit = _read_json(AUDIT_PATH)
    if not audit:
        print("bitrix_reactivation_readonly_plan_status=MISSING_AUDIT")
        print(f"expected_file={_relative(AUDIT_PATH)}")
        return 1

    plan = build_plan(audit)
    REPORT_JSON_PATH.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_markdown(plan)

    print("bitrix_reactivation_readonly_plan_status=READY")
    print(f"duplicate_groups={plan['summary']['total_duplicate_groups']}")
    print(f"cleanup_items={len(plan['cleanup_queue'])}")
    print(f"reactivation_buckets={len(plan['reactivation_buckets'])}")
    print(f"report_file={_relative(REPORT_JSON_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
