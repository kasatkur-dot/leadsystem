"""Build frontend graph data from the real agent dashboard report.

The visual frontend expects a compact graph model. This adapter keeps the
frontend separated from project internals while still using the real
`data/reports/agent_dashboard.json` as the source of truth.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from .agent_control import build_model_manifest
except ImportError:  # Allows running as: python backend/agent_dashboard_api/dashboard_data_builder.py
    from agent_control import build_model_manifest  # type: ignore


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DASHBOARD_PATH = PROJECT_ROOT / "data" / "reports" / "agent_dashboard.json"

ACCENT = {
    "cyan": "#4DE3FF",
    "green": "#66F2A6",
    "amber": "#F6C85F",
    "red": "#FF5C7A",
    "violet": "#A6B0FF",
    "grey": "#8E9AAA",
}

AGENT_VISUAL_IDS = {
    "agent1_scout": "a1-scout",
    "agent2_collector": "a2-collector",
    "agent3_processor": "a3-processor",
    "agent4_publisher": "a4-publisher",
    "agent5_crm": "a5-crm",
    "agent6_outreach": "a6-outreach",
}

AGENT_LAYOUT = {
    "agent1_scout": {"x": 560, "y": 540, "w": 320, "h": 188, "accent": ACCENT["cyan"]},
    "agent2_collector": {"x": 560, "y": 840, "w": 320, "h": 188, "accent": ACCENT["cyan"]},
    "agent3_processor": {"x": 1180, "y": 700, "w": 340, "h": 200, "accent": ACCENT["green"]},
    "agent4_publisher": {"x": 1180, "y": 1040, "w": 340, "h": 200, "accent": ACCENT["amber"]},
    "agent5_crm": {"x": 1820, "y": 700, "w": 340, "h": 200, "accent": ACCENT["green"]},
    "agent6_outreach": {"x": 560, "y": 1140, "w": 320, "h": 188, "accent": ACCENT["amber"]},
}

ARTIFACT_IDS = {
    "source card": "art-source",
    "source_card": "art-source",
    "signalcard": "art-signal",
    "signal card": "art-signal",
    "rawlead": "art-raw",
    "raw_lead": "art-raw",
    "normalized_raw_lead": "art-raw",
    "intake_card": "art-intake",
    "qualifiedlead": "art-qualified",
    "qualified_lead": "art-qualified",
    "score": "art-score",
    "score_result": "art-score",
    "score & reason": "art-score",
    "recommended action": "art-action",
    "recommended_action": "art-action",
    "approval_card": "art-approval",
    "content_brief": "art-content-brief",
    "content_draft": "art-draft",
    "content_metric_event": "art-content-event",
    "manual publication": "art-publication",
    "publication": "art-publication",
    "bitrix24 lead": "art-bitrix",
    "bitrix24 deal": "art-bitrix-deal",
    "crm_payload_preview": "art-crm-preview",
    "telegram alert": "art-tg",
    "romi report": "art-romi",
    "channel costs": "art-costs",
    "channel facts": "art-facts",
    "agent dashboard": "art-dashboard",
    "report.md memory": "art-report",
    "checker report": "art-checker",
    "outreachlead": "art-outreach",
    "outreach_lead": "art-outreach",
    "human_next_step": "art-human",
}


def load_dashboard(path: Path = DASHBOARD_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_agent_system_data(dashboard: dict[str, Any]) -> dict[str, Any]:
    source_map = dashboard.get("source_map", {})
    top_panel = dashboard.get("top_panel", {})
    metrics_dashboard = dashboard.get("metrics_dashboard", {})

    agents = [_build_agent_node(agent) for agent in dashboard.get("agent_details", [])]
    agent_node_ids = {node["dashboardAgentId"]: node["id"] for node in agents}

    artifacts = _build_artifacts(dashboard)
    services = _build_services(dashboard)
    sources = _build_sources(source_map)
    safety = _build_safety(top_panel.get("locks", {}), dashboard.get("scenario_artifact_contract", {}))
    edges = _build_edges(dashboard, agent_node_ids)
    scenarios = _build_scenarios(dashboard)

    return {
        "meta": {
            "projectName": top_panel.get("project_name", "design-studio-lead-engine"),
            "companyName": "Вектор Плюс-Про",
            "overallStatus": top_panel.get("overall_status", "OK"),
            "currentStage": top_panel.get("current_stage", ""),
            "generatedAt": dashboard.get("generated_at", ""),
            "nextSmallStep": dashboard.get("next_small_step") or top_panel.get("next_small_step", ""),
            "sourceReport": "data/reports/agent_dashboard.json",
            "dataMode": "live-local-dashboard-json",
        },
        "summary": {
            "channelsTotal": source_map.get("summary", {}).get("canonical_mvp_channels", 0),
            "wave1Channels": source_map.get("summary", {}).get("wave_1_channels", 0),
            "artifactsCount": len(artifacts),
            "servicesCount": len(services),
            "agentsCount": len(agents),
            "subrolesCount": sum(len(agent.get("subroles", [])) for agent in dashboard.get("agent_details", [])),
            "visualNodesCount": 1 + len(agents) + len(services) + len(sources) + len(artifacts),
        },
        "accent": ACCENT,
        "orchestrator": _build_orchestrator(top_panel),
        "agents": agents,
        "services": services,
        "sources": sources,
        "artifacts": artifacts,
        "safety": safety,
        "agentControl": build_model_manifest(),
        "edges": edges,
        "scenarios": scenarios,
        "metricsDashboard": metrics_dashboard,
    }


def build_runtime_js(dashboard: dict[str, Any]) -> str:
    data = build_agent_system_data(dashboard)
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    return (
        "/* Generated by backend/agent_dashboard_api from data/reports/agent_dashboard.json. */\n"
        f"window.AGENT_DATA = {payload};\n"
    )


def _build_orchestrator(top_panel: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": "orchestrator",
        "label": "AI Orchestrator",
        "type": "orchestrator",
        "sublabel": "CLAUDE.md · AGENTS.md · REPORT.md",
        "x": 1180,
        "y": 230,
        "w": 360,
        "h": 150,
        "accent": ACCENT["cyan"],
        "status": "active",
        "statusLabel": top_panel.get("overall_status", "Routing task"),
        "description": (
            "Главный управляющий слой проекта. Он принимает задачу от человека, "
            "маршрутизирует её в нужный агентский отдел, проверяет ограничения и "
            "фиксирует результат в REPORT.md."
        ),
        "responsibilities": [
            "Принять задачу от человека",
            "Определить нужный агентский отдел",
            "Проверить safety locks и правила проекта",
            "Получить agent-result или task-handoff",
            "Обновить память проекта и следующий шаг",
        ],
        "inputs": ["Human task", "REPORT.md", "AGENTS.md", "CLAUDE.md", "Agent reports"],
        "outputs": ["task-handoff", "agent-result", "checker verdict", "REPORT.md update"],
        "tools": ["CLAUDE.md", "AGENTS.md", "REPORT.md", "scripts/check_agent_okr_contract.py"],
        "statusStates": [
            "Reading REPORT.md",
            "Routing task",
            "Checking quality",
            "Awaiting approval",
            "Updating memory",
        ],
    }


def _build_agent_node(agent: dict[str, Any]) -> dict[str, Any]:
    agent_id = agent.get("agent_id", "")
    layout = AGENT_LAYOUT.get(agent_id, {"x": 900, "y": 900, "w": 320, "h": 188, "accent": ACCENT["grey"]})
    visual_id = AGENT_VISUAL_IDS.get(agent_id, agent_id.replace("_", "-"))
    subroles = agent.get("subroles") or []
    skills = agent.get("skills") or []
    mcp_api = agent.get("mcp_api") or []
    main_metric = agent.get("main_metric") or {}

    node = {
        "id": visual_id,
        "dashboardAgentId": agent_id,
        "label": _format_agent_title(agent.get("title", agent_id)),
        "short": _short_agent(agent_id),
        "type": "agent",
        "department": agent.get("department") or agent.get("role") or agent_id,
        "x": layout["x"],
        "y": layout["y"],
        "w": layout["w"],
        "h": layout["h"],
        "accent": layout["accent"],
        "status": _status_from_panel(agent.get("panel_status", "")),
        "statusLabel": agent.get("panel_status", ""),
        "description": agent.get("description") or agent.get("role") or "",
        "readiness": int(agent.get("readiness_percent") or 0),
        "krReadiness": int(agent.get("okr_readiness_percent") or 0),
        "stats": [
            {
                "k": _clip(main_metric.get("name", "main metric"), 19),
                "v": _metric_value(main_metric),
            },
            {"k": "subroles", "v": str(len(subroles))},
            {"k": "skills", "v": str(len(skills))},
            {"k": "status", "v": _clip(agent.get("panel_status", "—"), 18)},
        ],
        "responsibilities": _subrole_responsibilities(subroles) or _as_list(agent.get("outputs")),
        "inputs": _as_list(agent.get("inputs")),
        "outputs": _as_list(agent.get("outputs")),
        "sources": _source_scope_to_list(agent.get("source_scope")),
        "tools": [*mcp_api, agent.get("file", "")],
        "okr": agent.get("okr") or "",
        "krMetrics": [_okr_metric(metric) for metric in agent.get("okr_metrics", [])],
        "guardMetrics": _as_list(agent.get("guard_metrics")),
        "skills": skills,
        "modules": [role.get("name", "") for role in subroles if role.get("name")],
        "subroles": subroles,
        "nextAction": agent.get("next_action") or "",
        "exampleTask": f"Следующий безопасный шаг: {agent.get('next_action')}" if agent.get("next_action") else "",
        "agentFile": agent.get("file", ""),
    }
    return node


def _build_services(dashboard: dict[str, Any]) -> list[dict[str, Any]]:
    checker = dashboard.get("checker", {})
    locks = dashboard.get("top_panel", {}).get("locks", {})
    source_map = dashboard.get("source_map", {})
    return [
        {
            "id": "svc-scheduler",
            "label": "Technical Scheduler",
            "type": "module",
            "x": 160,
            "y": 1300,
            "w": 210,
            "h": 86,
            "accent": ACCENT["grey"],
            "status": "blocked" if locks.get("scheduler_locked", True) else "idle",
            "statusLabel": "Locked" if locks.get("scheduler_locked", True) else "Idle",
            "description": "Технический запускатель. В MVP не запускается до проверки блокеров.",
            "responsibilities": ["Расписание периодических задач", "Технический запуск, не бизнес-оркестратор"],
            "inputs": ["Cron config"],
            "outputs": ["scheduled jobs"],
            "tools": ["orchestrator/scheduler.py"],
        },
        {
            "id": "svc-redis",
            "label": "Redis Queues",
            "type": "module",
            "x": 390,
            "y": 1300,
            "w": 210,
            "h": 86,
            "accent": ACCENT["cyan"],
            "status": "idle",
            "statusLabel": "Not called now",
            "description": "Очереди для передачи RawLead, QualifiedLead, content drafts и approval cards.",
            "responsibilities": ["Передача артефактов между агентами", "Очереди MVP"],
            "inputs": ["RawLead", "QualifiedLead", "Content Draft"],
            "outputs": ["Queue events"],
            "tools": ["Redis", "shared/queue"],
        },
        {
            "id": "svc-sources",
            "label": "Source Registry",
            "type": "module",
            "x": 620,
            "y": 1300,
            "w": 210,
            "h": 86,
            "accent": ACCENT["cyan"],
            "status": "active" if source_map.get("source_map_status") == "OK" else "waiting",
            "description": "Реестр 17 каналов, волн, владельцев и UTM-логики.",
            "responsibilities": ["Хранение каналов", "Связь канала с owner_agent", "Волны запуска"],
            "inputs": ["channel-registry-mvp.csv"],
            "outputs": ["source_map"],
            "tools": ["content/library/sources/channel-registry-mvp.csv"],
        },
        {
            "id": "svc-checker",
            "label": "Checker / QA",
            "type": "module",
            "x": 850,
            "y": 1300,
            "w": 210,
            "h": 86,
            "accent": ACCENT["amber"],
            "status": "active" if checker.get("agent_contract_status") == "OK" else "waiting",
            "description": "Проверяет, что реальные файлы соответствуют схеме агентов, OKR и dashboard.",
            "responsibilities": ["Сверка файлов", "Проверка OKR", "Отчёт по пропускам"],
            "inputs": ["agent contracts"],
            "outputs": ["checker report"],
            "tools": [checker.get("script", "scripts/check_agent_okr_contract.py")],
        },
        {
            "id": "svc-report",
            "label": "REPORT.md Memory",
            "type": "module",
            "x": 1080,
            "y": 1300,
            "w": 210,
            "h": 86,
            "accent": ACCENT["violet"],
            "status": "active",
            "description": "Память проекта: что сделано, что проверено, что дальше.",
            "responsibilities": ["История работ", "Следующий шаг", "Safety decisions"],
            "inputs": ["agent-result", "task-handoff"],
            "outputs": ["REPORT.md update"],
            "tools": ["REPORT.md", "tasks/session-notes.md"],
        },
        {
            "id": "svc-dashboard",
            "label": "Dashboard Reports",
            "type": "module",
            "x": 1310,
            "y": 1300,
            "w": 210,
            "h": 86,
            "accent": ACCENT["green"],
            "status": "active",
            "description": "Локальные отчёты по агентам, сценариям, каналам и CRM.",
            "responsibilities": ["Снимок состояния", "HTML/MD/JSON отчёты", "Сценарии"],
            "inputs": ["agent facts", "source facts", "scenario checks"],
            "outputs": ["agent_dashboard.json"],
            "tools": ["scripts/build_agent_dashboard.py", "data/reports/agent_dashboard.json"],
        },
        {
            "id": "svc-visual-api",
            "label": "Local Visual API",
            "type": "module",
            "x": 1540,
            "y": 1300,
            "w": 210,
            "h": 86,
            "accent": ACCENT["green"],
            "status": "active",
            "description": "Новый backend для визуализации. Только читает локальные отчёты и отдаёт их frontend.",
            "responsibilities": ["Serve frontend", "Expose /api/dashboard", "Generate runtime data.js"],
            "inputs": ["data/reports/agent_dashboard.json"],
            "outputs": ["window.AGENT_DATA", "JSON API"],
            "tools": ["backend/agent_dashboard_api/server.py", "frontend/agent-system-visual"],
        },
    ]


def _build_sources(source_map: dict[str, Any]) -> list[dict[str, Any]]:
    canonical = source_map.get("canonical_channels", [])
    first_wave = source_map.get("first_wave_channels", [])
    planned = source_map.get("planned_channels", [])
    wave2 = [c for c in planned if c.get("priority_wave") == "wave_2"]
    wave3 = [c for c in planned if c.get("priority_wave") == "wave_3"]
    watchlist = source_map.get("competitor_watchlist", [])
    pending = source_map.get("yanika_pending_channels", [])

    return [
        {
            "id": "src-wave1",
            "label": "Wave 1 · Первая волна",
            "type": "source",
            "x": 140,
            "y": 480,
            "w": 240,
            "h": 218,
            "accent": ACCENT["cyan"],
            "status": "active",
            "description": "Каналы MVP, которые проверяются первыми.",
            "list": [_channel_name(c) for c in first_wave] or [_channel_name(c) for c in canonical[:9]],
        },
        {
            "id": "src-wave2",
            "label": "Wave 2 · Платный охват",
            "type": "source",
            "x": 140,
            "y": 760,
            "w": 240,
            "h": 168,
            "accent": ACCENT["amber"],
            "status": "queued",
            "description": "Планируемые каналы после MVP.",
            "list": [_channel_name(c) for c in wave2],
        },
        {
            "id": "src-wave3",
            "label": "Wave 3 · Внешние сети",
            "type": "source",
            "x": 140,
            "y": 980,
            "w": 240,
            "h": 100,
            "accent": ACCENT["violet"],
            "status": "idle",
            "description": "Отложенные каналы для более поздней проверки.",
            "list": [_channel_name(c) for c in wave3],
        },
        {
            "id": "src-watchlist",
            "label": "Competitor Watchlist",
            "type": "source",
            "x": 140,
            "y": 220,
            "w": 240,
            "h": 116,
            "accent": ACCENT["grey"],
            "status": "idle",
            "description": "Конкуренты, каналы Яники и backlog-источники для Agent 1.",
            "list": [
                f"{len(watchlist)} competitors",
                f"{len(pending)} Yanika channels",
                f"{source_map.get('summary', {}).get('backlog_sources', 0)} backlog sources",
                f"{source_map.get('summary', {}).get('lecture_growth_sources', 0)} lecture growth sources",
            ],
        },
    ]


def _build_artifacts(dashboard: dict[str, Any]) -> list[dict[str, Any]]:
    base = [
        ("art-source", "Source Card", 880, 320, ACCENT["cyan"]),
        ("art-signal", "Signal Card", 880, 400, ACCENT["cyan"]),
        ("art-intake", "Intake Card", 880, 780, ACCENT["cyan"]),
        ("art-raw", "RawLead", 880, 870, ACCENT["cyan"]),
        ("art-qualified", "QualifiedLead", 1560, 700, ACCENT["green"]),
        ("art-score", "Score & Reason", 1560, 780, ACCENT["green"]),
        ("art-action", "Recommended Action", 1560, 860, ACCENT["green"]),
        ("art-content-brief", "Content Brief", 1560, 1000, ACCENT["amber"]),
        ("art-approval", "Approval Card", 1560, 1080, ACCENT["amber"]),
        ("art-draft", "Content Draft", 1560, 1160, ACCENT["amber"]),
        ("art-publication", "Manual Publication", 1560, 1240, ACCENT["amber"]),
        ("art-crm-preview", "CRM Payload Preview", 2200, 500, ACCENT["green"]),
        ("art-bitrix", "Bitrix24 Lead", 2200, 580, ACCENT["green"]),
        ("art-bitrix-deal", "Bitrix24 Deal", 2200, 660, ACCENT["green"]),
        ("art-tg", "Telegram Alert", 2200, 740, ACCENT["green"]),
        ("art-romi", "ROMI Report", 2200, 820, ACCENT["green"]),
        ("art-human", "Human Next Step", 2200, 900, ACCENT["amber"]),
        ("art-costs", "Channel Costs", 2200, 980, ACCENT["violet"]),
        ("art-facts", "Channel Facts", 2200, 1060, ACCENT["violet"]),
        ("art-dashboard", "Agent Dashboard", 2200, 1300, ACCENT["green"]),
        ("art-report", "REPORT.md Memory", 1660, 230, ACCENT["violet"]),
        ("art-checker", "Checker Report", 880, 230, ACCENT["amber"]),
        ("art-outreach", "OutreachLead", 880, 1180, ACCENT["amber"]),
        ("art-content-event", "Content Metric Event", 1760, 1240, ACCENT["amber"]),
    ]
    known = {item[0] for item in base}
    extra = []
    y = 1400
    for scenario in dashboard.get("scenario_artifact_contract", {}).get("scenarios", []):
        for artifact in scenario.get("required_artifacts", []):
            artifact_id = artifact_id_for(artifact)
            if artifact_id not in known:
                known.add(artifact_id)
                extra.append((artifact_id, _label_from_token(artifact), 1980, y, ACCENT["grey"]))
                y += 76

    return [
        {"id": artifact_id, "label": label, "type": "artifact", "x": x, "y": y, "w": 180, "h": 64, "accent": accent}
        for artifact_id, label, x, y, accent in [*base, *extra]
    ]


def _build_safety(locks: dict[str, Any], contract: dict[str, Any]) -> list[dict[str, str]]:
    safety = []
    for key, label in [
        ("scheduler_locked", "Scheduler locked"),
        ("mass_collection_locked", "Mass collection locked"),
        ("real_publish_locked", "Real publish locked"),
        ("real_outreach_locked", "Real outreach locked"),
    ]:
        if locks.get(key, True):
            safety.append({"id": f"lock-{key}", "label": label, "reason": key})
    if not locks.get("secrets_visible", False):
        safety.append({"id": "lock-secrets", "label": "Secrets hidden", "reason": "values are never shown"})
    safety.append({"id": "lock-agent7", "label": "No Agent 7", "reason": "checker is a service module, not a new agent"})
    for forbidden in contract.get("forbidden_actions", []):
        safety.append({"id": f"lock-{_slug(forbidden)}", "label": forbidden, "reason": "forbidden by scenario contract"})
    return safety


def _build_edges(dashboard: dict[str, Any], agent_node_ids: dict[str, str]) -> list[dict[str, Any]]:
    def e(edge_id: str, source: str, target: str, edge_type: str, label: str = "", animated: bool = False) -> dict[str, Any]:
        return {"id": edge_id, "source": source, "target": target, "type": edge_type, "label": label, "animated": animated}

    edges: list[dict[str, Any]] = [
        e("e-wl-a1", "src-watchlist", "a1-scout", "hierarchy", "watchlist"),
        e("e-w1-a1", "src-wave1", "a1-scout", "handoff", "signals"),
        e("e-w1-a2", "src-wave1", "a2-collector", "handoff", "leads"),
        e("e-w1-a6", "src-wave1", "a6-outreach", "handoff", "chats"),
        e("e-w2-a4", "src-wave2", "a4-publisher", "handoff", "content/ads"),
        e("e-w3-a4", "src-wave3", "a4-publisher", "hierarchy"),
    ]

    for agent_id, visual_id in agent_node_ids.items():
        edges.append(e(f"e-orch-{visual_id}", "orchestrator", visual_id, "hierarchy"))

    for idx, edge in enumerate(dashboard.get("agent_map", {}).get("edges", []), start=1):
        source = agent_node_ids.get(edge.get("from"))
        target = agent_node_ids.get(edge.get("to"))
        if source and target:
            edges.append(e(f"e-agent-map-{idx}", source, target, "handoff", edge.get("passes", ""), True))

    edges.extend([
        e("e-a1-source", "a1-scout", "art-source", "artifact", "source card"),
        e("e-a1-signal", "a1-scout", "art-signal", "artifact", "signal card"),
        e("e-source-a2", "art-source", "a2-collector", "handoff", "source card"),
        e("e-signal-a4", "art-signal", "a4-publisher", "handoff", "topics"),
        e("e-a2-raw", "a2-collector", "art-raw", "artifact", "raw lead"),
        e("e-raw-a3", "art-raw", "a3-processor", "handoff", "leads:raw", True),
        e("e-intake-a3", "art-intake", "a3-processor", "handoff", "first inbound"),
        e("e-a3-qualified", "a3-processor", "art-qualified", "artifact", "qualified lead"),
        e("e-a3-score", "a3-processor", "art-score", "artifact", "score"),
        e("e-a3-action", "a3-processor", "art-action", "artifact", "next action"),
        e("e-qualified-a5", "art-qualified", "a5-crm", "handoff", "CRM", True),
        e("e-a5-preview", "a5-crm", "art-crm-preview", "artifact", "payload"),
        e("e-a5-bitrix", "a5-crm", "art-bitrix", "artifact", "lead"),
        e("e-a5-deal", "a5-crm", "art-bitrix-deal", "artifact", "deal"),
        e("e-a5-tg", "a5-crm", "art-tg", "artifact", "alert"),
        e("e-a5-human", "a5-crm", "art-human", "feedback", "manual next step"),
        e("e-a5-romi", "a5-crm", "art-romi", "artifact", "ROMI"),
        e("e-a4-brief", "a4-publisher", "art-content-brief", "artifact", "brief"),
        e("e-a4-draft", "a4-publisher", "art-draft", "artifact", "draft"),
        e("e-a4-approval", "a4-publisher", "art-approval", "feedback", "approval"),
        e("e-a4-publish", "a4-publisher", "art-publication", "artifact", "manual publish"),
        e("e-content-event-a5", "art-content-event", "a5-crm", "handoff", "analytics"),
        e("e-a6-approval", "a6-outreach", "art-approval", "feedback", "approval"),
        e("e-a6-outreach", "a6-outreach", "art-outreach", "artifact", "outreach lead"),
        e("e-outreach-a5", "art-outreach", "a5-crm", "handoff", "interest", True),
        e("e-costs-a5", "art-costs", "a5-crm", "handoff", "costs"),
        e("e-facts-a5", "art-facts", "a5-crm", "handoff", "facts"),
        e("e-a5-dashboard", "a5-crm", "art-dashboard", "artifact", "dashboard"),
        e("e-orch-report", "orchestrator", "art-report", "artifact", "memory"),
        e("e-orch-checker", "orchestrator", "art-checker", "feedback", "QA"),
        e("e-checker-orch", "art-checker", "orchestrator", "feedback", "verdict"),
        e("e-a5-orch", "a5-crm", "orchestrator", "feedback", "analytics"),
        e("e-visual-api-dashboard", "svc-visual-api", "art-dashboard", "artifact", "live data"),
        e("e-dashboard-api", "art-dashboard", "svc-visual-api", "handoff", "JSON"),
        e("e-lock-scheduler", "svc-scheduler", "orchestrator", "safety", "locked"),
    ])
    return edges


def _build_scenarios(dashboard: dict[str, Any]) -> list[dict[str, Any]]:
    raw_scenarios = dashboard.get("scenario_artifact_contract", {}).get("scenarios", [])
    scenarios = []
    for index, scenario in enumerate(raw_scenarios, start=1):
        timeline = scenario.get("timeline") or []
        steps = []
        path = []
        for raw_step in timeline:
            node_id = node_id_for_step(str(raw_step))
            artifact_id = node_id if node_id.startswith("art-") else None
            steps.append({"t": _label_from_token(str(raw_step)), "node": node_id, **({"artifact": artifact_id} if artifact_id else {})})
            if node_id not in path:
                path.append(node_id)
        if not steps:
            continue
        scenarios.append({
            "id": f"s{index}",
            "label": scenario.get("name") or f"Scenario {index}",
            "summary": f"{' → '.join(_label_from_token(str(x)) for x in timeline[:6])}",
            "status": scenario.get("mvp_status", ""),
            "steps": steps,
            "path": path,
        })

    if scenarios:
        return scenarios

    return [{
        "id": "s1",
        "label": "Первый входящий запрос",
        "summary": "site/MAX/Telegram/email → Agent 3 → Agent 5 → human",
        "status": "fallback",
        "steps": [
            {"t": "Task received", "node": "orchestrator"},
            {"t": "Intake Card", "node": "art-intake", "artifact": "art-intake"},
            {"t": "Agent 3", "node": "a3-processor"},
            {"t": "Agent 5", "node": "a5-crm"},
            {"t": "Human Next Step", "node": "art-human", "artifact": "art-human"},
        ],
        "path": ["orchestrator", "art-intake", "a3-processor", "a5-crm", "art-human"],
    }]


def node_id_for_step(raw: str) -> str:
    token = raw.lower().strip()
    if "agent 1" in token or "scout" in token:
        return "a1-scout"
    if "agent 2" in token or "collector" in token:
        return "a2-collector"
    if "agent 3" in token or "processor" in token:
        return "a3-processor"
    if "agent 4" in token or "publisher" in token:
        return "a4-publisher"
    if "agent 5" in token or "crm" in token or "analytics" in token:
        return "a5-crm"
    if "agent 6" in token or "outreach" in token:
        return "a6-outreach"
    if "site" in token or "max" in token or "telegram" in token or "email" in token or "gmail" in token:
        return "src-wave1"
    if "human" in token or "человек" in token:
        return "art-human"
    if "bitrix" in token and "deal" in token:
        return "art-bitrix-deal"
    if "bitrix" in token:
        return "art-bitrix"
    for key, artifact_id in ARTIFACT_IDS.items():
        if key in token:
            return artifact_id
    return "orchestrator"


def artifact_id_for(raw: str) -> str:
    token = raw.lower().strip()
    for key, artifact_id in ARTIFACT_IDS.items():
        if key == token or key in token:
            return artifact_id
    return f"art-{_slug(token)}"


def _okr_metric(metric: dict[str, Any]) -> dict[str, Any]:
    return {
        "label": metric.get("name", "metric"),
        "current": metric.get("current_value", 0),
        "target": metric.get("target_value", 1),
        "unit": metric.get("unit", ""),
    }


def _subrole_responsibilities(subroles: list[dict[str, Any]]) -> list[str]:
    result = []
    for role in subroles[:7]:
        name = role.get("name", "Subrole")
        responsibility = role.get("responsibility", "")
        artifact = role.get("artifact", "")
        result.append(f"{name}: {responsibility} → {artifact}".strip())
    return result


def _status_from_panel(panel_status: str) -> str:
    status = (panel_status or "").lower()
    if "locked" in status:
        return "blocked"
    if "tested" in status:
        return "active"
    if "partial" in status:
        return "queued"
    if "dry" in status or "manual" in status:
        return "waiting"
    if "planned" in status:
        return "idle"
    return "idle"


def _format_agent_title(title: str) -> str:
    parts = title.split()
    if len(parts) >= 3 and parts[0].lower() == "agent" and parts[1].isdigit():
        return f"Agent {parts[1]} · {' '.join(parts[2:])}"
    return title


def _short_agent(agent_id: str) -> str:
    for prefix, short in [
        ("agent1", "A1"),
        ("agent2", "A2"),
        ("agent3", "A3"),
        ("agent4", "A4"),
        ("agent5", "A5"),
        ("agent6", "A6"),
    ]:
        if agent_id.startswith(prefix):
            return short
    return "A?"


def _metric_value(metric: dict[str, Any]) -> str:
    current = metric.get("current_value", "0")
    target = metric.get("target_value", "0")
    unit = metric.get("unit", "")
    if unit:
        return f"{current}/{target} {unit}"
    return f"{current}/{target}"


def _channel_name(channel: dict[str, Any]) -> str:
    return channel.get("channel_name") or channel.get("channel_id") or "unknown"


def _as_list(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item not in (None, "")]
    return [str(value)]


def _source_scope_to_list(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, dict):
        result = []
        if value.get("summary"):
            result.append(str(value["summary"]))
        for key, label in [
            ("primary_sources", "primary"),
            ("direct_owner_sources", "owner"),
            ("watchlist_sources", "watchlist"),
            ("yanika_pending_sources", "yanika"),
            ("backlog_sources", "backlog"),
        ]:
            items = value.get(key) or []
            for item in items[:6]:
                if isinstance(item, dict):
                    name = item.get("channel_name") or item.get("channel_id") or str(item)
                else:
                    name = str(item)
                result.append(f"{label}: {name}")
            if len(items) > 6:
                result.append(f"{label}: +{len(items) - 6} ещё")
        return result
    return _as_list(value)


def _label_from_token(raw: str) -> str:
    return raw.replace("_", " ").replace("/", " / ").strip()


def _slug(raw: str) -> str:
    return "".join(ch if ch.isalnum() else "-" for ch in raw.lower()).strip("-") or "item"


def _clip(raw: Any, limit: int) -> str:
    text = str(raw)
    return text if len(text) <= limit else f"{text[:limit - 1]}…"


if __name__ == "__main__":
    print(build_runtime_js(load_dashboard()))
