"""Controlled one-deal Bitrix24 test for Agent 5.

Default mode is dry-run. Real Bitrix24 creation happens only with
`--execute` and uses the local synthetic QualifiedLead artifact.
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
sys.path.insert(0, str(PROJECT_ROOT))

from agents.agent5_crm.deal_payload_builder import build_deal_payload, redact_payload_for_report
from shared.models import QualifiedLead


INPUT_PATH = PROJECT_ROOT / "data" / "reports" / "first_inbound_qualified_lead_dry_run.json"
REPORT_PATH = PROJECT_ROOT / "data" / "reports" / "agent5_bitrix_deal_test.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


class BitrixDealTestClient:
    def __init__(self, webhook_url: str, timeout: int = 20) -> None:
        webhook_url = webhook_url.strip().strip("\"'")
        if not webhook_url:
            raise RuntimeError("BITRIX24_WEBHOOK_URL is EMPTY")
        self.base_url = webhook_url.rstrip("/") + "/"
        self.timeout = timeout
        self.methods_called: list[str] = []

    def call_json(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        self.methods_called.append(method)
        request = Request(
            self.base_url + method + ".json",
            data=json.dumps(params, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "vpp-agent5-bitrix-deal-test/1.0",
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


def _read_qualified_lead(path: Path) -> QualifiedLead:
    data = json.loads(path.read_text(encoding="utf-8"))
    return QualifiedLead.model_validate(data["output"])


def _prepare_test_payload(lead: QualifiedLead) -> dict[str, Any]:
    payload = build_deal_payload(lead)
    fields = payload["params"]["fields"]
    test_marker = "TEST_AGENT5_DEAL_2026_05_16"

    fields["TITLE"] = "[TEST] " + str(fields["TITLE"])
    fields["ORIGINATOR_ID"] = "design-studio-lead-engine"
    fields["ORIGIN_ID"] = test_marker
    fields["SOURCE_DESCRIPTION"] = "Тест Agent 5. Не реальный клиент."
    fields["COMMENTS"] = (
        "ТЕСТОВАЯ СДЕЛКА. НЕ РЕАЛЬНЫЙ КЛИЕНТ.\n"
        "Создано по разрешению Яники для проверки crm.deal.add.\n"
        "После проверки можно удалить вручную в Bitrix24, если не нужна в истории.\n\n"
        + str(fields["COMMENTS"])
    )
    return payload


def run(*, execute: bool) -> dict[str, Any]:
    load_dotenv(PROJECT_ROOT / ".env")
    webhook_url = os.getenv("BITRIX24_WEBHOOK_URL", "")
    env_status = {"BITRIX24_WEBHOOK_URL": "SET" if webhook_url.strip() else "EMPTY"}
    if env_status["BITRIX24_WEBHOOK_URL"] != "SET":
        raise RuntimeError("BITRIX24_WEBHOOK_URL is EMPTY")

    lead = _read_qualified_lead(INPUT_PATH)
    payload = _prepare_test_payload(lead)
    safe_payload = redact_payload_for_report(payload, lead.contact)
    client = BitrixDealTestClient(webhook_url)

    bitrix_status = "DRY_RUN_NOT_SENT"
    bitrix_id: str | None = None
    verify_status = "SKIPPED"
    verified_fields: dict[str, Any] = {}
    error: str | None = None

    if execute:
        try:
            result = client.call_json("crm.deal.add", {"fields": payload["params"]["fields"]})
            bitrix_id = str(result.get("result"))
            bitrix_status = "OK" if bitrix_id and bitrix_id != "None" else "FAILED"
            if bitrix_status == "OK":
                verify = client.call_json("crm.deal.get", {"id": bitrix_id})
                deal = verify.get("result") or {}
                verify_status = "OK" if str(deal.get("ID")) == bitrix_id else "FAILED"
                verified_fields = {
                    "ID": str(deal.get("ID")),
                    "TITLE": str(deal.get("TITLE")),
                    "CATEGORY_ID": str(deal.get("CATEGORY_ID")),
                    "STAGE_ID": str(deal.get("STAGE_ID")),
                    "ASSIGNED_BY_ID": str(deal.get("ASSIGNED_BY_ID")),
                    "SOURCE_ID": str(deal.get("SOURCE_ID")),
                    "UF_CRM_VPP_SITE_SRC": str(deal.get("UF_CRM_VPP_SITE_SRC")),
                    "UF_CRM_VPP_FLOW": str(deal.get("UF_CRM_VPP_FLOW")),
                    "UF_CRM_VPP_SCORE": str(deal.get("UF_CRM_VPP_SCORE")),
                }
        except Exception as exc:
            bitrix_status = "FAILED"
            error = str(exc)

    report = {
        "test_type": "agent5_bitrix_deal_create_test",
        "created_at": _utc_now(),
        "dry_run": not execute,
        "execute": execute,
        "input_file": str(INPUT_PATH.relative_to(PROJECT_ROOT)),
        "env_status": env_status,
        "external_calls": {
            "bitrix24_attempted": execute,
            "bitrix24_created": bool(execute and bitrix_status == "OK"),
            "bitrix24_verified": bool(execute and verify_status == "OK"),
            "redis": False,
            "telegram_send": False,
            "imap": False,
            "llm": False,
            "scheduler": False,
            "publisher": False,
        },
        "methods_called": sorted(set(client.methods_called)),
        "bitrix_method": "crm.deal.add",
        "bitrix_send_status": bitrix_status,
        "bitrix_verify_status": verify_status,
        "bitrix_id": bitrix_id,
        "error": error,
        "payload_preview": safe_payload,
        "verified_fields": verified_fields,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one safe Bitrix24 deal create test")
    parser.add_argument("--execute", action="store_true", help="Actually create one test deal in Bitrix24")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = run(execute=args.execute)
    except Exception as exc:
        print("bitrix_deal_test_status=FAILED")
        print(f"reason={exc}")
        return 1

    print("bitrix_deal_test_status=" + ("OK" if result["bitrix_send_status"] == "OK" else result["bitrix_send_status"]))
    print("BITRIX24_WEBHOOK_URL=" + result["env_status"]["BITRIX24_WEBHOOK_URL"])
    print("execute=" + str(result["execute"]))
    print("bitrix_method=" + result["bitrix_method"])
    print("bitrix_send_status=" + result["bitrix_send_status"])
    print("bitrix_verify_status=" + result["bitrix_verify_status"])
    print("bitrix_id=" + str(result["bitrix_id"]))
    print(
        "external_calls="
        + ",".join(f"{key}:{value}" for key, value in result["external_calls"].items())
    )
    print("report_file=" + str(REPORT_PATH.relative_to(PROJECT_ROOT)))
    return 0 if result["bitrix_send_status"] in {"OK", "DRY_RUN_NOT_SENT"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
