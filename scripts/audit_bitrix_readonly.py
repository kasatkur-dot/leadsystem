"""Read-only Bitrix24 CRM audit.

The script does not create, update, merge, or delete anything in Bitrix24.
It reads contacts, leads, deals, and status dictionaries through the webhook
from `.env`, masks personal contact values, and writes a local JSON report.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = PROJECT_ROOT / "data" / "reports" / "bitrix_readonly_audit.json"


def _safe_text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _phone_key(value: Any) -> str:
    digits = re.sub(r"\D+", "", _safe_text(value))
    if digits.startswith("8") and len(digits) == 11:
        digits = "7" + digits[1:]
    return digits if len(digits) >= 10 else ""


def _email_key(value: Any) -> str:
    return _safe_text(value).lower()


def _mask_phone(value: Any) -> str:
    digits = _phone_key(value)
    if not digits:
        return ""
    return "*" * max(0, len(digits) - 4) + digits[-4:]


def _mask_email(value: Any) -> str:
    email = _email_key(value)
    if "@" not in email:
        return email
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        return "***@" + domain
    return local[:2] + "***@" + domain


def _hash_key(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def _contact_name(contact: dict[str, Any]) -> str:
    parts = [
        _safe_text(contact.get("LAST_NAME")),
        _safe_text(contact.get("NAME")),
        _safe_text(contact.get("SECOND_NAME")),
    ]
    return " ".join(part for part in parts if part).strip()


class BitrixReadonlyClient:
    def __init__(self, webhook_url: str, timeout: int = 20) -> None:
        webhook_url = webhook_url.strip().strip("\"'")
        if not webhook_url:
            raise RuntimeError("BITRIX24_WEBHOOK_URL is empty")
        self.base_url = webhook_url.rstrip("/") + "/"
        self.timeout = timeout

    def call(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        params = params or {}
        body = urlencode(params, doseq=True).encode("utf-8")
        request = Request(
            self.base_url + method + ".json",
            data=body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "vpp-bitrix-readonly-audit/1.0",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8", errors="replace"))
        except HTTPError as exc:
            raise RuntimeError(f"HTTP {exc.code} for {method}") from exc
        except URLError as exc:
            raise RuntimeError(f"Network error for {method}: {exc.reason}") from exc

        if data.get("error"):
            raise RuntimeError(f"{method}: {data.get('error')} - {data.get('error_description')}")
        return data

    def list_all(
        self,
        method: str,
        params: dict[str, Any] | None = None,
        limit_pages: int | None = None,
    ) -> list[dict[str, Any]]:
        params = dict(params or {})
        start: int | str = 0
        rows: list[dict[str, Any]] = []
        pages = 0

        while True:
            page_params = dict(params)
            page_params["start"] = start
            data = self.call(method, page_params)
            result = data.get("result") or []
            if not isinstance(result, list):
                raise RuntimeError(f"{method}: expected list result, got {type(result).__name__}")

            rows.extend(result)
            pages += 1
            if limit_pages and pages >= limit_pages:
                break

            next_start = data.get("next")
            if next_start is None:
                break
            start = next_start
            time.sleep(0.25)

        return rows


def _read_contacts(client: BitrixReadonlyClient, limit_pages: int | None) -> list[dict[str, Any]]:
    return client.list_all(
        "crm.contact.list",
        {
            "select[]": [
                "ID",
                "NAME",
                "LAST_NAME",
                "SECOND_NAME",
                "PHONE",
                "EMAIL",
                "DATE_CREATE",
                "DATE_MODIFY",
                "ASSIGNED_BY_ID",
                "COMPANY_ID",
            ],
            "order[DATE_MODIFY]": "DESC",
        },
        limit_pages=limit_pages,
    )


def _read_leads(client: BitrixReadonlyClient, limit_pages: int | None) -> list[dict[str, Any]]:
    return client.list_all(
        "crm.lead.list",
        {
            "select[]": [
                "ID",
                "TITLE",
                "NAME",
                "LAST_NAME",
                "PHONE",
                "EMAIL",
                "STATUS_ID",
                "SOURCE_ID",
                "DATE_CREATE",
                "DATE_MODIFY",
                "ASSIGNED_BY_ID",
                "COMPANY_TITLE",
                "OPPORTUNITY",
                "CURRENCY_ID",
            ],
            "order[DATE_MODIFY]": "DESC",
        },
        limit_pages=limit_pages,
    )


def _read_deals(client: BitrixReadonlyClient, limit_pages: int | None) -> list[dict[str, Any]]:
    return client.list_all(
        "crm.deal.list",
        {
            "select[]": [
                "ID",
                "TITLE",
                "STAGE_ID",
                "CATEGORY_ID",
                "CONTACT_ID",
                "COMPANY_ID",
                "DATE_CREATE",
                "DATE_MODIFY",
                "ASSIGNED_BY_ID",
                "OPPORTUNITY",
                "CURRENCY_ID",
                "SOURCE_ID",
            ],
            "order[DATE_MODIFY]": "DESC",
        },
        limit_pages=limit_pages,
    )


def _read_statuses(client: BitrixReadonlyClient, entity_id: str) -> list[dict[str, Any]]:
    return client.list_all("crm.status.list", {"filter[ENTITY_ID]": entity_id})


def _duplicates_by_contact_field(
    rows: list[dict[str, Any]],
    field: str,
    key_fn,
    mask_fn,
    label: str,
) -> list[dict[str, Any]]:
    buckets: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        for item in row.get(field) or []:
            value = item.get("VALUE")
            key = key_fn(value)
            if key:
                buckets[key].append({"id": _safe_text(row.get("ID"))})

    result = []
    for key, items in buckets.items():
        if len(items) > 1:
            result.append(
                {
                    label: mask_fn(key),
                    "count": len(items),
                    "ids": [item["id"] for item in items[:20]],
                }
            )
    return sorted(result, key=lambda item: item["count"], reverse=True)


def _duplicate_contact_names(contacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, list[str]] = defaultdict(list)
    for contact in contacts:
        name = re.sub(r"\s+", " ", _contact_name(contact).lower()).strip()
        if name:
            buckets[name].append(_safe_text(contact.get("ID")))
    result = []
    for name, ids in buckets.items():
        if len(ids) > 1:
            result.append({"name_hash": _hash_key(name), "count": len(ids), "ids": ids[:20]})
    return sorted(result, key=lambda item: item["count"], reverse=True)


def build_audit(
    contacts: list[dict[str, Any]],
    leads: list[dict[str, Any]],
    deals: list[dict[str, Any]],
    statuses: list[dict[str, Any]],
    sources: list[dict[str, Any]],
    limited: bool,
) -> dict[str, Any]:
    status_map = {_safe_text(row.get("STATUS_ID")): _safe_text(row.get("NAME")) for row in statuses}
    source_map = {_safe_text(row.get("STATUS_ID")): _safe_text(row.get("NAME")) for row in sources}
    active_leads = [
        lead for lead in leads if _safe_text(lead.get("STATUS_ID")) not in {"JUNK", "CONVERTED"}
    ]

    lead_statuses = Counter(_safe_text(lead.get("STATUS_ID")) for lead in leads)
    active_statuses = Counter(_safe_text(lead.get("STATUS_ID")) for lead in active_leads)
    lead_sources = Counter(_safe_text(lead.get("SOURCE_ID")) or "EMPTY" for lead in leads)
    deal_stages = Counter(_safe_text(deal.get("STAGE_ID")) or "EMPTY" for deal in deals)

    missing_lead_sources = sum(1 for lead in leads if not _safe_text(lead.get("SOURCE_ID")))
    missing_lead_contacts = sum(
        1 for lead in leads if not lead.get("PHONE") and not lead.get("EMAIL")
    )
    missing_contact_channels = sum(
        1 for contact in contacts if not contact.get("PHONE") and not contact.get("EMAIL")
    )

    recommendations = []
    if missing_lead_sources:
        recommendations.append("Заполнить SOURCE_ID у лидов без источника, иначе нельзя считать ROMI.")
    if missing_lead_contacts:
        recommendations.append("Разобрать лиды без телефона/email: закрыть мусор или добавить контакт.")
    if missing_contact_channels:
        recommendations.append("Разобрать контакты без телефона/email: они почти бесполезны для продаж.")
    if active_leads:
        recommendations.append("Проверить активные лиды: у каждого должен быть ответственный и следующий шаг.")
    recommendations.append("Перед объединением дублей выгрузить backup и объединять только вручную после проверки.")

    return {
        "audit_type": "bitrix24_readonly",
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "readonly": True,
        "limited_by_pages": limited,
        "personal_data_policy": "phones/emails are masked; duplicate names are hashed",
        "counts": {
            "contacts": len(contacts),
            "leads_total": len(leads),
            "leads_active": len(active_leads),
            "deals_total": len(deals),
            "statuses": len(statuses),
            "sources": len(sources),
        },
        "quality_flags": {
            "leads_without_source": missing_lead_sources,
            "leads_without_phone_or_email": missing_lead_contacts,
            "contacts_without_phone_or_email": missing_contact_channels,
        },
        "lead_statuses": [
            {"status_id": key, "name": status_map.get(key, ""), "count": value}
            for key, value in lead_statuses.most_common()
        ],
        "active_lead_statuses": [
            {"status_id": key, "name": status_map.get(key, ""), "count": value}
            for key, value in active_statuses.most_common()
        ],
        "lead_sources": [
            {"source_id": key, "name": source_map.get(key, ""), "count": value}
            for key, value in lead_sources.most_common()
        ],
        "deal_stages": [
            {"stage_id": key, "count": value} for key, value in deal_stages.most_common()
        ],
        "duplicates": {
            "contacts_by_phone": _duplicates_by_contact_field(
                contacts, "PHONE", _phone_key, _mask_phone, "phone"
            ),
            "contacts_by_email": _duplicates_by_contact_field(
                contacts, "EMAIL", _email_key, _mask_email, "email"
            ),
            "contacts_by_name_hash": _duplicate_contact_names(contacts),
            "leads_by_phone": _duplicates_by_contact_field(
                leads, "PHONE", _phone_key, _mask_phone, "phone"
            ),
            "leads_by_email": _duplicates_by_contact_field(
                leads, "EMAIL", _email_key, _mask_email, "email"
            ),
        },
        "recent_active_leads": [
            {
                "id": _safe_text(lead.get("ID")),
                "status_id": _safe_text(lead.get("STATUS_ID")),
                "status": status_map.get(_safe_text(lead.get("STATUS_ID")), ""),
                "source_id": _safe_text(lead.get("SOURCE_ID")),
                "source": source_map.get(_safe_text(lead.get("SOURCE_ID")), ""),
                "modified": _safe_text(lead.get("DATE_MODIFY"))[:19],
            }
            for lead in active_leads[:50]
        ],
        "recommendations": recommendations,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read-only Bitrix24 CRM audit")
    parser.add_argument(
        "--limit-pages",
        type=int,
        default=None,
        help="Limit pages per entity for a quick check. One page is usually 50 rows.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPORT_PATH,
        help="Path for masked JSON report.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    load_dotenv(PROJECT_ROOT / ".env")
    webhook_url = os.getenv("BITRIX24_WEBHOOK_URL", "")

    try:
        client = BitrixReadonlyClient(webhook_url)
        contacts = _read_contacts(client, args.limit_pages)
        leads = _read_leads(client, args.limit_pages)
        deals = _read_deals(client, args.limit_pages)
        statuses = _read_statuses(client, "STATUS")
        sources = _read_statuses(client, "SOURCE")
        audit = build_audit(
            contacts=contacts,
            leads=leads,
            deals=deals,
            statuses=statuses,
            sources=sources,
            limited=args.limit_pages is not None,
        )
    except Exception as exc:
        print(f"bitrix_readonly_audit_status=FAILED", file=sys.stderr)
        print(f"reason={exc}", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("bitrix_readonly_audit_status=OK")
    print(f"contacts={audit['counts']['contacts']}")
    print(f"leads_total={audit['counts']['leads_total']}")
    print(f"leads_active={audit['counts']['leads_active']}")
    print(f"deals_total={audit['counts']['deals_total']}")
    print(f"contact_phone_duplicate_groups={len(audit['duplicates']['contacts_by_phone'])}")
    print(f"contact_email_duplicate_groups={len(audit['duplicates']['contacts_by_email'])}")
    print(f"lead_phone_duplicate_groups={len(audit['duplicates']['leads_by_phone'])}")
    print(f"lead_email_duplicate_groups={len(audit['duplicates']['leads_by_email'])}")
    print(f"report_file={args.output.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
