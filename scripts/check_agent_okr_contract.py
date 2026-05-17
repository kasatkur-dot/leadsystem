"""Check that the six agent departments have their OKR contract recorded.

This is a local read-only checker. It reads project files and writes one JSON
report. It does not import runtime agent modules and does not call Redis,
Bitrix24, Telegram, IMAP, LLM APIs, scheduler, or publication services.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = PROJECT_ROOT / "data" / "reports" / "agent_okr_contract_check.json"
VISUAL_MAP_PATH = PROJECT_ROOT / "docs" / "multi-agent-visual-control-map.md"
ADMIN_DASHBOARD_SPEC_PATH = PROJECT_ROOT / "docs" / "admin-dashboard-spec.md"
DASHBOARD_BUILDER_PATH = PROJECT_ROOT / "scripts" / "build_agent_dashboard.py"
DASHBOARD_REPORT_PATH = PROJECT_ROOT / "data" / "reports" / "agent_dashboard.json"
DASHBOARD_VIEWER_BUILDER_PATH = PROJECT_ROOT / "scripts" / "build_agent_dashboard_viewer.py"
DASHBOARD_VIEWER_PATH = PROJECT_ROOT / "data" / "reports" / "agent_dashboard.html"
DASHBOARD_MARKDOWN_BUILDER_PATH = PROJECT_ROOT / "scripts" / "build_agent_dashboard_markdown.py"
DASHBOARD_MARKDOWN_PATH = PROJECT_ROOT / "data" / "reports" / "agent_dashboard.md"
SECURITY_AGENT_PATH = PROJECT_ROOT / "agents" / "Агент безопастности" / "AGENT_SECURITY.md"
SECURITY_RULE_PATH = PROJECT_ROOT / ".claude" / "rules" / "security.md"
CLAUDE_PROJECT_RULES_PATH = PROJECT_ROOT / "docs" / "claude-project-rules.md"
SECURITY_CONTROL_DOC_PATH = PROJECT_ROOT / "docs" / "security-agent-control-layer.md"

AGENTS = {
    "agent1_scout": PROJECT_ROOT / "agents" / "agent1_scout",
    "agent2_collector": PROJECT_ROOT / "agents" / "agent2_collector",
    "agent3_processor": PROJECT_ROOT / "agents" / "agent3_processor",
    "agent4_publisher": PROJECT_ROOT / "agents" / "agent4_publisher",
    "agent5_crm": PROJECT_ROOT / "agents" / "agent5_crm",
    "agent6_outreach": PROJECT_ROOT / "agents" / "agent6_outreach",
}

REQUIRED_REDIS_QUEUE_LITERALS = [
    "leads:raw",
    "leads:qualified",
    "leads:outreach",
    "content:published",
]

REQUIRED_VISUAL_MAP_LITERALS = [
    "Agent 1 Scout",
    "Agent 2 Collector",
    "Agent 3 Processor",
    "Agent 4 Publisher",
    "Agent 5 CRM",
    "Agent 6 Outreach",
    "`agents/agent1_scout/__init__.py`",
    "`agents/agent2_collector/__init__.py`",
    "`agents/agent3_processor/__init__.py`",
    "`agents/agent4_publisher/__init__.py`",
    "`agents/agent5_crm/__init__.py`",
    "`agents/agent6_outreach/__init__.py`",
    "Mermaid-схема всей системы",
    "Markdown-таблица агентов",
    "Будущая админ-панель",
    "Верхняя панель",
    "Карта агентов",
    "Перемещаемая карта агентов",
    "Детали агента",
    "Event stream",
    "Dashboard метрик",
    "Checker-agent",
    "Внешняя MAS-модель как референс",
    "Scenario Timeline",
    "Artifact Tracker",
    "OSINT-модуль",
    "Суброли по модели лектора без создания Agent 7",
    "docs/agent-subroles-and-kpi-map.md",
    "docs/agent-scenario-artifact-contract.md",
    "Security Agent Control Layer",
    "AGENT_SECURITY.md",
]

REQUIRED_ADMIN_DASHBOARD_LITERALS = [
    "Верхняя панель",
    "Карта агентов",
    "Детали агента",
    "Event stream",
    "Dashboard метрик",
    "Checker-блок",
    "Перемещаемая карта агентов",
    "Agent 1 Scout",
    "Agent 2 Collector",
    "Agent 3 Processor",
    "Agent 4 Publisher",
    "Agent 5 CRM",
    "Agent 6 Outreach",
    "admin_dashboard_spec_status",
    "missing_admin_dashboard_items",
    "scripts/check_agent_okr_contract.py",
    "MAS-референс",
    "Scenario Timeline",
    "Artifact Tracker",
    "Status model",
    "AI Operator Chat",
    "Scenario Artifact Contract",
    "Суброли внутри 6 агентов",
    "docs/agent-subroles-and-kpi-map.md",
    "docs/agent-scenario-artifact-contract.md",
    "Security Agent Control Layer",
    "AGENT_SECURITY.md",
]

REQUIRED_DASHBOARD_REPORT_KEYS = [
    "dashboard_build_status",
    "top_panel",
    "visual_display",
    "source_map",
    "interaction_graph",
    "management_protocol",
    "mas_reference_layer",
    "security_agent_control_layer",
    "scenario_artifact_contract",
    "agent_map",
    "agent_details",
    "event_stream",
    "metrics_dashboard",
    "checker",
    "external_calls",
]

REQUIRED_DASHBOARD_VIEWER_LITERALS = [
    "Общий статус",
    "Схема по лекции 5",
    "Перемещаемая карта агентов",
    "Главный агент-оркестратор",
    "workflowCanvas",
    "workflow-node",
    "leadEngineAgentWorkflowPositionsV1",
    "Сбросить расположение",
    "Что доделать",
    "готово",
    "как на доске Obsidian",
    "Карта взаимодействий агентов",
    "Chief of Staff / Handoff / Escalation / Weekly digest",
    "Управленческий слой без Agent 7",
    "task-handoff",
    "agent-result",
    "escalation-to-yana",
    "weekly digest",
    "Основной поток лида",
    "Контентный поток",
    "Outreach поток",
    "Контрольный поток",
    "source card -&gt; RawLead -&gt; QualifiedLead -&gt; CRM record",
    "Департаменты",
    "Поток результата",
    "Связи и handoff",
    "Что передается",
    "Кто проверяет",
    "6 агентов",
    "Детали агента",
    "Главная метрика",
    "OKR/KR метрики",
    "Защитные метрики",
    "KR готово",
    "Последние события",
    "Метрики",
    "Запреты",
    "только просмотр",
    "data/reports/agent_dashboard.json",
    "Redis, Bitrix24, Telegram, IMAP, LLM, scheduler и publisher",
    "Карта источников",
    "17 MVP-каналов",
    "Watchlist конкурентов Agent 1",
    "Каналы Яники: 5 строк ждут ссылок",
    "Backlog-источники",
    "Источники по агенту",
    "MAS reference layer",
    "Scenario Timeline",
    "Artifact Tracker",
    "OSINT без Agent 7",
    "AI Operator Chat",
    "Scenario Artifact Contract",
    "Суброли",
    "subrole-card",
    "docs/agent-subroles-and-kpi-map.md",
    "docs/agent-scenario-artifact-contract.md",
    "Security Agent Control Layer",
    "AGENT_SECURITY.md",
    "не Agent 7",
]

REQUIRED_DASHBOARD_MARKDOWN_LITERALS = [
    "Agent Dashboard Snapshot",
    "Верхняя панель",
    "Карта агентов",
    "Карта взаимодействий агентов",
    "Chief of Staff / Handoff / Escalation / Weekly digest",
    "Нервная система",
    "task-handoff",
    "agent-result",
    "escalation-to-yana",
    "Weekly digest",
    "Основной поток лида",
    "Контентный поток",
    "Outreach поток",
    "Контрольный поток",
    "Детали агентов",
    "Готовность",
    "KR-готовность",
    "Главная метрика",
    "OKR/KR метрики",
    "Защитные метрики",
    "Что доделать",
    "Скиллы",
    "Event stream",
    "Dashboard метрик",
    "Checker",
    "Redis, Bitrix24, Telegram, IMAP, LLM, scheduler, publisher",
    "Карта источников",
    "Все 17 MVP-каналов",
    "Источники по агенту",
    "Backlog-источники",
    "MAS Reference Layer",
    "Scenario Timeline",
    "Artifact Tracker",
    "OSINT protocol",
    "AI Operator Chat",
    "Scenario Artifact Contract",
    "Суброли",
    "docs/agent-subroles-and-kpi-map.md",
    "docs/agent-scenario-artifact-contract.md",
    "Security Agent Control Layer",
    "AGENT_SECURITY.md",
    "не Agent 7",
]

REQUIRED_SECURITY_AGENT_LITERALS = [
    "Стоп-линии",
    "Зелёный коридор",
    "Что НИКОГДА не уходит",
    "кошелёк",
    "MCP",
    "LLM",
    "lethal trifecta",
    "SSRF",
    "slopsquatting",
]

REQUIRED_SECURITY_REFERENCE_FILES = {
    "CLAUDE.md": PROJECT_ROOT / "CLAUDE.md",
    "AGENTS.md": PROJECT_ROOT / "AGENTS.md",
    ".claude/rules/security.md": SECURITY_RULE_PATH,
    "docs/claude-project-rules.md": CLAUDE_PROJECT_RULES_PATH,
    "docs/security-agent-control-layer.md": SECURITY_CONTROL_DOC_PATH,
}

REQUIRED_SECURITY_REFERENCE_LITERALS = [
    "AGENT_SECURITY.md",
    "Агент безопастности",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except json.JSONDecodeError:
        return {}


def _relative(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def run() -> dict[str, Any]:
    missing_agent_files: list[str] = []
    missing_okr_blocks: list[str] = []
    missing_metric_blocks: list[str] = []
    checked_agents: dict[str, dict[str, str]] = {}

    for agent_name, agent_dir in AGENTS.items():
        init_path = agent_dir / "__init__.py"
        folder_status = "FOUND" if agent_dir.is_dir() else "MISSING"
        file_status = "FOUND" if init_path.is_file() else "MISSING"
        text = _read_text(init_path)
        okr_status = "FOUND" if "Ожидаемый конечный результат" in text else "MISSING"
        metric_status = "FOUND" if "Метрики" in text else "MISSING"

        if folder_status == "MISSING":
            missing_agent_files.append(_relative(agent_dir))
        if file_status == "MISSING":
            missing_agent_files.append(_relative(init_path))
        if okr_status == "MISSING":
            missing_okr_blocks.append(_relative(init_path))
        if metric_status == "MISSING":
            missing_metric_blocks.append(_relative(init_path))

        checked_agents[agent_name] = {
            "folder_status": folder_status,
            "init_file_status": file_status,
            "okr_block_status": okr_status,
            "metric_block_status": metric_status,
        }

    agent4_readme = PROJECT_ROOT / "agents" / "agent4_publisher" / "README.md"
    agent4_readme_status = "FOUND" if agent4_readme.is_file() else "MISSING"

    claude_text = _read_text(PROJECT_ROOT / "CLAUDE.md")
    missing_claude_folder_mentions = [
        agent_name for agent_name in AGENTS if f"{agent_name}/" not in claude_text
    ]
    claude_folder_map_status = "OK" if not missing_claude_folder_mentions else "FAILED"

    redis_text = _read_text(PROJECT_ROOT / "shared" / "redis_client.py")
    missing_redis_queues = [
        queue_literal for queue_literal in REQUIRED_REDIS_QUEUE_LITERALS if queue_literal not in redis_text
    ]
    redis_queue_status = "OK" if not missing_redis_queues else "FAILED"

    canonical_test = PROJECT_ROOT / "scripts" / "test_agent3_to_agent5_handoff_local.py"
    canonical_test_status = "FOUND" if canonical_test.is_file() else "MISSING"

    visual_map_text = _read_text(VISUAL_MAP_PATH)
    missing_visual_map_items = [
        item for item in REQUIRED_VISUAL_MAP_LITERALS if item not in visual_map_text
    ]
    visual_map_status = "OK" if VISUAL_MAP_PATH.is_file() and not missing_visual_map_items else "FAILED"

    admin_dashboard_text = _read_text(ADMIN_DASHBOARD_SPEC_PATH)
    missing_admin_dashboard_items = [
        item for item in REQUIRED_ADMIN_DASHBOARD_LITERALS if item not in admin_dashboard_text
    ]
    admin_dashboard_spec_status = (
        "OK"
        if ADMIN_DASHBOARD_SPEC_PATH.is_file() and not missing_admin_dashboard_items
        else "FAILED"
    )

    dashboard_builder_status = "FOUND" if DASHBOARD_BUILDER_PATH.is_file() else "MISSING"
    dashboard_report = _read_json(DASHBOARD_REPORT_PATH)
    missing_dashboard_report_items = [
        item for item in REQUIRED_DASHBOARD_REPORT_KEYS if item not in dashboard_report
    ]
    dashboard_report_status = (
        "OK"
        if DASHBOARD_REPORT_PATH.is_file()
        and dashboard_report.get("dashboard_build_status") == "OK"
        and not missing_dashboard_report_items
        else "FAILED"
    )

    dashboard_viewer_builder_status = "FOUND" if DASHBOARD_VIEWER_BUILDER_PATH.is_file() else "MISSING"
    dashboard_viewer_text = _read_text(DASHBOARD_VIEWER_PATH)
    missing_dashboard_viewer_items = [
        item for item in REQUIRED_DASHBOARD_VIEWER_LITERALS if item not in dashboard_viewer_text
    ]
    dashboard_viewer_status = (
        "OK"
        if DASHBOARD_VIEWER_PATH.is_file() and not missing_dashboard_viewer_items
        else "FAILED"
    )

    dashboard_markdown_builder_status = "FOUND" if DASHBOARD_MARKDOWN_BUILDER_PATH.is_file() else "MISSING"
    dashboard_markdown_text = _read_text(DASHBOARD_MARKDOWN_PATH)
    missing_dashboard_markdown_items = [
        item for item in REQUIRED_DASHBOARD_MARKDOWN_LITERALS if item not in dashboard_markdown_text
    ]
    dashboard_markdown_status = (
        "OK"
        if DASHBOARD_MARKDOWN_PATH.is_file() and not missing_dashboard_markdown_items
        else "FAILED"
    )

    security_agent_text = _read_text(SECURITY_AGENT_PATH)
    missing_security_agent_items = [
        item for item in REQUIRED_SECURITY_AGENT_LITERALS if item not in security_agent_text
    ]
    security_agent_status = (
        "OK"
        if SECURITY_AGENT_PATH.is_file() and not missing_security_agent_items
        else "FAILED"
    )

    missing_security_reference_items: dict[str, list[str]] = {}
    for label, path in REQUIRED_SECURITY_REFERENCE_FILES.items():
        text = _read_text(path)
        missing_items = [item for item in REQUIRED_SECURITY_REFERENCE_LITERALS if item not in text]
        if missing_items or not path.is_file():
            missing_security_reference_items[label] = missing_items or ["FILE_MISSING"]
    security_reference_status = "OK" if not missing_security_reference_items else "FAILED"

    blocking_failures = (
        missing_agent_files
        or missing_okr_blocks
        or missing_metric_blocks
        or agent4_readme_status == "MISSING"
        or claude_folder_map_status != "OK"
        or redis_queue_status != "OK"
        or canonical_test_status != "FOUND"
        or visual_map_status != "OK"
        or admin_dashboard_spec_status != "OK"
        or dashboard_builder_status != "FOUND"
        or dashboard_report_status != "OK"
        or dashboard_viewer_builder_status != "FOUND"
        or dashboard_viewer_status != "OK"
        or dashboard_markdown_builder_status != "FOUND"
        or dashboard_markdown_status != "OK"
        or security_agent_status != "OK"
        or security_reference_status != "OK"
    )
    agent_contract_status = "FAILED" if blocking_failures else "OK"

    result: dict[str, Any] = {
        "test_type": "agent_okr_contract_check",
        "agent_contract_status": agent_contract_status,
        "checked_agents": checked_agents,
        "missing_agent_files": missing_agent_files,
        "missing_okr_blocks": missing_okr_blocks,
        "missing_metric_blocks": missing_metric_blocks,
        "agent4_readme_status": agent4_readme_status,
        "claude_folder_map_status": claude_folder_map_status,
        "missing_claude_folder_mentions": missing_claude_folder_mentions,
        "redis_queue_status": redis_queue_status,
        "missing_redis_queues": missing_redis_queues,
        "canonical_test_status": canonical_test_status,
        "canonical_test_file": _relative(canonical_test),
        "visual_map_status": visual_map_status,
        "visual_map_file": _relative(VISUAL_MAP_PATH),
        "missing_visual_map_items": missing_visual_map_items,
        "admin_dashboard_spec_status": admin_dashboard_spec_status,
        "admin_dashboard_spec_file": _relative(ADMIN_DASHBOARD_SPEC_PATH),
        "missing_admin_dashboard_items": missing_admin_dashboard_items,
        "dashboard_builder_status": dashboard_builder_status,
        "dashboard_builder_file": _relative(DASHBOARD_BUILDER_PATH),
        "dashboard_report_status": dashboard_report_status,
        "dashboard_report_file": _relative(DASHBOARD_REPORT_PATH),
        "missing_dashboard_report_items": missing_dashboard_report_items,
        "dashboard_viewer_builder_status": dashboard_viewer_builder_status,
        "dashboard_viewer_builder_file": _relative(DASHBOARD_VIEWER_BUILDER_PATH),
        "dashboard_viewer_status": dashboard_viewer_status,
        "dashboard_viewer_file": _relative(DASHBOARD_VIEWER_PATH),
        "missing_dashboard_viewer_items": missing_dashboard_viewer_items,
        "dashboard_markdown_builder_status": dashboard_markdown_builder_status,
        "dashboard_markdown_builder_file": _relative(DASHBOARD_MARKDOWN_BUILDER_PATH),
        "dashboard_markdown_status": dashboard_markdown_status,
        "dashboard_markdown_file": _relative(DASHBOARD_MARKDOWN_PATH),
        "missing_dashboard_markdown_items": missing_dashboard_markdown_items,
        "security_agent_status": security_agent_status,
        "security_agent_file": _relative(SECURITY_AGENT_PATH),
        "missing_security_agent_items": missing_security_agent_items,
        "security_reference_status": security_reference_status,
        "security_control_doc_file": _relative(SECURITY_CONTROL_DOC_PATH),
        "missing_security_reference_items": missing_security_reference_items,
        "external_calls": {
            "redis": False,
            "bitrix24": False,
            "telegram_send": False,
            "imap": False,
            "llm": False,
            "scheduler": False,
            "publisher": False,
        },
        "report_write_status": "OK",
        "created_at": _utc_now(),
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    result = run()
    for key in [
        "test_type",
        "agent_contract_status",
        "agent4_readme_status",
        "claude_folder_map_status",
        "redis_queue_status",
        "canonical_test_status",
        "visual_map_status",
        "admin_dashboard_spec_status",
        "dashboard_builder_status",
        "dashboard_report_status",
        "dashboard_viewer_builder_status",
        "dashboard_viewer_status",
        "dashboard_markdown_builder_status",
        "dashboard_markdown_status",
        "security_agent_status",
        "security_reference_status",
        "report_write_status",
    ]:
        print(f"{key}={result[key]}")
    for key in [
        "missing_agent_files",
        "missing_okr_blocks",
        "missing_metric_blocks",
        "missing_claude_folder_mentions",
        "missing_redis_queues",
        "missing_visual_map_items",
        "missing_admin_dashboard_items",
        "missing_dashboard_report_items",
        "missing_dashboard_viewer_items",
        "missing_dashboard_markdown_items",
        "missing_security_agent_items",
        "missing_security_reference_items",
    ]:
        print(f"{key}={json.dumps(result[key], ensure_ascii=False)}")
    print(
        "external_calls="
        + ",".join(f"{key}:{value}" for key, value in result["external_calls"].items())
    )
    print(f"report_file={REPORT_PATH.relative_to(PROJECT_ROOT)}")
    return 0 if result["agent_contract_status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
