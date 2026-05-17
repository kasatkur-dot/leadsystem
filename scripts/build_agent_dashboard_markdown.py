"""Build a Markdown snapshot from data/reports/agent_dashboard.json.

The snapshot is read-only documentation for humans. It does not import runtime
agents and does not call Redis, Bitrix24, Telegram, IMAP, LLM APIs, scheduler,
publisher, or any external service.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_JSON_PATH = PROJECT_ROOT / "data" / "reports" / "agent_dashboard.json"
DASHBOARD_MD_PATH = PROJECT_ROOT / "data" / "reports" / "agent_dashboard.md"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _load_dashboard() -> dict[str, Any]:
    return json.loads(DASHBOARD_JSON_PATH.read_text(encoding="utf-8"))


def _safe(value: object) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "нет данных"
    return str(value).replace("\n", " ").strip()


def _table(headers: list[str], rows: list[list[object]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_safe(cell) for cell in row) + " |")
    return lines


def _metric_ratio(metric: dict[str, Any]) -> str:
    current = metric.get("current_value", "нет данных")
    target = metric.get("target_value", "нет данных")
    unit = metric.get("unit", "")
    direction = metric.get("direction", "at_least")
    if direction == "at_most":
        return f"{_safe(current)} <= {_safe(target)} {_safe(unit)}".strip()
    return f"{_safe(current)} / {_safe(target)} {_safe(unit)}".strip()


def _top_panel(data: dict[str, Any]) -> list[str]:
    top = data.get("top_panel", {})
    if not isinstance(top, dict):
        top = {}

    locks = top.get("locks", {})
    if not isinstance(locks, dict):
        locks = {}

    rows = [
        ["project_name", top.get("project_name", "нет данных")],
        ["overall_status", top.get("overall_status", "нет данных")],
        ["current_stage", top.get("current_stage", "нет данных")],
        ["next_small_step", top.get("next_small_step", "нет данных")],
        ["last_checked_at", top.get("last_checked_at", "нет данных")],
    ]
    lines = ["## Верхняя панель", ""]
    lines.extend(_table(["Поле", "Значение"], rows))
    lines.extend(["", "### Запреты", ""])
    lines.extend(_table(["Запрет", "Статус"], [[key, value] for key, value in locks.items()]))
    return lines


def _agent_map(data: dict[str, Any]) -> list[str]:
    agent_map = data.get("agent_map", {})
    if not isinstance(agent_map, dict):
        agent_map = {}
    agents = agent_map.get("agents", [])
    if not isinstance(agents, list):
        agents = []

    rows = []
    for agent in agents:
        if not isinstance(agent, dict):
            continue
        rows.append(
            [
                agent.get("title", "нет данных"),
                agent.get("department", "нет данных"),
                agent.get("panel_status", "нет данных"),
                agent.get("file", "нет данных"),
            ]
        )

    lines = ["## Карта агентов", ""]
    lines.extend(_table(["Агент", "Департамент", "Статус", "Файл"], rows))
    return lines


def _interaction_graph(data: dict[str, Any]) -> list[str]:
    graph = data.get("interaction_graph", {})
    if not isinstance(graph, dict):
        graph = {}
    routes = graph.get("routes", [])
    if not isinstance(routes, list):
        routes = []

    lines = ["## Карта взаимодействий агентов", ""]
    lines.append(_safe(graph.get("purpose", "как агенты передают результат друг другу")))
    lines.append("")
    for route in routes:
        if not isinstance(route, dict):
            continue
        nodes = route.get("nodes", [])
        if not isinstance(nodes, list):
            nodes = []
        lines.extend(
            [
                f"### {_safe(route.get('title', 'нет данных'))}",
                "",
                f"- Статус: `{_safe(route.get('status', 'нет данных'))}`",
                f"- Цепочка: {' -> '.join(_safe(node) for node in nodes)}",
                f"- Что проходит: {_safe(route.get('payload', 'нет данных'))}",
                f"- Safety: {_safe(route.get('safe_note', 'нет данных'))}",
                "",
            ]
        )
    return lines


def _management_protocol(data: dict[str, Any]) -> list[str]:
    protocol = data.get("management_protocol", {})
    if not isinstance(protocol, dict):
        protocol = {}

    chief = protocol.get("chief_of_staff", {})
    if not isinstance(chief, dict):
        chief = {}
    nervous_system = protocol.get("nervous_system", [])
    if not isinstance(nervous_system, list):
        nervous_system = []
    templates = protocol.get("templates", [])
    if not isinstance(templates, list):
        templates = []
    escalation_rules = protocol.get("escalation_rules", [])
    if not isinstance(escalation_rules, list):
        escalation_rules = []

    lines = [
        "## Chief of Staff / Handoff / Escalation / Weekly digest",
        "",
        f"- Статус: `{_safe(protocol.get('protocol_status', 'нет данных'))}`",
        f"- Источник: `{_safe(protocol.get('source_doc', 'нет данных'))}`",
        f"- Правило: {_safe(protocol.get('rule', 'агент = роль; skill = действие'))}",
        f"- Chief of Staff: {_safe(chief.get('owner', 'CLAUDE.md / AGENTS.md / REPORT.md'))}",
        f"- Смысл: {_safe(chief.get('meaning', 'режим координации, не новый агент'))}",
        f"- Ответственность: {_safe(chief.get('responsibility', 'нет данных'))}",
        "",
        "### Нервная система",
        "",
        " -> ".join(_safe(step) for step in nervous_system) if nervous_system else "нет данных",
        "",
        "### Шаблоны",
        "",
    ]

    rows = []
    for template in templates:
        if not isinstance(template, dict):
            continue
        fields = template.get("fields", [])
        if not isinstance(fields, list):
            fields = []
        rows.append(
            [
                template.get("name", "нет данных"),
                template.get("purpose", "нет данных"),
                ", ".join(_safe(field) for field in fields),
            ]
        )
    lines.extend(_table(["Шаблон", "Зачем", "Поля"], rows))
    lines.extend(["", "### Эскалация Янике", ""])
    if escalation_rules:
        lines.extend(f"- {_safe(rule)}" for rule in escalation_rules)
    else:
        lines.append("- нет данных")
    lines.extend(["", f"Weekly digest: {_safe(protocol.get('weekly_digest_owner', 'Agent 5/dashboard позже'))}", ""])
    return lines


def _mas_reference_layer(data: dict[str, Any]) -> list[str]:
    layer = data.get("mas_reference_layer", {})
    if not isinstance(layer, dict):
        layer = {}

    adopted_blocks = layer.get("adopted_blocks", [])
    scenario_timelines = layer.get("scenario_timelines", [])
    required_artifacts = layer.get("required_artifacts", [])
    statuses = layer.get("statuses", [])
    osint_rules = layer.get("osint_rules", [])
    later_locks = layer.get("later_locks", [])
    if not isinstance(adopted_blocks, list):
        adopted_blocks = []
    if not isinstance(scenario_timelines, list):
        scenario_timelines = []
    if not isinstance(required_artifacts, list):
        required_artifacts = []
    if not isinstance(statuses, list):
        statuses = []
    if not isinstance(osint_rules, list):
        osint_rules = []
    if not isinstance(later_locks, list):
        later_locks = []

    lines = [
        "## MAS Reference Layer",
        "",
        f"- Статус: `{_safe(layer.get('status', 'нет данных'))}`",
        f"- Источник: `{_safe(layer.get('source_doc', 'нет данных'))}`",
        f"- URL: `{_safe(layer.get('reference_url', 'нет данных'))}`",
        f"- Модель: {_safe(layer.get('model_summary', 'нет данных'))}",
        f"- Правило применения: {_safe(layer.get('application_rule', 'нет данных'))}",
        "",
        "### Что берём",
        "",
    ]
    rows = []
    for block in adopted_blocks:
        if not isinstance(block, dict):
            continue
        rows.append(
            [
                block.get("name", "нет данных"),
                block.get("meaning", "нет данных"),
                block.get("where", "нет данных"),
                block.get("mvp_status", "нет данных"),
            ]
        )
    lines.extend(_table(["Блок", "Зачем", "Где", "Статус"], rows))
    lines.extend(["", "### Сценарии", ""])
    scenario_rows = []
    for scenario in scenario_timelines:
        if not isinstance(scenario, dict):
            continue
        steps = scenario.get("steps", [])
        if not isinstance(steps, list):
            steps = []
        scenario_rows.append(
            [
                scenario.get("name", "нет данных"),
                " -> ".join(_safe(step) for step in steps),
                scenario.get("artifact", "нет данных"),
            ]
        )
    lines.extend(_table(["Сценарий", "Цепочка", "Артефакт"], scenario_rows))
    lines.extend(["", "### Артефакты", ""])
    artifact_rows = []
    for item in required_artifacts:
        if not isinstance(item, dict):
            continue
        artifact_rows.append([item.get("stage", "нет данных"), item.get("artifact", "нет данных")])
    lines.extend(_table(["Этап", "Артефакт"], artifact_rows))
    lines.extend(["", "### Status model", ""])
    lines.append(", ".join(f"`{_safe(status)}`" for status in statuses) if statuses else "нет данных")
    lines.extend(["", "### OSINT-правила", ""])
    lines.extend(f"- {_safe(rule)}" for rule in osint_rules)
    lines.extend(["", "### Later-locks", ""])
    lines.extend(f"- {_safe(rule)}" for rule in later_locks)
    return lines


def _security_agent_control_layer(data: dict[str, Any]) -> list[str]:
    layer = data.get("security_agent_control_layer", {})
    if not isinstance(layer, dict):
        layer = {}

    applied_to = layer.get("applied_to", [])
    red_lines = layer.get("red_lines", [])
    green_corridor = layer.get("green_corridor", [])
    risks = layer.get("ai_specific_risks", [])
    touchpoints = layer.get("agent_touchpoints", [])
    if not isinstance(applied_to, list):
        applied_to = []
    if not isinstance(red_lines, list):
        red_lines = []
    if not isinstance(green_corridor, list):
        green_corridor = []
    if not isinstance(risks, list):
        risks = []
    if not isinstance(touchpoints, list):
        touchpoints = []

    lines = [
        "## Security Agent Control Layer",
        "",
        f"- Статус: `{_safe(layer.get('status', 'нет данных'))}`",
        f"- Источник: `{_safe(layer.get('source_file', 'agents/Агент безопастности/AGENT_SECURITY.md'))}`",
        f"- Документ: `{_safe(layer.get('control_doc', 'docs/security-agent-control-layer.md'))}`",
        f"- Не Agent 7: `{_safe(layer.get('not_agent_7', True))}`",
        f"- Смысл: {_safe(layer.get('purpose', 'контроль безопасности для всех агентов'))}",
        "",
        "### Красные линии",
        "",
    ]
    lines.extend(f"- {_safe(item)}" for item in red_lines)
    lines.extend(["", "### Зелёный коридор", ""])
    lines.extend(f"- {_safe(item)}" for item in green_corridor)
    lines.extend(["", "### AI-риски", ""])
    lines.extend(f"- {_safe(item)}" for item in risks)
    lines.extend(["", "### Куда подключён", ""])
    lines.extend(f"- `{_safe(item)}`" for item in applied_to)
    lines.extend(["", "### По агентам", ""])
    rows = []
    for item in touchpoints:
        if isinstance(item, dict):
            rows.append([item.get("agent", "нет данных"), item.get("control", "нет данных")])
    lines.extend(_table(["Агент", "Контроль"], rows))
    return lines


def _source_label(source: dict[str, Any]) -> str:
    return _safe(
        source.get("channel_name")
        or source.get("source_name")
        or source.get("channel_id")
        or source.get("source_id")
        or "нет данных"
    )


def _source_rows(sources: list[Any], *, mode: str = "channel") -> list[list[object]]:
    rows: list[list[object]] = []
    for source in sources:
        if not isinstance(source, dict):
            continue
        if mode == "watch":
            rows.append(
                [
                    source.get("source_name", "нет данных"),
                    source.get("platform", ""),
                    source.get("segment", ""),
                    source.get("status", ""),
                    source.get("why_watch", ""),
                ]
            )
        else:
            rows.append(
                [
                    source.get("channel_name", "нет данных"),
                    source.get("priority_wave", ""),
                    source.get("status", ""),
                    source.get("owner_agent", ""),
                    source.get("flow", ""),
                    source.get("notes", ""),
                ]
            )
    return rows


def _source_map(data: dict[str, Any]) -> list[str]:
    source_map = data.get("source_map", {})
    if not isinstance(source_map, dict):
        source_map = {}
    summary = source_map.get("summary", {})
    if not isinstance(summary, dict):
        summary = {}
    canonical = source_map.get("canonical_channels", [])
    first_wave = source_map.get("first_wave_channels", [])
    planned = source_map.get("planned_channels", [])
    competitor = source_map.get("competitor_watchlist", [])
    lecture_growth = source_map.get("lecture_growth_source_map", [])
    yanika = source_map.get("yanika_pending_channels", [])
    backlog = source_map.get("backlog_sources", [])
    content_surfaces = source_map.get("content_surfaces", [])
    counts_by_owner = source_map.get("counts_by_owner", {})
    lecture_growth_score_summary = source_map.get("lecture_growth_score_summary", {})
    if not isinstance(canonical, list):
        canonical = []
    if not isinstance(first_wave, list):
        first_wave = []
    if not isinstance(planned, list):
        planned = []
    if not isinstance(competitor, list):
        competitor = []
    if not isinstance(lecture_growth, list):
        lecture_growth = []
    if not isinstance(yanika, list):
        yanika = []
    if not isinstance(backlog, list):
        backlog = []
    if not isinstance(content_surfaces, list):
        content_surfaces = []
    if not isinstance(counts_by_owner, dict):
        counts_by_owner = {}
    if not isinstance(lecture_growth_score_summary, dict):
        lecture_growth_score_summary = {}

    lines = [
        "## Карта источников",
        "",
        f"- Статус: `{_safe(source_map.get('source_map_status', 'нет данных'))}`",
        f"- Справочник: `{_safe(source_map.get('registry_file', 'нет данных'))}`",
        f"- Всего MVP-каналов: {_safe(summary.get('canonical_mvp_channels', 0))}",
        f"- Первая волна: {_safe(summary.get('wave_1_channels', 0))}",
        f"- Planned-каналы: {_safe(summary.get('planned_channels', 0))}",
        f"- Watchlist конкурентов: {_safe(summary.get('competitor_watchlist_sources', 0))}",
        f"- Источники из лекции 15.05: {_safe(summary.get('lecture_growth_sources', 0))}",
        f"- Каналы Яники ждут заполнения: {_safe(summary.get('yanika_pending_sources', 0))}",
        "",
        "### Каналы по владельцам",
        "",
    ]
    lines.extend(_table(["Владелец", "Каналов"], [[key, value] for key, value in counts_by_owner.items()]))
    lines.extend(["", "### Все 17 MVP-каналов", ""])
    lines.extend(_table(["Канал", "Волна", "Статус", "Владелец", "Flow", "Заметка"], _source_rows(canonical)))
    lines.extend(["", "### Первая волна", ""])
    lines.extend(_table(["Канал", "Волна", "Статус", "Владелец", "Flow", "Заметка"], _source_rows(first_wave)))
    lines.extend(["", "### Planned-каналы", ""])
    lines.extend(_table(["Канал", "Волна", "Статус", "Владелец", "Flow", "Заметка"], _source_rows(planned)))
    lines.extend(["", "### Контентные поверхности Agent 4", ""])
    lines.extend(f"- {_safe(item)}" for item in content_surfaces)
    lines.extend(["", "### Watchlist конкурентов Agent 1", ""])
    lines.extend(_table(["Источник", "Платформа", "Сегмент", "Статус", "Зачем смотреть"], _source_rows(competitor, mode="watch")))
    lines.extend(["", "### Growth source map из лекции 15.05", ""])
    lines.append(f"Файл: `{_safe(source_map.get('lecture_growth_source_map_file', 'нет данных'))}`")
    lines.append(f"Скоринг: `{_safe(source_map.get('lecture_growth_score_status', 'нет данных'))}`")
    lines.append(f"Отчёт скоринга: `{_safe(source_map.get('lecture_growth_score_report', 'нет данных'))}`")
    lines.append(f"Требуют approval или уточнения: {_safe(lecture_growth_score_summary.get('approval_required_count', 'нет данных'))}")
    lines.append("")
    lines.extend(_table(["Источник", "Платформа", "Сегмент", "Статус", "Зачем смотреть"], _source_rows(lecture_growth, mode="watch")))
    lines.extend(["", "### Каналы Яники: ждут ссылок", ""])
    lines.extend(_table(["Источник", "Платформа", "Сегмент", "Статус", "Зачем смотреть"], _source_rows(yanika, mode="watch")))
    lines.extend(["", "### Backlog-источники", ""])
    lines.extend(f"- {_safe(item)}" for item in backlog)
    return lines


def _agent_details(data: dict[str, Any]) -> list[str]:
    agents = data.get("agent_details", [])
    if not isinstance(agents, list):
        agents = []

    lines = ["## Детали агентов", ""]
    for agent in agents:
        if not isinstance(agent, dict):
            continue
        lines.extend(
            [
                f"### {_safe(agent.get('title', 'нет данных'))}",
                "",
                f"- Департамент: {_safe(agent.get('department', 'нет данных'))}",
                f"- Готовность: {_safe(agent.get('readiness_percent', 'нет данных'))}%",
                f"- KR-готовность: {_safe(agent.get('okr_readiness_percent', 'нет данных'))}%",
                f"- Описание: {_safe(agent.get('description', 'нет данных'))}",
                f"- OKR: {_safe(agent.get('okr', 'нет данных'))}",
                f"- Что доделать: {_safe(agent.get('todo', agent.get('next_action', 'нет данных')))}",
                "",
            ]
        )
        source_scope = agent.get("source_scope", {})
        lines.extend(["Источники по агенту:", ""])
        if isinstance(source_scope, dict):
            primary_sources = source_scope.get("primary_sources", [])
            watchlist_sources = source_scope.get("watchlist_sources", [])
            yanika_pending = source_scope.get("yanika_pending_sources", [])
            content_surfaces = source_scope.get("content_surfaces", [])
            backlog_sources = source_scope.get("backlog_sources", [])
            if not isinstance(primary_sources, list):
                primary_sources = []
            if not isinstance(watchlist_sources, list):
                watchlist_sources = []
            if not isinstance(yanika_pending, list):
                yanika_pending = []
            if not isinstance(content_surfaces, list):
                content_surfaces = []
            if not isinstance(backlog_sources, list):
                backlog_sources = []
            lines.extend(
                [
                    f"- Смысл: {_safe(source_scope.get('summary', 'нет данных'))}",
                    f"- Основных источников: {_safe(source_scope.get('source_count', len(primary_sources)))}",
                    f"- Watchlist: {_safe(source_scope.get('watchlist_count', len(watchlist_sources)))}",
                    f"- Каналы Яники ждут: {_safe(source_scope.get('yanika_pending_count', len(yanika_pending)))}",
                    "",
                ]
            )
            if primary_sources:
                lines.extend("- " + _source_label(source) for source in primary_sources if isinstance(source, dict))
            if content_surfaces:
                lines.extend(["", "Контентные поверхности:"])
                lines.extend(f"- {_safe(surface)}" for surface in content_surfaces)
            if watchlist_sources:
                lines.extend(["", "Watchlist:"])
                lines.extend("- " + _source_label(source) for source in watchlist_sources if isinstance(source, dict))
            if yanika_pending:
                lines.extend(["", "Каналы Яники ждут заполнения:"])
                lines.extend("- " + _source_label(source) for source in yanika_pending if isinstance(source, dict))
            if backlog_sources:
                lines.extend(["", "Backlog-источники:"])
                lines.extend(f"- {_safe(source)}" for source in backlog_sources)
            lines.append("")
        else:
            lines.extend(["- нет данных", ""])
        lines.append("Главная метрика:")
        main_metric = agent.get("main_metric", {})
        if isinstance(main_metric, dict) and main_metric:
            lines.extend(
                [
                    f"- {_safe(main_metric.get('name', 'нет данных'))}: {_metric_ratio(main_metric)}",
                    f"- Когда закрыта: {_safe(main_metric.get('done_when', 'нет данных'))}",
                    "",
                ]
            )
        else:
            lines.extend(["- нет данных", ""])

        okr_metrics = agent.get("okr_metrics", [])
        lines.extend(["OKR/KR метрики:", ""])
        if isinstance(okr_metrics, list) and okr_metrics:
            rows = []
            for metric in okr_metrics:
                if isinstance(metric, dict):
                    rows.append([metric.get("name", "нет данных"), _metric_ratio(metric)])
            lines.extend(_table(["Метрика", "Число"], rows))
        else:
            lines.append("- нет данных")
        lines.extend(["", "Защитные метрики:"])
        guard_metrics = agent.get("guard_metrics", [])
        if isinstance(guard_metrics, list) and guard_metrics:
            lines.extend(f"- {_safe(metric)}" for metric in guard_metrics)
        else:
            lines.append("- нет данных")

        subroles = agent.get("subroles", [])
        lines.extend(["", "Суброли:"])
        if isinstance(subroles, list) and subroles:
            rows = []
            for subrole in subroles:
                if isinstance(subrole, dict):
                    rows.append(
                        [
                            subrole.get("name", "нет данных"),
                            subrole.get("responsibility", "нет данных"),
                            subrole.get("artifact", "нет данных"),
                            subrole.get("kpi", "нет данных"),
                        ]
                    )
            lines.extend(_table(["Суброль", "Что делает", "Артефакт", "KPI"], rows))
        else:
            lines.append("- нет данных")
        lines.extend(
            [
                "",
                "Скиллы:",
            ]
        )
        skills = agent.get("skills", [])
        if isinstance(skills, list) and skills:
            lines.extend(f"- {_safe(skill)}" for skill in skills)
        else:
            lines.append("- нет данных")
        lines.append("")
    return lines


def _scenario_artifact_contract(data: dict[str, Any]) -> list[str]:
    contract = data.get("scenario_artifact_contract", {})
    if not isinstance(contract, dict):
        contract = {}
    scenarios = contract.get("scenarios", [])
    statuses = contract.get("statuses", [])
    forbidden_actions = contract.get("forbidden_actions", [])
    if not isinstance(scenarios, list):
        scenarios = []
    if not isinstance(statuses, list):
        statuses = []
    if not isinstance(forbidden_actions, list):
        forbidden_actions = []

    lines = [
        "## Scenario Artifact Contract",
        "",
        f"- Статус: `{_safe(contract.get('status', 'нет данных'))}`",
        f"- Документ сценариев: `{_safe(contract.get('source_doc', 'нет данных'))}`",
        f"- Документ субролей: `{_safe(contract.get('subroles_doc', 'нет данных'))}`",
        f"- Правило: {_safe(contract.get('rule', 'нет данных'))}",
        "",
        "### Сценарии и артефакты",
        "",
    ]
    rows = []
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            continue
        timeline = scenario.get("timeline", [])
        artifacts = scenario.get("required_artifacts", [])
        if not isinstance(timeline, list):
            timeline = []
        if not isinstance(artifacts, list):
            artifacts = []
        rows.append(
            [
                scenario.get("name", "нет данных"),
                " -> ".join(_safe(step) for step in timeline),
                ", ".join(_safe(item) for item in artifacts),
                scenario.get("mvp_status", "нет данных"),
            ]
        )
    lines.extend(_table(["Сценарий", "Timeline", "Артефакты", "MVP-статус"], rows))
    lines.extend(["", "### Единый Status model", ""])
    lines.append(", ".join(f"`{_safe(status)}`" for status in statuses) if statuses else "нет данных")
    lines.extend(["", "### Запреты", ""])
    lines.extend(f"- {_safe(item)}" for item in forbidden_actions)
    return lines


def _bitrix_crm_hygiene(data: dict[str, Any]) -> list[str]:
    hygiene = data.get("bitrix_crm_hygiene", {})
    if not isinstance(hygiene, dict) or not hygiene:
        return ["## Bitrix CRM Hygiene", "", "- нет данных"]

    counts = hygiene.get("counts", {})
    quality = hygiene.get("quality_flags", {})
    duplicates = hygiene.get("duplicate_groups", {})
    lead_sources = hygiene.get("lead_sources", [])
    deal_stages = hygiene.get("deal_stages", [])
    queue = hygiene.get("first_cleanup_queue", [])
    if not isinstance(counts, dict):
        counts = {}
    if not isinstance(quality, dict):
        quality = {}
    if not isinstance(duplicates, dict):
        duplicates = {}
    if not isinstance(lead_sources, list):
        lead_sources = []
    if not isinstance(deal_stages, list):
        deal_stages = []
    if not isinstance(queue, list):
        queue = []

    lines = [
        "## Bitrix CRM Hygiene",
        "",
        f"- Статус: `{_safe(hygiene.get('status', 'нет данных'))}`",
        f"- Отчёт: `{_safe(hygiene.get('report_file', 'нет данных'))}`",
        f"- Сформирован: `{_safe(hygiene.get('generated_at', 'нет данных'))}`",
        f"- Полный отчёт: `{not bool(hygiene.get('limited_by_pages'))}`",
        "",
        "### Сводка",
        "",
    ]
    lines.extend(_table(["Метрика", "Значение"], [[key, value] for key, value in counts.items()]))
    lines.extend(["", "### Качество данных", ""])
    lines.extend(_table(["Проблема", "Количество"], [[key, value] for key, value in quality.items()]))
    lines.extend(["", "### Дубли", ""])
    lines.extend(_table(["Тип", "Групп"], [[key, value] for key, value in duplicates.items()]))
    lines.extend(["", "### Источники лидов", ""])
    lines.extend(_table(["ID", "Название", "Кол-во"], [[item.get("source_id", ""), item.get("name", ""), item.get("count", "")] for item in lead_sources[:12] if isinstance(item, dict)]))
    lines.extend(["", "### Стадии сделок", ""])
    lines.extend(_table(["ID", "Кол-во"], [[item.get("stage_id", ""), item.get("count", "")] for item in deal_stages[:12] if isinstance(item, dict)]))
    lines.extend(["", "### Очередь чистки", ""])
    lines.extend(f"- {_safe(item)}" for item in queue)
    lines.append("")
    return lines


def _vpp_ai_manager_dry_run(data: dict[str, Any]) -> list[str]:
    dry_run = data.get("vpp_ai_manager_dry_run", {})
    if not isinstance(dry_run, dict) or not dry_run:
        return ["## VPP AI-manager dry-run", "", "- нет данных"]

    summary = dry_run.get("summary", {})
    scenarios = dry_run.get("scenarios", [])
    external_calls = dry_run.get("external_calls", {})
    if not isinstance(summary, dict):
        summary = {}
    if not isinstance(scenarios, list):
        scenarios = []
    if not isinstance(external_calls, dict):
        external_calls = {}

    lines = [
        "## VPP AI-manager dry-run",
        "",
        f"- Статус: `{_safe(dry_run.get('status', 'нет данных'))}`",
        f"- Dry-run: `{_safe(dry_run.get('dry_run', 'нет данных'))}`",
        f"- Сценариев: `{_safe(dry_run.get('scenario_count', 0))}`",
        f"- Отчёт: `{_safe(dry_run.get('report_file', 'нет данных'))}`",
        f"- Markdown: `{_safe(dry_run.get('markdown_report', 'нет данных'))}`",
        "",
        "### Сводка",
        "",
    ]
    lines.extend(_table(["Метрика", "Значение"], [[key, value] for key, value in summary.items()]))
    lines.extend(["", "### Сценарии", ""])
    rows = []
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            continue
        missing = scenario.get("missing_data", [])
        if not isinstance(missing, list):
            missing = []
        rows.append(
            [
                scenario.get("title", "нет данных"),
                scenario.get("segment", "нет данных"),
                scenario.get("flow", "нет данных"),
                scenario.get("score", "нет данных"),
                scenario.get("data_completeness", "нет данных"),
                ", ".join(_safe(item) for item in missing) if missing else "нет",
                scenario.get("next_action", "нет данных"),
                scenario.get("kp_24h_allowed", False),
                scenario.get("bitrix_send_status", "нет данных"),
            ]
        )
    lines.extend(
        _table(
            ["Сценарий", "Сегмент", "Flow", "Score", "Данные", "Чего не хватает", "Следующий шаг", "КП 24ч", "Bitrix"],
            rows,
        )
    )
    lines.extend(["", "### Внешние вызовы", ""])
    lines.extend(_table(["Сервис", "Вызван"], [[key, value] for key, value in external_calls.items()]))
    lines.extend(["", f"Safety: {_safe(dry_run.get('safety_note', 'нет данных'))}", ""])
    return lines


def _first_safe_growth_tests(data: dict[str, Any]) -> list[str]:
    report = data.get("first_safe_growth_tests", {})
    if not isinstance(report, dict) or not report:
        return ["## First Safe Growth Tests", "", "- нет данных"]
    tests = report.get("tests", [])
    deferred = report.get("deferred_items", [])
    if not isinstance(tests, list):
        tests = []
    if not isinstance(deferred, list):
        deferred = []

    rows = []
    for test in tests:
        if not isinstance(test, dict):
            continue
        rows.append(
            [
                test.get("test_id", "нет данных"),
                test.get("source_name", "нет данных"),
                test.get("mode", "нет данных"),
                test.get("proposed_action", "нет данных"),
                test.get("approval_required", "нет данных"),
                test.get("stop_rule", "нет данных"),
            ]
        )

    lines = [
        "## First Safe Growth Tests",
        "",
        f"- Статус: `{_safe(report.get('status', 'нет данных'))}`",
        f"- Тестов: `{_safe(report.get('tests_count', 0))}`",
        f"- Отчёт: `{_safe(report.get('report_file', 'нет данных'))}`",
        "",
    ]
    lines.extend(_table(["ID", "Источник", "Режим", "Действие", "Approval", "Stop rule"], rows))
    lines.extend(["", "### Отложено", ""])
    lines.extend(f"- {_safe(item)}" for item in deferred)
    lines.append("")
    return lines


def _bitrix_reactivation_readonly_plan(data: dict[str, Any]) -> list[str]:
    report = data.get("bitrix_reactivation_readonly_plan", {})
    if not isinstance(report, dict) or not report:
        return ["## Bitrix Reactivation Readonly Plan", "", "- нет данных"]
    summary = report.get("summary", {})
    cleanup_queue = report.get("cleanup_queue", [])
    buckets = report.get("reactivation_buckets", [])
    approvals = report.get("approval_required_before", [])
    if not isinstance(summary, dict):
        summary = {}
    if not isinstance(cleanup_queue, list):
        cleanup_queue = []
    if not isinstance(buckets, list):
        buckets = []
    if not isinstance(approvals, list):
        approvals = []

    lines = [
        "## Bitrix Reactivation Readonly Plan",
        "",
        f"- Статус: `{_safe(report.get('status', 'нет данных'))}`",
        f"- Отчёт: `{_safe(report.get('report_file', 'нет данных'))}`",
        f"- Audit limited_by_pages: `{_safe(report.get('limited_by_pages', 'нет данных'))}`",
        "",
        "### Summary",
        "",
    ]
    lines.extend(_table(["Метрика", "Значение"], [[key, value] for key, value in summary.items()]))
    lines.extend(["", "### Cleanup Queue", ""])
    lines.extend(
        _table(
            ["ID", "Очередь", "Count", "Priority", "Action"],
            [
                [
                    item.get("queue_id", ""),
                    item.get("title", ""),
                    item.get("count", ""),
                    item.get("priority", ""),
                    item.get("action", ""),
                ]
                for item in cleanup_queue
                if isinstance(item, dict)
            ],
        )
    )
    lines.extend(["", "### Reactivation Buckets", ""])
    lines.extend(
        _table(
            ["ID", "Группа", "Priority", "Status"],
            [
                [
                    item.get("bucket_id", ""),
                    item.get("title", ""),
                    item.get("priority", ""),
                    item.get("first_message_status", ""),
                ]
                for item in buckets
                if isinstance(item, dict)
            ],
        )
    )
    lines.extend(["", "### Нужен approval перед", ""])
    lines.extend(f"- `{_safe(item)}`" for item in approvals)
    lines.append("")
    return lines


def _tender_filter_pack_dry_run(data: dict[str, Any]) -> list[str]:
    report = data.get("tender_filter_pack_dry_run", {})
    if not isinstance(report, dict) or not report:
        return ["## Tender Filter Pack Dry Run", "", "- нет данных"]
    checks = report.get("checks", [])
    approvals = report.get("approval_required_before", [])
    if not isinstance(checks, list):
        checks = []
    if not isinstance(approvals, list):
        approvals = []
    lines = [
        "## Tender Filter Pack Dry Run",
        "",
        f"- Статус: `{_safe(report.get('status', 'нет данных'))}`",
        f"- Фильтров: `{_safe(report.get('filter_count', 0))}`",
        f"- Файл: `{_safe(report.get('filter_file', 'нет данных'))}`",
        f"- Отчёт: `{_safe(report.get('report_file', 'нет данных'))}`",
        "",
    ]
    lines.extend(
        _table(
            ["Filter", "Segment", "Priority", "Status", "Stop rule"],
            [
                [
                    item.get("filter_id", ""),
                    item.get("segment", ""),
                    item.get("priority", ""),
                    item.get("status", ""),
                    item.get("stop_rule", ""),
                ]
                for item in checks
                if isinstance(item, dict)
            ],
        )
    )
    lines.extend(["", "### Нужен approval перед", ""])
    lines.extend(f"- `{_safe(item)}`" for item in approvals)
    lines.append("")
    return lines


def _client_acquisition_pack_dry_run(data: dict[str, Any]) -> list[str]:
    report = data.get("client_acquisition_pack_dry_run", {})
    if not isinstance(report, dict) or not report:
        return ["## Client Acquisition Pack", "", "- нет данных"]
    summary = report.get("summary", {})
    routes = report.get("routes", [])
    assets = report.get("supporting_assets", [])
    if not isinstance(summary, dict):
        summary = {}
    if not isinstance(routes, list):
        routes = []
    if not isinstance(assets, list):
        assets = []
    lines = [
        "## Client Acquisition Pack",
        "",
        f"- Статус: `{_safe(report.get('status', 'нет данных'))}`",
        f"- Маршрутов: `{_safe(report.get('route_count', 0))}`",
        f"- Approval required: `{_safe(summary.get('approval_required_routes', 0))}`",
        f"- Отчёт: `{_safe(report.get('report_file', 'нет данных'))}`",
        "",
    ]
    lines.extend(
        _table(
            ["Route", "Segment", "Priority", "Source", "Offer", "Approval"],
            [
                [
                    item.get("route_id", ""),
                    item.get("segment", ""),
                    item.get("priority", ""),
                    item.get("primary_source", ""),
                    item.get("offer", ""),
                    item.get("approval_gate", ""),
                ]
                for item in routes
                if isinstance(item, dict)
            ],
        )
    )
    lines.extend(["", "### Supporting assets", ""])
    lines.extend(f"- `{_safe(item)}`" for item in assets)
    lines.append("")
    return lines


def _three_qualified_leads_sprint(data: dict[str, Any]) -> list[str]:
    report = data.get("three_qualified_leads_sprint", {})
    if not isinstance(report, dict) or not report:
        return ["## Three Qualified Leads Sprint", "", "- нет данных"]
    mapping = report.get("astrology_method_mapping", {})
    items = report.get("items", [])
    if not isinstance(mapping, dict):
        mapping = {}
    if not isinstance(items, list):
        items = []
    lines = [
        "## Three Qualified Leads Sprint",
        "",
        f"- Статус: `{_safe(report.get('status', 'нет данных'))}`",
        f"- Цель: `{_safe(report.get('goal', 'нет данных'))}`",
        f"- Sprint items: `{_safe(report.get('sprint_items_count', 0))}`",
        f"- Target qualified leads: `{_safe(report.get('qualified_lead_target_count', 0))}`",
        f"- Ready/draft items: `{_safe(report.get('ready_or_draft_items', 0))}`",
        f"- Approval required items: `{_safe(report.get('approval_required_items', 0))}`",
        f"- Отчёт: `{_safe(report.get('report_file', 'нет данных'))}`",
        "",
        "### Перенос астрометодики",
        "",
    ]
    lines.extend(f"- `{_safe(key)}`: {_safe(value)}" for key, value in mapping.items())
    lines.extend(["", "### Sprint items", ""])
    lines.extend(
        _table(
            ["ID", "Week", "Segment", "Agent", "Source", "Metric", "Target", "Status", "Next"],
            [
                [
                    item.get("sprint_item_id", ""),
                    item.get("week", ""),
                    item.get("segment", ""),
                    item.get("agent_owner", ""),
                    item.get("source", ""),
                    item.get("goal_metric", ""),
                    item.get("target_count", ""),
                    item.get("status", ""),
                    item.get("next_action", ""),
                ]
                for item in items
                if isinstance(item, dict)
            ],
        )
    )
    lines.append("")
    return lines


def _events(data: dict[str, Any], limit: int = 10) -> list[str]:
    events = data.get("event_stream", [])
    if not isinstance(events, list):
        events = []

    rows = []
    for event in events[:limit]:
        if not isinstance(event, dict):
            continue
        rows.append(
            [
                event.get("created_at", "нет данных"),
                event.get("event_type", "нет данных"),
                event.get("status", "нет данных"),
                event.get("report_file", "нет данных"),
            ]
        )

    lines = ["## Event stream", ""]
    lines.extend(_table(["Время", "Событие", "Статус", "Файл"], rows))
    return lines


def _metrics(data: dict[str, Any]) -> list[str]:
    metrics = data.get("metrics_dashboard", {})
    if not isinstance(metrics, dict):
        metrics = {}

    lines = ["## Dashboard метрик", ""]
    for group_name, values in metrics.items():
        if not isinstance(values, dict):
            continue
        lines.extend([f"### {_safe(group_name)}", ""])
        lines.extend(_table(["Метрика", "Значение"], [[key, value] for key, value in values.items()]))
        lines.append("")
    return lines


def _checker(data: dict[str, Any]) -> list[str]:
    checker = data.get("checker", {})
    if not isinstance(checker, dict):
        checker = {}
    return [
        "## Checker",
        "",
        *_table(["Поле", "Значение"], [[key, value] for key, value in checker.items()]),
    ]


def build_markdown() -> str:
    data = _load_dashboard()
    lines: list[str] = [
        "# Agent Dashboard Snapshot",
        "",
        f"Дата сборки: `{_utc_now()}`",
        "",
        "Статус: read-only Markdown-снимок из `data/reports/agent_dashboard.json`.",
        "",
        "Безопасность: этот снимок не запускает Redis, Bitrix24, Telegram, IMAP, LLM, scheduler, publisher и не показывает значения секретов.",
        "",
    ]
    for section in [
        _top_panel,
        _agent_map,
        _source_map,
        _bitrix_crm_hygiene,
        _vpp_ai_manager_dry_run,
        _first_safe_growth_tests,
        _bitrix_reactivation_readonly_plan,
        _tender_filter_pack_dry_run,
        _client_acquisition_pack_dry_run,
        _three_qualified_leads_sprint,
        _interaction_graph,
        _management_protocol,
        _mas_reference_layer,
        _security_agent_control_layer,
        _scenario_artifact_contract,
        _agent_details,
        _events,
        _metrics,
        _checker,
    ]:
        lines.extend(section(data))
        lines.append("")
    lines.extend(
        [
            "## Следующий маленький шаг",
            "",
            _safe(data.get("next_small_step", "нет данных")),
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    markdown = build_markdown()
    DASHBOARD_MD_PATH.write_text(markdown, encoding="utf-8")

    data = _load_dashboard()
    agents_count = data.get("agent_map", {}).get("agents_count", "нет данных")
    event_count = len(data.get("event_stream", [])) if isinstance(data.get("event_stream"), list) else 0

    print("dashboard_markdown_build_status=OK")
    print(f"agents_count={agents_count}")
    print(f"event_count={event_count}")
    print("external_calls=redis:False,bitrix24:False,telegram_send:False,imap:False,llm:False,scheduler:False,publisher:False")
    print(f"report_file={DASHBOARD_MD_PATH.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
