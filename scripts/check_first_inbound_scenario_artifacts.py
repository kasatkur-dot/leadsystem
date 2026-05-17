"""Check the local artifacts for the first inbound request scenario.

This script is read-only against runtime services. It reads local JSON dry-run
artifacts and writes JSON/Markdown reports. It does not call Redis, Bitrix24,
Telegram, IMAP, LLM APIs, scheduler, publisher, MAX, VK, or any paid service.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = PROJECT_ROOT / "data" / "reports"

INTAKE_PATH = REPORTS_DIR / "first_inbound_intake_card_dry_run.json"
QUALIFIED_PATH = REPORTS_DIR / "first_inbound_qualified_lead_dry_run.json"
CRM_PREVIEW_PATH = REPORTS_DIR / "first_inbound_crm_payload_preview_dry_run.json"
REPORT_JSON_PATH = REPORTS_DIR / "first_inbound_scenario_artifact_check.json"
REPORT_MD_PATH = REPORTS_DIR / "first_inbound_scenario_artifact_check.md"

SCENARIO_NAME = "Первый входящий запрос"
OK_STATUSES = {"OK", "OK_LOCAL_DRY_RUN", "OK_PREVIEW_ONLY", "DRY_RUN_NOT_SENT", "READY_FOR_MANUAL_REVIEW"}

ARTIFACT_SPECS: list[dict[str, Any]] = [
    {
        "artifact": "intake_card",
        "path": INTAKE_PATH,
        "expected_artifact_name": "intake_card",
        "owner": "AI-менеджер / Agent 5 CRM Router",
        "required_fields": [
            "input.channel",
            "input.raw_message",
            "input.first_touch_channel",
            "input.last_touch_channel",
            "output.intake_card_id",
            "output.lead_source",
            "output.flow",
            "output.city",
            "output.object_type",
            "output.area_m2",
            "output.raw_dialog_summary",
            "output.recommended_first_reply",
            "stage_check.next_step",
        ],
    },
    {
        "artifact": "qualified_lead",
        "path": QUALIFIED_PATH,
        "expected_artifact_name": "qualified_lead",
        "owner": "Agent 3 Processor / Scorer",
        "required_fields": [
            "input.intake_card_id",
            "output.id",
            "output.raw_lead_id",
            "output.source",
            "output.flow",
            "output.contact",
            "output.city",
            "output.object_type",
            "output.area_m2",
            "output.score",
            "output.score_reason",
            "output.offer_text",
            "output.recommended_action",
            "output.first_touch_channel",
            "output.last_touch_channel",
            "stage_check.next_step",
        ],
    },
    {
        "artifact": "crm_payload_preview",
        "path": CRM_PREVIEW_PATH,
        "expected_artifact_name": "crm_payload_preview",
        "owner": "Agent 5 CRM / CRM Router",
        "required_fields": [
            "input.qualified_lead_id",
            "output.crm_payload_status",
            "output.bitrix_send_status",
            "output.bitrix_method",
            "output.fields_preview.TITLE",
            "output.fields_preview.SOURCE_ID",
            "output.fields_preview.UF_CRM_VPP_SITE_SRC",
            "output.fields_preview.UF_CRM_VPP_FLOW",
            "output.fields_preview.UF_CRM_VPP_SCORE",
            "output.fields_preview.UF_CRM_VPP_OBJ_TYPE",
            "output.fields_preview.UF_CRM_VPP_AREA_M2",
            "output.fields_preview.UF_CRM_VPP_FIRST_CH",
            "output.fields_preview.UF_CRM_VPP_LAST_CH",
            "output.fields_preview.UF_CRM_VPP_AI_STATUS",
            "output.fields_to_confirm_before_real_send",
            "stage_check.next_step",
        ],
    },
    {
        "artifact": "human_next_step",
        "path": CRM_PREVIEW_PATH,
        "expected_artifact_name": "crm_payload_preview",
        "owner": "Человек-контролёр",
        "embedded_in": "crm_payload_preview.output.human_handoff",
        "required_fields": [
            "output.human_handoff.owner",
            "output.human_handoff.handoff_status",
            "output.human_handoff.summary",
            "output.human_handoff.recommended_first_action",
        ],
    },
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _relative(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def _read_json(path: Path) -> tuple[dict[str, Any], str]:
    if not path.exists():
        return {}, "MISSING"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"error": str(exc)}, "FAILED_JSON_DECODE"
    if not isinstance(data, dict):
        return {"error": "top-level JSON is not object"}, "FAILED_JSON_TYPE"
    return data, "OK"


def _get_path(data: dict[str, Any], dotted_path: str) -> Any:
    current: Any = data
    for part in dotted_path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def _is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def _external_calls_false(data: dict[str, Any]) -> bool:
    calls = data.get("external_calls")
    if not isinstance(calls, dict):
        return False
    return all(value is False for value in calls.values())


def _stage_status(data: dict[str, Any]) -> str:
    stage_check = data.get("stage_check")
    if isinstance(stage_check, dict):
        return str(stage_check.get("status", "MISSING"))
    human_handoff = _get_path(data, "output.human_handoff")
    if isinstance(human_handoff, dict):
        return str(human_handoff.get("handoff_status", "MISSING"))
    return "MISSING"


def _check_artifact(spec: dict[str, Any]) -> dict[str, Any]:
    path = spec["path"]
    data, json_status = _read_json(path)
    missing_fields = [
        field for field in spec["required_fields"] if not _is_present(_get_path(data, field))
    ]
    artifact_name = data.get("artifact_name")
    scenario = data.get("scenario")
    stage_status = _stage_status(data)

    checks = {
        "file_status": "FOUND" if path.exists() else "MISSING",
        "json_status": json_status,
        "artifact_name_status": "OK"
        if artifact_name == spec["expected_artifact_name"]
        else "FAILED",
        "scenario_status": "OK" if scenario == SCENARIO_NAME else "FAILED",
        "dry_run_status": "OK" if data.get("dry_run") is True else "FAILED",
        "external_calls_status": "OK" if _external_calls_false(data) else "FAILED",
        "stage_status": stage_status,
        "required_fields_status": "OK" if not missing_fields else "FAILED",
    }

    status = "OK" if (
        checks["file_status"] == "FOUND"
        and checks["json_status"] == "OK"
        and checks["artifact_name_status"] == "OK"
        and checks["scenario_status"] == "OK"
        and checks["dry_run_status"] == "OK"
        and checks["external_calls_status"] == "OK"
        and checks["required_fields_status"] == "OK"
        and stage_status in OK_STATUSES
    ) else "FAILED"

    if spec.get("embedded_in") and status == "OK":
        status = "OK_EMBEDDED"

    return {
        "artifact": spec["artifact"],
        "owner": spec["owner"],
        "file": _relative(path),
        "embedded_in": spec.get("embedded_in"),
        "status": status,
        "checks": checks,
        "missing_required_fields": missing_fields,
        "next_step": _get_path(data, "stage_check.next_step")
        or _get_path(data, "output.human_handoff.recommended_first_action")
        or "нет данных",
    }


def _attribution_check(qualified: dict[str, Any], crm: dict[str, Any]) -> dict[str, Any]:
    field_pairs = [
        ("source", "output.source", "output.fields_preview.UF_CRM_VPP_SITE_SRC"),
        ("flow", "output.flow", "output.fields_preview.UF_CRM_VPP_FLOW"),
        ("score", "output.score", "output.fields_preview.UF_CRM_VPP_SCORE"),
        ("object_type", "output.object_type", "output.fields_preview.UF_CRM_VPP_OBJ_TYPE"),
        ("area_m2", "output.area_m2", "output.fields_preview.UF_CRM_VPP_AREA_M2"),
        ("first_touch_channel", "output.first_touch_channel", "output.fields_preview.UF_CRM_VPP_FIRST_CH"),
        ("last_touch_channel", "output.last_touch_channel", "output.fields_preview.UF_CRM_VPP_LAST_CH"),
    ]
    results = []
    for name, qualified_path, crm_path in field_pairs:
        qualified_value = _get_path(qualified, qualified_path)
        crm_value = _get_path(crm, crm_path)
        results.append(
            {
                "field": name,
                "qualified_value": qualified_value,
                "crm_value": crm_value,
                "status": "OK" if _is_present(qualified_value) and qualified_value == crm_value else "FAILED",
            }
        )
    return {
        "status": "OK" if all(item["status"] == "OK" for item in results) else "FAILED",
        "fields": results,
    }


def _write_markdown(report: dict[str, Any]) -> None:
    rows = []
    for item in report["artifact_checks"]:
        rows.append(
            "| {artifact} | {owner} | {status} | `{file}` | {next_step} |".format(
                artifact=item["artifact"],
                owner=item["owner"],
                status=item["status"],
                file=item["file"],
                next_step=item["next_step"],
            )
        )

    attribution_rows = []
    for item in report["attribution_check"]["fields"]:
        attribution_rows.append(
            "| {field} | {status} | `{qualified}` | `{crm}` |".format(
                field=item["field"],
                status=item["status"],
                qualified=item["qualified_value"],
                crm=item["crm_value"],
            )
        )

    markdown = "\n".join(
        [
            "# First Inbound Scenario Artifact Check",
            "",
            f"Дата: `{report['created_at']}`",
            "",
            f"Статус: `{report['scenario_status']}`",
            "",
            "Проверка локальная: внешние сервисы не запускались.",
            "",
            "## Артефакты",
            "",
            "| Артефакт | Владелец | Статус | Файл | Следующий шаг |",
            "|---|---|---|---|---|",
            *rows,
            "",
            "## Сквозные поля",
            "",
            "| Поле | Статус | QualifiedLead | CRM preview |",
            "|---|---|---|---|",
            *attribution_rows,
            "",
            "## Что осталось подтвердить перед реальной отправкой",
            "",
            *[f"- {item}" for item in report["fields_to_confirm_before_real_send"]],
            "",
            "## Запреты",
            "",
            *[f"- {item}" for item in report["forbidden_actions"]],
            "",
            f"Следующий маленький шаг: {report['next_small_step']}",
            "",
        ]
    )
    REPORT_MD_PATH.write_text(markdown, encoding="utf-8")


def run() -> dict[str, Any]:
    artifact_checks = [_check_artifact(spec) for spec in ARTIFACT_SPECS]
    qualified_data, _ = _read_json(QUALIFIED_PATH)
    crm_data, _ = _read_json(CRM_PREVIEW_PATH)
    attribution_check = _attribution_check(qualified_data, crm_data)

    crm_confirm_fields = _get_path(crm_data, "output.fields_to_confirm_before_real_send")
    if not isinstance(crm_confirm_fields, list):
        crm_confirm_fields = []

    all_artifacts_ok = all(item["status"] in {"OK", "OK_EMBEDDED"} for item in artifact_checks)
    scenario_status = (
        "OK_LOCAL_DRY_RUN_READY_FOR_MANUAL_REVIEW"
        if all_artifacts_ok and attribution_check["status"] == "OK"
        else "FAILED"
    )

    report = {
        "test_type": "first_inbound_scenario_artifact_check",
        "scenario": SCENARIO_NAME,
        "scenario_status": scenario_status,
        "created_at": _utc_now(),
        "dry_run": True,
        "artifact_count": len(artifact_checks),
        "artifact_checks": artifact_checks,
        "attribution_check": attribution_check,
        "fields_to_confirm_before_real_send": crm_confirm_fields,
        "next_small_step": "подтвердить Bitrix24 поля для crm.deal.add или оставить сценарий в dry-run до реального входящего запроса",
        "forbidden_actions": [
            "не отправлять crm.deal.add без отдельного подтверждения",
            "не запускать Redis, Telegram, IMAP, LLM, scheduler и publisher",
            "не использовать реальные клиентские данные в тестах",
            "не показывать значения webhook, токенов и секретов",
        ],
        "external_calls": {
            "redis": False,
            "bitrix24": False,
            "telegram_send": False,
            "imap": False,
            "llm": False,
            "scheduler": False,
            "publisher": False,
            "max": False,
            "vk": False,
        },
        "report_file": _relative(REPORT_JSON_PATH),
        "markdown_report": _relative(REPORT_MD_PATH),
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_markdown(report)
    return report


def main() -> int:
    report = run()
    print(f"test_type={report['test_type']}")
    print(f"scenario_status={report['scenario_status']}")
    print(f"artifact_count={report['artifact_count']}")
    print(f"attribution_status={report['attribution_check']['status']}")
    for item in report["artifact_checks"]:
        print(f"{item['artifact']}_status={item['status']}")
    print(
        "external_calls="
        + ",".join(f"{key}:{value}" for key, value in report["external_calls"].items())
    )
    print(f"report_file={report['report_file']}")
    print(f"markdown_report={report['markdown_report']}")
    return 0 if report["scenario_status"].startswith("OK") else 1


if __name__ == "__main__":
    raise SystemExit(main())
