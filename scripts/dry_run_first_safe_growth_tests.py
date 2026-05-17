"""Build local dry-run records for the first safe growth tests.

No external service is called. The output is an approval checklist for the next
manual decisions.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON_PATH = PROJECT_ROOT / "data" / "reports" / "first_safe_growth_tests.json"
REPORT_MD_PATH = PROJECT_ROOT / "data" / "reports" / "first_safe_growth_tests.md"


TESTS: list[dict[str, Any]] = [
    {
        "test_id": "safe_growth_001",
        "source_id": "lgm_012",
        "source_name": "Старые контакты и сделки Bitrix24",
        "segment": "crm_base",
        "owner_agent": "agent5_crm",
        "mode": "read_only",
        "proposed_action": "Сегментировать старые контакты и сделки, найти дубли и кандидатов на ручную реактивацию.",
        "content_or_material": "CRM hygiene and reactivation candidate report",
        "bitrix_tags": ["source:bitrix24", "segment:crm_base", "risk:low", "mode:read_only"],
        "utm": {"utm_source": "bitrix24", "utm_campaign": "old_base_readonly", "utm_medium": "crm"},
        "approval_required": True,
        "stop_rule": "Остановиться до любых изменений карточек, объединения дублей или сообщений клиентам.",
        "success_metric": "reactivation_candidates найден, но action_status остается DRY_RUN_NOT_SENT.",
    },
    {
        "test_id": "safe_growth_002",
        "source_id": "lgm_001",
        "source_name": "MAX-канал СИЛА Проекта",
        "segment": "all_segments",
        "owner_agent": "agent4_publisher",
        "mode": "draft_only",
        "proposed_action": "Подготовить 5 B2B-постов первой волны без публикации.",
        "content_or_material": "content/pipeline/drafts/max-b2b-first-wave-2026-05-16.md",
        "bitrix_tags": ["source:max", "segment:b2b", "risk:low", "mode:draft_only"],
        "utm": {"utm_source": "max", "utm_campaign": "b2b_first_wave", "utm_medium": "organic"},
        "approval_required": True,
        "stop_rule": "Остановиться до публикации, автопостинга или платного продвижения.",
        "success_metric": "5 черновиков готовы и имеют segment, CTA, approval_status=draft.",
    },
    {
        "test_id": "safe_growth_003",
        "source_id": "lgm_008",
        "source_name": "Коммерческие тендерные площадки",
        "segment": "b2b",
        "owner_agent": "agent1_scout",
        "mode": "read_only",
        "proposed_action": "Подготовить фильтры тендеров и чеклист решения участвовать или нет.",
        "content_or_material": "tender filters and bid decision checklist",
        "bitrix_tags": ["source:tender", "segment:b2b", "risk:low", "mode:read_only"],
        "utm": {"utm_source": "tender", "utm_campaign": "commercial_design_monitoring", "utm_medium": "manual"},
        "approval_required": True,
        "stop_rule": "Остановиться до регистрации, оплаты агрегатора, подачи заявки или загрузки документов.",
        "success_metric": "Фильтры и чеклист готовы; bid_status=NOT_SUBMITTED.",
    },
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _relative(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def _write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# First Safe Growth Tests",
        "",
        f"Generated at: `{report['generated_at']}`",
        "",
        "Статус: dry-run. Внешние сервисы, публикации, Bitrix24-запись и реклама не запускались.",
        "",
        "| Test | Источник | Режим | Действие | Stop rule |",
        "|---|---|---|---|---|",
    ]
    for test in report["tests"]:
        lines.append(
            "| {test_id} | {source_name} | {mode} | {proposed_action} | {stop_rule} |".format(**test)
        )
    lines.extend(["", "## Что отложено", ""])
    for item in report["deferred_items"]:
        lines.append(f"- {item}")
    lines.append("")
    REPORT_MD_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = {
        "status": "READY",
        "generated_at": _utc_now(),
        "source_doc": "docs/first-safe-growth-tests-from-lecture-2026-05-15.md",
        "readonly": True,
        "tests_count": len(TESTS),
        "tests": TESTS,
        "deferred_items": [
            "Реактивация старых контактов Bitrix24 только после отдельного approval.",
            "Публикация MAX-постов только после approval.",
            "Регистрация, оплата и подача тендеров только после отдельного решения.",
            "Telegram/VK/форумы только после списка конкретных площадок и проверки правил.",
            "Реклама только после бюджета, UTM, стоп-правил и готового лендинга/поста.",
        ],
        "external_calls": {
            "redis": False,
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
    REPORT_JSON_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_markdown(report)

    print("first_safe_growth_tests_status=READY")
    print(f"tests_count={report['tests_count']}")
    print(f"report_file={_relative(REPORT_JSON_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
