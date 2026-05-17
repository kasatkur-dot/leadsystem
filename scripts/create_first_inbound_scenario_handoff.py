"""Create a local task-handoff for the first inbound request scenario.

This does not send anything to Bitrix24 or messengers. It only reads local
dry-run reports and writes a local handoff artifact for dashboard/REPORT.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = PROJECT_ROOT / "data" / "reports"

CHECK_PATH = REPORTS_DIR / "first_inbound_scenario_artifact_check.json"
CRM_PREVIEW_PATH = REPORTS_DIR / "first_inbound_crm_payload_preview_dry_run.json"
REPORT_JSON_PATH = REPORTS_DIR / "first_inbound_scenario_handoff_to_human.json"
REPORT_MD_PATH = REPORTS_DIR / "first_inbound_scenario_handoff_to_human.md"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _relative(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _write_markdown(report: dict[str, Any]) -> None:
    required_decisions = report.get("required_decisions_from_yana", [])
    forbidden = report.get("forbidden_actions", [])
    markdown = "\n".join(
        [
            "# First Inbound Scenario Handoff To Human",
            "",
            f"Дата: `{report['created_at']}`",
            "",
            f"Статус: `{report['handoff_status']}`",
            "",
            "## Task-handoff",
            "",
            f"- От кого: {report['from']}",
            f"- Кому: {report['to']}",
            f"- Цель: {report['goal']}",
            f"- Контекст: {report['context']}",
            f"- Что уже известно: {report['known_facts']}",
            f"- Что нужно сделать: {report['what_to_do']}",
            f"- Формат результата: {report['result_format']}",
            f"- Куда положить результат: {report['result_storage']}",
            f"- Условие готовности: {report['done_when']}",
            f"- Нужна Яника: {report['needs_yana']}",
            "",
            "## Решения перед реальной отправкой",
            "",
            *[f"- {item}" for item in required_decisions],
            "",
            "## Запреты",
            "",
            *[f"- {item}" for item in forbidden],
            "",
            f"Следующий маленький шаг: {report['next_small_step']}",
            "",
        ]
    )
    REPORT_MD_PATH.write_text(markdown, encoding="utf-8")


def run() -> dict[str, Any]:
    check = _read_json(CHECK_PATH)
    crm_preview = _read_json(CRM_PREVIEW_PATH)
    output = crm_preview.get("output", {})
    if not isinstance(output, dict):
        output = {}
    human_handoff = output.get("human_handoff", {})
    if not isinstance(human_handoff, dict):
        human_handoff = {}
    fields_to_confirm = output.get("fields_to_confirm_before_real_send", [])
    if not isinstance(fields_to_confirm, list):
        fields_to_confirm = []

    scenario_status = check.get("scenario_status", "MISSING_CHECK")
    handoff_status = (
        "READY_FOR_MANUAL_REVIEW"
        if scenario_status == "OK_LOCAL_DRY_RUN_READY_FOR_MANUAL_REVIEW"
        else "BLOCKED_BY_SCENARIO_CHECK"
    )

    report: dict[str, Any] = {
        "test_type": "task-handoff",
        "handoff_type": "first_inbound_scenario_to_human",
        "scenario": "Первый входящий запрос",
        "handoff_status": handoff_status,
        "created_at": _utc_now(),
        "dry_run": True,
        "from": "Agent 5 CRM / CRM Router",
        "to": "Человек-контролёр / Яника",
        "goal": "передать готовый dry-run сценарий первого входящего запроса на ручное решение перед реальной отправкой",
        "context": "Есть локальный intake_card, qualified_lead, crm_payload_preview и human_next_step. Bitrix24 не вызывался.",
        "known_facts": human_handoff.get(
            "summary",
            "Тестовый входящий запрос готов к ручной проверке.",
        ),
        "what_to_do": human_handoff.get(
            "recommended_first_action",
            "Проверить сценарий и решить, подтверждать ли поля Bitrix24.",
        ),
        "result_format": "решение: confirm_bitrix_fields / keep_dry_run / revise_payload",
        "result_storage": "REPORT.md + data/reports/first_inbound_scenario_handoff_to_human.json",
        "done_when": "человек подтвердил поля Bitrix24 или явно оставил сценарий в dry-run",
        "needs_yana": "да",
        "required_decisions_from_yana": fields_to_confirm,
        "input_reports": {
            "scenario_check": _relative(CHECK_PATH),
            "crm_payload_preview": _relative(CRM_PREVIEW_PATH),
        },
        "forbidden_actions": [
            "не отправлять crm.deal.add без отдельного подтверждения",
            "не запускать Redis, Bitrix24, Telegram, IMAP, LLM, scheduler и publisher",
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
        "next_small_step": "Янике выбрать: confirm_bitrix_fields, keep_dry_run или revise_payload",
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
    print(f"handoff_status={report['handoff_status']}")
    print(f"scenario={report['scenario']}")
    print(f"needs_yana={report['needs_yana']}")
    print(
        "external_calls="
        + ",".join(f"{key}:{value}" for key, value in report["external_calls"].items())
    )
    print(f"report_file={report['report_file']}")
    print(f"markdown_report={report['markdown_report']}")
    return 0 if report["handoff_status"] == "READY_FOR_MANUAL_REVIEW" else 1


if __name__ == "__main__":
    raise SystemExit(main())
