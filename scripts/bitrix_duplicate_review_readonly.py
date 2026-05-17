"""Detailed read-only Bitrix24 duplicate review.

This script is the second audit layer after `audit_bitrix_readonly.py`.
It does not create, update, merge, or delete anything in Bitrix24.

It builds a review queue for suspicious contacts/leads and explains why each
group should be merged, reviewed, or left separate. Phone and email values are
masked in reports; Bitrix IDs are kept so the user can open the records.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.audit_bitrix_readonly import (  # noqa: E402
    BitrixReadonlyClient,
    _email_key,
    _hash_key,
    _mask_email,
    _mask_phone,
    _phone_key,
    _read_contacts,
    _read_deals,
    _read_leads,
    _safe_text,
)


JSON_REPORT_PATH = PROJECT_ROOT / "data" / "reports" / "bitrix_duplicate_review.json"
MD_REPORT_PATH = PROJECT_ROOT / "data" / "reports" / "bitrix_duplicate_review.md"

SERVICE_EMAIL_DOMAINS = {
    "avito.ru",
    "b2b-center.ru",
    "bidzaar.com",
    "e.roseltorg.ru",
    "etscorp.ru",
    "gosuslugi.ru",
    "info.sberbank.ru",
    "sberbank-ast.ru",
    "sbis.ru",
}


def _normalize_name(row: dict[str, Any]) -> str:
    parts = [
        _safe_text(row.get("LAST_NAME")),
        _safe_text(row.get("NAME")),
        _safe_text(row.get("SECOND_NAME")),
    ]
    return re.sub(r"\s+", " ", " ".join(part for part in parts if part).lower()).strip()


def _name_status(row: dict[str, Any]) -> str:
    name = _normalize_name(row)
    if not name:
        return "empty"
    if name in {"неизвестно", "без имени", "контакт", "лид", "клиент"}:
        return "generic"
    return "filled"


def _email_domain(email: str) -> str:
    email = _email_key(email)
    if "@" not in email:
        return ""
    return email.split("@", 1)[1]


def _item_values(row: dict[str, Any], field: str, key_fn) -> list[str]:
    keys = []
    for item in row.get(field) or []:
        key = key_fn(item.get("VALUE"))
        if key and key not in keys:
            keys.append(key)
    return keys


def _item_masks(row: dict[str, Any], field: str, mask_fn) -> list[str]:
    values = []
    for item in row.get(field) or []:
        masked = mask_fn(item.get("VALUE"))
        if masked and masked not in values:
            values.append(masked)
    return values


def _make_maps(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {_safe_text(row.get("ID")): row for row in rows if _safe_text(row.get("ID"))}


def _bucket_rows(rows: list[dict[str, Any]], field: str, key_fn) -> dict[str, list[str]]:
    buckets: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        row_id = _safe_text(row.get("ID"))
        seen_in_row = set()
        for item in row.get(field) or []:
            key = key_fn(item.get("VALUE"))
            if key and key not in seen_in_row:
                buckets[key].append(row_id)
                seen_in_row.add(key)
    return {key: ids for key, ids in buckets.items() if len(set(ids)) > 1}


def _bucket_names(contacts: list[dict[str, Any]]) -> dict[str, list[str]]:
    buckets: dict[str, list[str]] = defaultdict(list)
    for contact in contacts:
        name = _normalize_name(contact)
        if name:
            buckets[name].append(_safe_text(contact.get("ID")))
    return {key: ids for key, ids in buckets.items() if len(set(ids)) > 1}


def _index_deals_by_contact(deals: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    index: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for deal in deals:
        contact_id = _safe_text(deal.get("CONTACT_ID"))
        if contact_id:
            index[contact_id].append(deal)
    return index


def _index_rows_by_field(rows: list[dict[str, Any]], field: str, key_fn) -> dict[str, list[dict[str, Any]]]:
    index: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        seen_in_row = set()
        for item in row.get(field) or []:
            key = key_fn(item.get("VALUE"))
            if key and key not in seen_in_row:
                index[key].append(row)
                seen_in_row.add(key)
    return index


def _status_maps(statuses: list[dict[str, Any]]) -> tuple[dict[str, str], dict[str, str]]:
    lead_status = {}
    generic_status = {}
    for row in statuses:
        status_id = _safe_text(row.get("STATUS_ID"))
        name = _safe_text(row.get("NAME"))
        entity_id = _safe_text(row.get("ENTITY_ID"))
        if status_id and name:
            generic_status[status_id] = name
            if entity_id == "STATUS":
                lead_status[status_id] = name
    return lead_status, generic_status


def _read_statuses_all(client: BitrixReadonlyClient) -> list[dict[str, Any]]:
    try:
        return client.list_all("crm.status.list", {})
    except Exception:
        return []


def _summarize_leads(leads: list[dict[str, Any]], lead_status_map: dict[str, str], source_map: dict[str, str]) -> dict[str, Any]:
    statuses = Counter(_safe_text(row.get("STATUS_ID")) or "EMPTY" for row in leads)
    sources = Counter(_safe_text(row.get("SOURCE_ID")) or "EMPTY" for row in leads)
    return {
        "count": len(leads),
        "ids": [_safe_text(row.get("ID")) for row in leads[:30]],
        "statuses": [
            {"id": key, "name": lead_status_map.get(key, ""), "count": value}
            for key, value in statuses.most_common()
        ],
        "sources": [
            {"id": key, "name": source_map.get(key, ""), "count": value}
            for key, value in sources.most_common()
        ],
    }


def _summarize_deals(deals: list[dict[str, Any]], status_map: dict[str, str], source_map: dict[str, str]) -> dict[str, Any]:
    stages = Counter(_safe_text(row.get("STAGE_ID")) or "EMPTY" for row in deals)
    sources = Counter(_safe_text(row.get("SOURCE_ID")) or "EMPTY" for row in deals)
    return {
        "count": len(deals),
        "ids": [_safe_text(row.get("ID")) for row in deals[:30]],
        "stages": [
            {"id": key, "name": status_map.get(key, ""), "count": value}
            for key, value in stages.most_common()
        ],
        "sources": [
            {"id": key, "name": source_map.get(key, ""), "count": value}
            for key, value in sources.most_common()
        ],
    }


def _contact_card(
    contact: dict[str, Any],
    contact_deals: list[dict[str, Any]],
    matched_leads: list[dict[str, Any]],
    lead_status_map: dict[str, str],
    status_map: dict[str, str],
    source_map: dict[str, str],
) -> dict[str, Any]:
    name = _normalize_name(contact)
    return {
        "id": _safe_text(contact.get("ID")),
        "name_status": _name_status(contact),
        "name_hash": _hash_key(name) if name else "",
        "phones": _item_masks(contact, "PHONE", _mask_phone),
        "emails": _item_masks(contact, "EMAIL", _mask_email),
        "company_id": _safe_text(contact.get("COMPANY_ID")),
        "assigned_by_id": _safe_text(contact.get("ASSIGNED_BY_ID")),
        "created": _safe_text(contact.get("DATE_CREATE"))[:19],
        "modified": _safe_text(contact.get("DATE_MODIFY"))[:19],
        "linked_deals": _summarize_deals(contact_deals, status_map, source_map),
        "matched_leads_by_phone_or_email": _summarize_leads(matched_leads, lead_status_map, source_map),
    }


def _classify_contact_group(match_type: str, contacts: list[dict[str, Any]], matched_key: str) -> dict[str, str]:
    has_deals = False
    names = {_normalize_name(row) for row in contacts if _normalize_name(row)}
    name_statuses = {_name_status(row) for row in contacts}

    if match_type == "email":
        domain = _email_domain(matched_key)
        if domain in SERVICE_EMAIL_DOMAINS:
            return {
                "risk": "high",
                "decision_hint": "do_not_merge_by_email_only",
                "why": "Email похож на системный адрес площадки/сервиса. Он может повторяться у разных заявок.",
            }

    if match_type == "phone" and len(names) <= 1:
        return {
            "risk": "medium",
            "decision_hint": "likely_duplicate_check_history",
            "why": "Один телефон и одинаковое/пустое имя. Вероятный дубль, но перед объединением проверить сделки и дела.",
        }

    if match_type in {"phone", "email"}:
        return {
            "risk": "medium",
            "decision_hint": "review_before_merge",
            "why": "Совпадает сильный идентификатор, но карточки могут отличаться историей, компанией или ответственным.",
        }

    if "empty" in name_statuses or "generic" in name_statuses:
        return {
            "risk": "high",
            "decision_hint": "do_not_merge_by_name",
            "why": "Совпадает пустое или типовое имя. Это сигнал плохого заполнения, а не доказательство дубля.",
        }

    return {
        "risk": "high",
        "decision_hint": "weak_match_manual_only",
        "why": "Совпадает только имя. Объединять можно только при совпадении телефона/email или явной истории.",
    }


def _build_contact_groups(
    contacts: list[dict[str, Any]],
    deals_by_contact: dict[str, list[dict[str, Any]]],
    leads_by_phone: dict[str, list[dict[str, Any]]],
    leads_by_email: dict[str, list[dict[str, Any]]],
    contact_map: dict[str, dict[str, Any]],
    lead_status_map: dict[str, str],
    status_map: dict[str, str],
    source_map: dict[str, str],
) -> list[dict[str, Any]]:
    groups = []
    phone_buckets = _bucket_rows(contacts, "PHONE", _phone_key)
    email_buckets = _bucket_rows(contacts, "EMAIL", _email_key)
    name_buckets = _bucket_names(contacts)

    for match_type, buckets, mask_fn in [
        ("phone", phone_buckets, _mask_phone),
        ("email", email_buckets, _mask_email),
    ]:
        for key, ids in buckets.items():
            unique_ids = sorted(set(ids), key=lambda value: int(value) if value.isdigit() else value)
            rows = [contact_map[row_id] for row_id in unique_ids if row_id in contact_map]
            matched_leads = []
            if match_type == "phone":
                matched_leads = leads_by_phone.get(key, [])
            elif match_type == "email":
                matched_leads = leads_by_email.get(key, [])

            classification = _classify_contact_group(match_type, rows, key)
            groups.append(
                {
                    "group_id": f"contact_{match_type}_{_hash_key(key)}",
                    "entity": "contact",
                    "match_type": match_type,
                    "matched_value": mask_fn(key),
                    "record_count": len(unique_ids),
                    **classification,
                    "record_ids": unique_ids,
                    "records": [
                        _contact_card(
                            row,
                            deals_by_contact.get(_safe_text(row.get("ID")), []),
                            matched_leads,
                            lead_status_map,
                            status_map,
                            source_map,
                        )
                        for row in rows
                    ],
                }
            )

    for name, ids in name_buckets.items():
        unique_ids = sorted(set(ids), key=lambda value: int(value) if value.isdigit() else value)
        rows = [contact_map[row_id] for row_id in unique_ids if row_id in contact_map]
        if len(unique_ids) < 2:
            continue
        classification = _classify_contact_group("name", rows, name)
        groups.append(
            {
                "group_id": f"contact_name_{_hash_key(name)}",
                "entity": "contact",
                "match_type": "name",
                "matched_value": "name_hash:" + _hash_key(name),
                "record_count": len(unique_ids),
                **classification,
                "record_ids": unique_ids[:100],
                "records": [
                    _contact_card(
                        row,
                        deals_by_contact.get(_safe_text(row.get("ID")), []),
                        [],
                        lead_status_map,
                        status_map,
                        source_map,
                    )
                    for row in rows[:30]
                ],
            }
        )

    priority = {"phone": 0, "email": 1, "name": 2}
    return sorted(groups, key=lambda item: (priority.get(item["match_type"], 9), -item["record_count"]))


def _lead_card(lead: dict[str, Any], lead_status_map: dict[str, str], source_map: dict[str, str]) -> dict[str, Any]:
    name = _normalize_name(lead)
    return {
        "id": _safe_text(lead.get("ID")),
        "title_hash": _hash_key(_safe_text(lead.get("TITLE"))) if _safe_text(lead.get("TITLE")) else "",
        "name_status": _name_status(lead),
        "name_hash": _hash_key(name) if name else "",
        "phones": _item_masks(lead, "PHONE", _mask_phone),
        "emails": _item_masks(lead, "EMAIL", _mask_email),
        "status_id": _safe_text(lead.get("STATUS_ID")),
        "status": lead_status_map.get(_safe_text(lead.get("STATUS_ID")), ""),
        "source_id": _safe_text(lead.get("SOURCE_ID")),
        "source": source_map.get(_safe_text(lead.get("SOURCE_ID")), ""),
        "created": _safe_text(lead.get("DATE_CREATE"))[:19],
        "modified": _safe_text(lead.get("DATE_MODIFY"))[:19],
    }


def _classify_lead_group(match_type: str, key: str) -> dict[str, str]:
    if match_type == "email" and _email_domain(key) in SERVICE_EMAIL_DOMAINS:
        return {
            "risk": "high",
            "decision_hint": "do_not_merge_by_service_email",
            "why": "Email похож на адрес площадки/уведомлений. Такие лиды могут быть разными заявками.",
        }
    if match_type == "phone":
        return {
            "risk": "medium",
            "decision_hint": "same_person_or_repeat_request",
            "why": "Совпадает телефон. Проверить: это повторная заявка того же человека или дубль одной заявки.",
        }
    return {
        "risk": "medium",
        "decision_hint": "review_before_merge",
        "why": "Совпадает email. Проверить источник и текст заявки перед любым объединением.",
    }


def _build_lead_groups(
    leads: list[dict[str, Any]],
    lead_status_map: dict[str, str],
    source_map: dict[str, str],
) -> list[dict[str, Any]]:
    groups = []
    lead_map = _make_maps(leads)
    for match_type, buckets, mask_fn in [
        ("phone", _bucket_rows(leads, "PHONE", _phone_key), _mask_phone),
        ("email", _bucket_rows(leads, "EMAIL", _email_key), _mask_email),
    ]:
        for key, ids in buckets.items():
            unique_ids = sorted(set(ids), key=lambda value: int(value) if value.isdigit() else value)
            rows = [lead_map[row_id] for row_id in unique_ids if row_id in lead_map]
            classification = _classify_lead_group(match_type, key)
            groups.append(
                {
                    "group_id": f"lead_{match_type}_{_hash_key(key)}",
                    "entity": "lead",
                    "match_type": match_type,
                    "matched_value": mask_fn(key),
                    "record_count": len(unique_ids),
                    **classification,
                    "record_ids": unique_ids,
                    "records": [_lead_card(row, lead_status_map, source_map) for row in rows],
                }
            )

    priority = {"phone": 0, "email": 1}
    return sorted(groups, key=lambda item: (priority.get(item["match_type"], 9), -item["record_count"]))


def _build_empty_contact_queue(
    contacts: list[dict[str, Any]],
    deals_by_contact: dict[str, list[dict[str, Any]]],
    status_map: dict[str, str],
    source_map: dict[str, str],
) -> list[dict[str, Any]]:
    queue = []
    for contact in contacts:
        phones = _item_values(contact, "PHONE", _phone_key)
        emails = _item_values(contact, "EMAIL", _email_key)
        if phones or emails:
            continue
        contact_id = _safe_text(contact.get("ID"))
        deals = deals_by_contact.get(contact_id, [])
        queue.append(
            {
                "id": contact_id,
                "name_status": _name_status(contact),
                "name_hash": _hash_key(_normalize_name(contact)) if _normalize_name(contact) else "",
                "company_id": _safe_text(contact.get("COMPANY_ID")),
                "assigned_by_id": _safe_text(contact.get("ASSIGNED_BY_ID")),
                "created": _safe_text(contact.get("DATE_CREATE"))[:19],
                "modified": _safe_text(contact.get("DATE_MODIFY"))[:19],
                "linked_deals": _summarize_deals(deals, status_map, source_map),
                "suggested_action": "keep_and_fill" if deals else "archive_or_delete_after_manual_check",
            }
        )
    return sorted(queue, key=lambda item: (-item["linked_deals"]["count"], item["id"]))


def build_review(
    contacts: list[dict[str, Any]],
    leads: list[dict[str, Any]],
    deals: list[dict[str, Any]],
    statuses: list[dict[str, Any]],
    sources: list[dict[str, Any]],
) -> dict[str, Any]:
    lead_status_map, status_map = _status_maps(statuses)
    source_map = {_safe_text(row.get("STATUS_ID")): _safe_text(row.get("NAME")) for row in sources}
    contact_map = _make_maps(contacts)
    deals_by_contact = _index_deals_by_contact(deals)
    leads_by_phone = _index_rows_by_field(leads, "PHONE", _phone_key)
    leads_by_email = _index_rows_by_field(leads, "EMAIL", _email_key)

    contact_groups = _build_contact_groups(
        contacts,
        deals_by_contact,
        leads_by_phone,
        leads_by_email,
        contact_map,
        lead_status_map,
        status_map,
        source_map,
    )
    lead_groups = _build_lead_groups(leads, lead_status_map, source_map)
    empty_contacts = _build_empty_contact_queue(contacts, deals_by_contact, status_map, source_map)

    high_priority = [
        group
        for group in contact_groups
        if group["match_type"] in {"phone", "email"}
        and group["decision_hint"] not in {"do_not_merge_by_email_only"}
    ][:25]

    return {
        "audit_type": "bitrix24_duplicate_review_readonly",
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "readonly": True,
        "personal_data_policy": "phones/emails are masked; names are hashed/status-only",
        "counts": {
            "contacts": len(contacts),
            "leads": len(leads),
            "deals": len(deals),
            "contact_duplicate_groups": len(contact_groups),
            "lead_duplicate_groups": len(lead_groups),
            "empty_contacts": len(empty_contacts),
        },
        "next_manual_queue": high_priority,
        "contact_duplicate_groups": contact_groups,
        "lead_duplicate_groups": lead_groups,
        "empty_contact_queue": empty_contacts,
        "rules": [
            "Сильный дубль: совпал телефон или обычный email, плюс история указывает на одного человека.",
            "Слабый дубль: совпало только имя. Не объединять без телефона/email.",
            "Сервисный email площадки не доказывает дубль клиента.",
            "Главной карточкой обычно выбирать контакт с большим числом сделок, свежей историей и заполненными каналами связи.",
        ],
    }


def render_markdown(review: dict[str, Any]) -> str:
    lines = [
        "# Bitrix24 Duplicate Review",
        "",
        f"Generated: `{review['generated_at']}`",
        "",
        "## Summary",
        "",
        f"- Contacts: `{review['counts']['contacts']}`",
        f"- Leads: `{review['counts']['leads']}`",
        f"- Deals: `{review['counts']['deals']}`",
        f"- Contact duplicate groups: `{review['counts']['contact_duplicate_groups']}`",
        f"- Lead duplicate groups: `{review['counts']['lead_duplicate_groups']}`",
        f"- Empty contacts: `{review['counts']['empty_contacts']}`",
        "",
        "## First Manual Queue",
        "",
    ]
    for group in review["next_manual_queue"][:20]:
        lines.extend(
            [
                f"### {group['group_id']}",
                "",
                f"- Type: `{group['entity']}` / `{group['match_type']}`",
                f"- Matched: `{group['matched_value']}`",
                f"- IDs: `{', '.join(group['record_ids'])}`",
                f"- Decision hint: `{group['decision_hint']}`",
                f"- Why: {group['why']}",
                "",
            ]
        )
        for record in group["records"][:10]:
            lines.append(
                "- "
                + f"ID `{record['id']}`; "
                + f"name `{record['name_status']}`; "
                + f"deals `{record['linked_deals']['count']}`; "
                + f"matched leads `{record['matched_leads_by_phone_or_email']['count']}`; "
                + f"modified `{record['modified']}`"
            )
        lines.append("")

    lines.extend(
        [
            "## Rules",
            "",
            *[f"- {rule}" for rule in review["rules"]],
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detailed read-only Bitrix24 duplicate review")
    parser.add_argument("--limit-pages", type=int, default=None)
    parser.add_argument("--json-output", type=Path, default=JSON_REPORT_PATH)
    parser.add_argument("--md-output", type=Path, default=MD_REPORT_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    load_dotenv(PROJECT_ROOT / ".env")
    webhook_url = _safe_text(__import__("os").getenv("BITRIX24_WEBHOOK_URL"))
    try:
        client = BitrixReadonlyClient(webhook_url)
        contacts = _read_contacts(client, args.limit_pages)
        leads = _read_leads(client, args.limit_pages)
        deals = _read_deals(client, args.limit_pages)
        statuses = _read_statuses_all(client)
        sources = client.list_all("crm.status.list", {"filter[ENTITY_ID]": "SOURCE"})
        review = build_review(contacts, leads, deals, statuses, sources)
    except Exception as exc:
        print("bitrix_duplicate_review_status=FAILED", file=sys.stderr)
        print(f"reason={exc}", file=sys.stderr)
        return 1

    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.md_output.write_text(render_markdown(review) + "\n", encoding="utf-8")

    print("bitrix_duplicate_review_status=OK")
    print(f"contacts={review['counts']['contacts']}")
    print(f"leads={review['counts']['leads']}")
    print(f"deals={review['counts']['deals']}")
    print(f"contact_duplicate_groups={review['counts']['contact_duplicate_groups']}")
    print(f"lead_duplicate_groups={review['counts']['lead_duplicate_groups']}")
    print(f"empty_contacts={review['counts']['empty_contacts']}")
    print(f"json_report={args.json_output.relative_to(PROJECT_ROOT)}")
    print(f"md_report={args.md_output.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
