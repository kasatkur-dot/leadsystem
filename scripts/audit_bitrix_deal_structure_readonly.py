"""Read-only Bitrix24 deal structure audit.

This script reads Bitrix24 CRM metadata needed before enabling `crm.deal.add`.
It does not create, update, close, merge, or delete CRM entities.
It never prints or writes webhook values.
"""

from __future__ import annotations

import json
import os
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = PROJECT_ROOT / "data" / "reports" / "bitrix_deal_structure_readonly.json"


REQUIRED_DEAL_FIELDS = [
    "TITLE",
    "TYPE_ID",
    "STAGE_ID",
    "SOURCE_ID",
    "COMMENTS",
    "CATEGORY_ID",
    "ASSIGNED_BY_ID",
]

TARGET_CUSTOM_FIELDS = [
    "UF_CRM_VPP_SITE_SRC",
    "UF_CRM_VPP_FLOW",
    "UF_CRM_VPP_SCORE",
    "UF_CRM_VPP_OBJ_TYPE",
    "UF_CRM_VPP_AREA_M2",
    "UF_CRM_VPP_FIRST_CH",
    "UF_CRM_VPP_LAST_CH",
    "UF_CRM_VPP_LAND_URL",
    "UF_CRM_VPP_AI_STATUS",
]

READONLY_METHODS = {
    "crm.deal.fields",
    "crm.status.list",
    "crm.dealcategory.list",
    "crm.deal.list",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _safe_text(value: Any) -> str:
    return "" if value is None else str(value).strip()


class BitrixReadonlyClient:
    def __init__(self, webhook_url: str, timeout: int = 20) -> None:
        webhook_url = webhook_url.strip().strip("\"'")
        if not webhook_url:
            raise RuntimeError("BITRIX24_WEBHOOK_URL is EMPTY")
        self.base_url = webhook_url.rstrip("/") + "/"
        self.timeout = timeout
        self.methods_called: list[str] = []

    def call(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if method not in READONLY_METHODS:
            raise RuntimeError(f"Blocked non-readonly Bitrix24 method: {method}")
        self.methods_called.append(method)
        body = urlencode(params or {}, doseq=True).encode("utf-8")
        request = Request(
            self.base_url + method + ".json",
            data=body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "vpp-bitrix-deal-structure-readonly/1.0",
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
        *,
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


def _read_deal_fields(client: BitrixReadonlyClient) -> dict[str, Any]:
    result = client.call("crm.deal.fields").get("result")
    if not isinstance(result, dict):
        raise RuntimeError("crm.deal.fields returned unexpected result")
    return result


def _read_statuses(client: BitrixReadonlyClient, entity_id: str) -> list[dict[str, Any]]:
    return client.list_all("crm.status.list", {"filter[ENTITY_ID]": entity_id})


def _read_categories(client: BitrixReadonlyClient) -> list[dict[str, Any]]:
    try:
        return client.list_all("crm.dealcategory.list")
    except Exception as exc:
        return [{"read_status": "FAILED", "reason": str(exc)}]


def _read_recent_deals(client: BitrixReadonlyClient) -> list[dict[str, Any]]:
    return client.list_all(
        "crm.deal.list",
        {
            "select[]": [
                "ID",
                "STAGE_ID",
                "CATEGORY_ID",
                "ASSIGNED_BY_ID",
                "SOURCE_ID",
                "DATE_MODIFY",
            ],
            "order[DATE_MODIFY]": "DESC",
        },
        limit_pages=2,
    )


def _field_summary(fields: dict[str, Any], field_id: str) -> dict[str, Any]:
    meta = fields.get(field_id) or {}
    return {
        "field_id": field_id,
        "status": "FOUND" if field_id in fields else "MISSING",
        "type": _safe_text(meta.get("type")),
        "title": _safe_text(meta.get("title") or meta.get("formLabel") or meta.get("listLabel")),
        "is_required": bool(meta.get("isRequired")),
        "is_read_only": bool(meta.get("isReadOnly")),
    }


def _statuses_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": _safe_text(row.get("STATUS_ID")),
            "name": _safe_text(row.get("NAME")),
            "sort": _safe_text(row.get("SORT")),
        }
        for row in rows
    ]


def build_report(
    *,
    env_status: dict[str, str],
    deal_fields: dict[str, Any],
    sources: list[dict[str, Any]],
    categories: list[dict[str, Any]],
    stages_by_entity: dict[str, list[dict[str, Any]]],
    recent_deals: list[dict[str, Any]],
    methods_called: list[str],
) -> dict[str, Any]:
    required = [_field_summary(deal_fields, field_id) for field_id in REQUIRED_DEAL_FIELDS]
    target_custom = [_field_summary(deal_fields, field_id) for field_id in TARGET_CUSTOM_FIELDS]
    all_custom = [
        _field_summary(deal_fields, field_id)
        for field_id in sorted(field_id for field_id in deal_fields if field_id.startswith("UF_CRM_"))
    ]

    recent_category_ids = sorted({_safe_text(row.get("CATEGORY_ID")) for row in recent_deals if _safe_text(row.get("CATEGORY_ID"))})
    recent_assigned_ids = Counter(_safe_text(row.get("ASSIGNED_BY_ID")) or "EMPTY" for row in recent_deals)
    recent_source_ids = Counter(_safe_text(row.get("SOURCE_ID")) or "EMPTY" for row in recent_deals)
    recent_stage_ids = Counter(_safe_text(row.get("STAGE_ID")) or "EMPTY" for row in recent_deals)

    source_ids = {_safe_text(row.get("STATUS_ID")) for row in sources}
    target_source_status = {
        source_id: ("FOUND" if source_id in source_ids else "MISSING")
        for source_id in ["CALL", "EMAIL", "WEB", "2|MAX", "12|MAX_NUMBER_REDHAM", "2|TELEGRAM", "6|TELEGRAM_UNLIM"]
    }

    missing_required = [item["field_id"] for item in required if item["status"] == "MISSING"]
    missing_target_custom = [item["field_id"] for item in target_custom if item["status"] == "MISSING"]

    return {
        "audit_type": "bitrix24_deal_structure_readonly",
        "generated_at": _utc_now(),
        "readonly": True,
        "env_status": env_status,
        "methods_called": sorted(set(methods_called)),
        "external_calls": {
            "bitrix24_readonly": True,
            "bitrix24_write": False,
            "redis": False,
            "telegram_send": False,
            "imap": False,
            "llm": False,
            "scheduler": False,
            "publisher": False,
        },
        "deal_fields_status": "OK" if not missing_required else "MISSING_REQUIRED",
        "required_deal_fields": required,
        "target_custom_fields_status": "OK" if not missing_target_custom else "NEEDS_CONFIRMATION",
        "target_custom_fields": target_custom,
        "missing_target_custom_fields": missing_target_custom,
        "all_custom_deal_fields_count": len(all_custom),
        "all_custom_deal_fields": all_custom,
        "sources_count": len(sources),
        "target_source_status": target_source_status,
        "sources": _statuses_summary(sources),
        "categories_read_status": "FAILED" if categories and categories[0].get("read_status") == "FAILED" else "OK",
        "categories": [
            {
                "id": _safe_text(row.get("ID")),
                "name": _safe_text(row.get("NAME")),
                "sort": _safe_text(row.get("SORT")),
                "is_default": bool(row.get("IS_DEFAULT")),
            }
            if not row.get("read_status")
            else row
            for row in categories
        ],
        "stages_by_entity": {
            entity_id: _statuses_summary(rows) for entity_id, rows in stages_by_entity.items()
        },
        "recent_deals_sample_count": len(recent_deals),
        "recent_category_ids": recent_category_ids,
        "recent_assigned_by_ids": [
            {"assigned_by_id": key, "count": value} for key, value in recent_assigned_ids.most_common()
        ],
        "recent_source_ids": [
            {"source_id": key, "count": value} for key, value in recent_source_ids.most_common()
        ],
        "recent_stage_ids": [
            {"stage_id": key, "count": value} for key, value in recent_stage_ids.most_common()
        ],
        "must_confirm_before_real_send": [
            "какую воронку использовать: CATEGORY_ID",
            "какую первую стадию использовать: STAGE_ID",
            "какой Bitrix24-пользователь будет ASSIGNED_BY_ID для AI-сделок",
            "какой SOURCE_ID реально ставят Open Lines для MAX",
            "какой SOURCE_ID реально ставят Open Lines для Telegram",
            "создавать ли недостающие пользовательские поля UF_CRM_* или временно писать их в COMMENTS",
            "как связывать контакт: CONTACT_ID/COMPANY_ID или ручная обработка первого касания",
        ],
    }


def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env")
    webhook_url = os.getenv("BITRIX24_WEBHOOK_URL", "")
    env_status = {"BITRIX24_WEBHOOK_URL": "SET" if webhook_url.strip() else "EMPTY"}
    if env_status["BITRIX24_WEBHOOK_URL"] != "SET":
        print("bitrix_deal_structure_status=FAILED")
        print("BITRIX24_WEBHOOK_URL=EMPTY")
        return 1

    try:
        client = BitrixReadonlyClient(webhook_url)
        deal_fields = _read_deal_fields(client)
        sources = _read_statuses(client, "SOURCE")
        categories = _read_categories(client)
        recent_deals = _read_recent_deals(client)

        stage_entities = ["DEAL_STAGE"]
        category_ids = [
            _safe_text(row.get("ID"))
            for row in categories
            if not row.get("read_status") and _safe_text(row.get("ID"))
        ]
        stage_entities.extend(f"DEAL_STAGE_{category_id}" for category_id in category_ids if category_id != "0")
        for category_id in sorted({_safe_text(row.get("CATEGORY_ID")) for row in recent_deals if _safe_text(row.get("CATEGORY_ID"))}):
            entity_id = "DEAL_STAGE" if category_id == "0" else f"DEAL_STAGE_{category_id}"
            if entity_id not in stage_entities:
                stage_entities.append(entity_id)

        stages_by_entity: dict[str, list[dict[str, Any]]] = {}
        for entity_id in stage_entities:
            try:
                stages_by_entity[entity_id] = _read_statuses(client, entity_id)
            except Exception as exc:
                stages_by_entity[entity_id] = [{"STATUS_ID": "READ_FAILED", "NAME": str(exc), "SORT": ""}]

        report = build_report(
            env_status=env_status,
            deal_fields=deal_fields,
            sources=sources,
            categories=categories,
            stages_by_entity=stages_by_entity,
            recent_deals=recent_deals,
            methods_called=client.methods_called,
        )
    except Exception as exc:
        print("bitrix_deal_structure_status=FAILED")
        print(f"reason={exc}")
        return 1

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("bitrix_deal_structure_status=OK")
    print("BITRIX24_WEBHOOK_URL=SET")
    print(f"deal_fields_status={report['deal_fields_status']}")
    print(f"target_custom_fields_status={report['target_custom_fields_status']}")
    print(f"missing_target_custom_fields={json.dumps(report['missing_target_custom_fields'], ensure_ascii=False)}")
    print(f"sources_count={report['sources_count']}")
    print(f"categories_read_status={report['categories_read_status']}")
    print(f"recent_deals_sample_count={report['recent_deals_sample_count']}")
    print(f"recent_category_ids={json.dumps(report['recent_category_ids'], ensure_ascii=False)}")
    print(f"recent_assigned_by_ids={json.dumps(report['recent_assigned_by_ids'], ensure_ascii=False)}")
    print(f"report_file={REPORT_PATH.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
