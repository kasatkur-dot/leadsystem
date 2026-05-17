"""Create missing Bitrix24 deal custom fields for VPP lead automation.

Default mode is dry-run. It only reads `crm.deal.fields` and writes a local
report. Actual Bitrix24 changes happen only with `--execute`.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = PROJECT_ROOT / "data" / "reports" / "bitrix_deal_custom_fields_sync.json"

FIELD_SPECS: list[dict[str, Any]] = [
    {
        "actual_id": "UF_CRM_VPP_SITE_SRC",
        "FIELD_NAME": "VPP_SITE_SRC",
        "USER_TYPE_ID": "string",
        "LABEL": "ВПП: сайтовый источник",
        "SORT": 510,
    },
    {
        "actual_id": "UF_CRM_VPP_FLOW",
        "FIELD_NAME": "VPP_FLOW",
        "USER_TYPE_ID": "enumeration",
        "LABEL": "ВПП: поток",
        "SORT": 520,
        "LIST": [
            {"VALUE": "A — перепланировки", "XML_ID": "A"},
            {"VALUE": "B — проектирование", "XML_ID": "B"},
        ],
    },
    {
        "actual_id": "UF_CRM_VPP_SCORE",
        "FIELD_NAME": "VPP_SCORE",
        "USER_TYPE_ID": "enumeration",
        "LABEL": "ВПП: скор",
        "SORT": 530,
        "LIST": [
            {"VALUE": "hot", "XML_ID": "hot"},
            {"VALUE": "warm", "XML_ID": "warm"},
            {"VALUE": "cold", "XML_ID": "cold"},
            {"VALUE": "off", "XML_ID": "off"},
        ],
    },
    {
        "actual_id": "UF_CRM_VPP_OBJ_TYPE",
        "FIELD_NAME": "VPP_OBJ_TYPE",
        "USER_TYPE_ID": "string",
        "LABEL": "ВПП: тип объекта",
        "SORT": 540,
    },
    {
        "actual_id": "UF_CRM_VPP_AREA_M2",
        "FIELD_NAME": "VPP_AREA_M2",
        "USER_TYPE_ID": "double",
        "LABEL": "ВПП: площадь м2",
        "SORT": 550,
    },
    {
        "actual_id": "UF_CRM_VPP_FIRST_CH",
        "FIELD_NAME": "VPP_FIRST_CH",
        "USER_TYPE_ID": "string",
        "LABEL": "ВПП: первое касание",
        "SORT": 560,
    },
    {
        "actual_id": "UF_CRM_VPP_LAST_CH",
        "FIELD_NAME": "VPP_LAST_CH",
        "USER_TYPE_ID": "string",
        "LABEL": "ВПП: последнее касание",
        "SORT": 570,
    },
    {
        "actual_id": "UF_CRM_VPP_LAND_URL",
        "FIELD_NAME": "VPP_LAND_URL",
        "USER_TYPE_ID": "string",
        "LABEL": "ВПП: страница входа",
        "SORT": 580,
    },
    {
        "actual_id": "UF_CRM_VPP_AI_STATUS",
        "FIELD_NAME": "VPP_AI_STATUS",
        "USER_TYPE_ID": "string",
        "LABEL": "ВПП: статус AI-менеджера",
        "SORT": 590,
    },
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


class BitrixFieldSyncClient:
    def __init__(self, webhook_url: str, timeout: int = 20) -> None:
        webhook_url = webhook_url.strip().strip("\"'")
        if not webhook_url:
            raise RuntimeError("BITRIX24_WEBHOOK_URL is EMPTY")
        self.base_url = webhook_url.rstrip("/") + "/"
        self.timeout = timeout
        self.methods_called: list[str] = []

    def call_json(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self.methods_called.append(method)
        request = Request(
            self.base_url + method + ".json",
            data=json.dumps(params or {}, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "vpp-bitrix-deal-custom-field-sync/1.0",
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


def _read_deal_fields(client: BitrixFieldSyncClient) -> dict[str, Any]:
    result = client.call_json("crm.deal.fields").get("result")
    if not isinstance(result, dict):
        raise RuntimeError("crm.deal.fields returned unexpected result")
    return result


def _field_add_payload(spec: dict[str, Any]) -> dict[str, Any]:
    fields: dict[str, Any] = {
        "FIELD_NAME": spec["FIELD_NAME"],
        "USER_TYPE_ID": spec["USER_TYPE_ID"],
        "LABEL": spec["LABEL"],
        "EDIT_FORM_LABEL": spec["LABEL"],
        "LIST_COLUMN_LABEL": spec["LABEL"],
        "LIST_FILTER_LABEL": spec["LABEL"],
        "SORT": spec["SORT"],
        "MULTIPLE": "N",
        "MANDATORY": "N",
        "SHOW_FILTER": "Y",
        "SHOW_IN_LIST": "Y",
    }
    if spec.get("LIST"):
        fields["LIST"] = spec["LIST"]
    return {"fields": fields}


def run(*, execute: bool) -> dict[str, Any]:
    load_dotenv(PROJECT_ROOT / ".env")
    webhook_url = os.getenv("BITRIX24_WEBHOOK_URL", "")
    env_status = {"BITRIX24_WEBHOOK_URL": "SET" if webhook_url.strip() else "EMPTY"}
    if env_status["BITRIX24_WEBHOOK_URL"] != "SET":
        raise RuntimeError("BITRIX24_WEBHOOK_URL is EMPTY")

    client = BitrixFieldSyncClient(webhook_url)
    fields = _read_deal_fields(client)
    existing = set(fields)

    planned: list[dict[str, Any]] = []
    created: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []

    for spec in FIELD_SPECS:
        item = {
            "actual_id": spec["actual_id"],
            "field_name": spec["FIELD_NAME"],
            "type": spec["USER_TYPE_ID"],
            "label": spec["LABEL"],
        }
        if spec["actual_id"] in existing:
            skipped.append({**item, "status": "ALREADY_EXISTS"})
            continue
        planned.append({**item, "status": "MISSING"})
        if execute:
            try:
                result = client.call_json("crm.deal.userfield.add", _field_add_payload(spec))
                created.append({**item, "status": "CREATED", "bitrix_result": result.get("result")})
            except Exception as exc:
                failed.append({**item, "status": "FAILED", "reason": str(exc)})

    result = {
        "sync_type": "bitrix24_deal_custom_fields_sync",
        "generated_at": _utc_now(),
        "dry_run": not execute,
        "execute": execute,
        "env_status": env_status,
        "external_calls": {
            "bitrix24_readonly": True,
            "bitrix24_write": bool(execute and planned),
            "redis": False,
            "telegram_send": False,
            "imap": False,
            "llm": False,
            "scheduler": False,
            "publisher": False,
        },
        "methods_called": sorted(set(client.methods_called)),
        "field_code_rule": "Use compact FIELD_NAME values. Bitrix24 stores them as UF_CRM_<FIELD_NAME>.",
        "fields_total": len(FIELD_SPECS),
        "fields_existing_count": len(skipped),
        "fields_missing_before_sync_count": len(planned),
        "fields_created_count": len(created),
        "fields_failed_count": len(failed),
        "planned_missing_fields": planned,
        "created_fields": created,
        "already_existing_fields": skipped,
        "failed_fields": failed,
        "sync_status": "FAILED" if failed else "OK",
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync Bitrix24 deal custom fields for VPP")
    parser.add_argument("--execute", action="store_true", help="Actually create missing fields in Bitrix24")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = run(execute=args.execute)
    except Exception as exc:
        print("bitrix_deal_custom_fields_sync_status=FAILED")
        print(f"reason={exc}")
        return 1

    print("bitrix_deal_custom_fields_sync_status=" + result["sync_status"])
    print("BITRIX24_WEBHOOK_URL=" + result["env_status"]["BITRIX24_WEBHOOK_URL"])
    print("dry_run=" + str(result["dry_run"]))
    print("execute=" + str(result["execute"]))
    print("fields_total=" + str(result["fields_total"]))
    print("fields_existing_count=" + str(result["fields_existing_count"]))
    print("fields_missing_before_sync_count=" + str(result["fields_missing_before_sync_count"]))
    print("fields_created_count=" + str(result["fields_created_count"]))
    print("fields_failed_count=" + str(result["fields_failed_count"]))
    print("report_file=" + str(REPORT_PATH.relative_to(PROJECT_ROOT)))
    return 0 if result["sync_status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
