"""Build a static local HTML viewer from data/reports/agent_dashboard.json.

The generated page is a read-only snapshot. It does not fetch data, import
runtime agents, call Redis, Bitrix24, Telegram, IMAP, LLM APIs, scheduler,
publisher, or any external service.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_JSON_PATH = PROJECT_ROOT / "data" / "reports" / "agent_dashboard.json"
DASHBOARD_HTML_PATH = PROJECT_ROOT / "data" / "reports" / "agent_dashboard.html"

SECRET_KEY_MARKERS = (
    "api_key",
    "apikey",
    "secret",
    "token",
    "password",
    "passwd",
    "webhook",
    "hash",
)

PROHIBITIONS = [
    "Не запускать scheduler без отдельного подтверждения.",
    "Не запускать массовый сбор лидов.",
    "Не публиковать реальные посты.",
    "Не отправлять outreach-сообщения.",
    "Не показывать значения секретов.",
    "Не создавать Agent 7.",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _load_dashboard() -> dict[str, Any]:
    return json.loads(DASHBOARD_JSON_PATH.read_text(encoding="utf-8"))


def _e(value: object) -> str:
    return escape(str(value), quote=True)


def _hide_key(key: str) -> bool:
    normalized = key.lower()
    return any(marker in normalized for marker in SECRET_KEY_MARKERS)


def _safe_text(value: object) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "нет данных"
    return str(value)


def _status_class(status: object) -> str:
    text = _safe_text(status).lower()
    if text in {"ok", "found", "tested"} or text.endswith("_ok"):
        return "is-ok"
    if "dry" in text or "planned" in text or "partial" in text:
        return "is-wait"
    if "lock" in text or "abort" in text or "fail" in text or "missing" in text:
        return "is-bad"
    return "is-neutral"


def _kv_grid(data: dict[str, Any], *, skip_secret_keys: bool = True) -> str:
    items = []
    for key, value in data.items():
        if skip_secret_keys and _hide_key(key):
            continue
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        items.append(
            "<div class=\"kv-item\">"
            f"<span>{_e(key)}</span>"
            f"<strong>{_e(_safe_text(value))}</strong>"
            "</div>"
        )
    return "\n".join(items)


def _tag_list(values: list[Any], class_name: str = "tag") -> str:
    if not values:
        return "<span class=\"muted\">нет данных</span>"
    return "\n".join(f"<span class=\"{class_name}\">{_e(_safe_text(value))}</span>" for value in values)


def _metric_ratio(metric: dict[str, Any]) -> str:
    current = metric.get("current_value", "нет данных")
    target = metric.get("target_value", "нет данных")
    unit = metric.get("unit", "")
    direction = metric.get("direction", "at_least")
    sign = "<=" if direction == "at_most" else "/"
    if direction == "at_most":
        return f"{_safe_text(current)} {sign} {_safe_text(target)} {_safe_text(unit)}".strip()
    return f"{_safe_text(current)} / {_safe_text(target)} {_safe_text(unit)}".strip()


def _okr_metric_list(metrics: list[Any]) -> str:
    if not metrics:
        return "<p class=\"muted\">нет данных</p>"
    rows = []
    for item in metrics:
        if not isinstance(item, dict):
            continue
        rows.append(
            "<article class=\"okr-metric-row\">"
            f"<span>{_e(item.get('name', 'нет данных'))}</span>"
            f"<strong>{_e(_metric_ratio(item))}</strong>"
            "</article>"
        )
    return "\n".join(rows) if rows else "<p class=\"muted\">нет данных</p>"


def _main_metric(metric: dict[str, Any]) -> str:
    if not isinstance(metric, dict) or not metric:
        return "<p class=\"muted\">нет данных</p>"
    return (
        "<article class=\"main-metric-card\">"
        f"<span>Главная метрика</span>"
        f"<strong>{_e(metric.get('name', 'нет данных'))}</strong>"
        f"<em>{_e(_metric_ratio(metric))}</em>"
        f"<p>{_e(metric.get('done_when', 'нет данных'))}</p>"
        "</article>"
    )


def _source_name(source: dict[str, Any]) -> str:
    return _safe_text(
        source.get("channel_name")
        or source.get("source_name")
        or source.get("channel_id")
        or source.get("source_id")
        or "нет данных"
    )


def _source_id(source: dict[str, Any]) -> str:
    return _safe_text(source.get("channel_id") or source.get("source_id") or "")


def _source_tags(sources: list[Any], *, max_items: int | None = None) -> str:
    if not sources:
        return "<span class=\"muted\">нет данных</span>"
    items = sources[:max_items] if max_items else sources
    tags = []
    for source in items:
        if not isinstance(source, dict):
            continue
        meta = " / ".join(
            value
            for value in [
                _safe_text(source.get("priority_wave") or source.get("platform") or ""),
                _safe_text(source.get("status") or ""),
            ]
            if value
        )
        label = _source_name(source)
        source_id = _source_id(source)
        suffix = f" ({source_id})" if source_id else ""
        tags.append(f"<span class=\"tag tag--source\">{_e(label)}{_e(suffix)}<small>{_e(meta)}</small></span>")
    if max_items and len(sources) > max_items:
        tags.append(f"<span class=\"tag tag--source\">ещё {_e(len(sources) - max_items)}</span>")
    return "\n".join(tags) if tags else "<span class=\"muted\">нет данных</span>"


def _source_table(sources: list[Any], *, mode: str = "channel") -> str:
    if not sources:
        return "<p class=\"muted\">нет данных</p>"
    rows = []
    for source in sources:
        if not isinstance(source, dict):
            continue
        if mode == "watch":
            rows.append(
                "<tr>"
                f"<td>{_e(source.get('source_name', 'нет данных'))}</td>"
                f"<td>{_e(source.get('platform', ''))}</td>"
                f"<td>{_e(source.get('segment', ''))}</td>"
                f"<td>{_e(source.get('status', ''))}</td>"
                f"<td>{_e(source.get('why_watch', ''))}</td>"
                "</tr>"
            )
        else:
            rows.append(
                "<tr>"
                f"<td>{_e(source.get('channel_name', 'нет данных'))}</td>"
                f"<td>{_e(source.get('priority_wave', ''))}</td>"
                f"<td>{_e(source.get('status', ''))}</td>"
                f"<td>{_e(source.get('owner_agent', ''))}</td>"
                f"<td>{_e(source.get('flow', ''))}</td>"
                f"<td>{_e(source.get('notes', ''))}</td>"
                "</tr>"
            )
    if mode == "watch":
        header = "<tr><th>Источник</th><th>Платформа</th><th>Сегмент</th><th>Статус</th><th>Зачем смотреть</th></tr>"
    else:
        header = "<tr><th>Канал</th><th>Волна</th><th>Статус</th><th>Владелец</th><th>Flow</th><th>Заметка</th></tr>"
    return (
        "<div class=\"source-table-wrap\"><table class=\"source-table\">"
        f"<thead>{header}</thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table></div>"
    )


def _source_summary_cards(source_map: dict[str, Any]) -> str:
    summary = source_map.get("summary", {})
    if not isinstance(summary, dict):
        summary = {}
    labels = {
        "canonical_mvp_channels": "MVP-каналы",
        "wave_1_channels": "1-я волна",
        "wave_2_channels": "2-я волна",
        "wave_3_channels": "3-я волна",
        "active_channels": "активные",
        "manual_channels": "ручные",
        "planned_channels": "planned",
        "competitor_watchlist_sources": "watchlist конкурентов",
        "lecture_growth_sources": "источники из лекции 15.05",
        "yanika_pending_sources": "каналы Яники ждут",
        "content_surfaces": "контентные поверхности",
        "backlog_sources": "backlog-источники",
    }
    cards = []
    for key, label in labels.items():
        cards.append(
            "<article class=\"source-stat-card\">"
            f"<span>{_e(label)}</span>"
            f"<strong>{_e(summary.get(key, 0))}</strong>"
            "</article>"
        )
    return "\n".join(cards)


def _source_map_section(source_map: dict[str, Any]) -> str:
    if not source_map:
        return ""
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

    return (
        "<section class=\"source-map\" aria-label=\"Карта источников и OKR источников\">"
        "<div class=\"section-heading\">"
        "<h2>Карта источников</h2>"
        f"<span class=\"status-pill {_status_class(source_map.get('source_map_status', 'NO_DATA'))}\">"
        f"{_e(source_map.get('source_map_status', 'NO_DATA'))}</span>"
        "</div>"
        "<p class=\"lead-text\">Здесь собраны 17 MVP-каналов, источники первой волны, planned-каналы из дашборда лектора, watchlist конкурентов и backlog-источники.</p>"
        f"<div class=\"source-stat-grid\">{_source_summary_cards(source_map)}</div>"
        "<div class=\"source-two-col\">"
        "<article class=\"source-panel\"><h3>Кто владеет каналами</h3>"
        f"<div class=\"kv-grid small\">{_kv_grid(counts_by_owner)}</div></article>"
        "<article class=\"source-panel\"><h3>Контентные поверхности Agent 4</h3>"
        f"<div class=\"tags\">{_tag_list(content_surfaces, 'tag tag--source')}</div></article>"
        "</div>"
        "<details class=\"source-details\" open><summary>Все 17 MVP-каналов</summary>"
        f"{_source_table(canonical)}"
        "</details>"
        "<div class=\"source-two-col\">"
        "<details class=\"source-details\" open><summary>Первая волна: 9 каналов</summary>"
        f"{_source_table(first_wave)}"
        "</details>"
        "<details class=\"source-details\" open><summary>Planned-каналы: 8 каналов</summary>"
        f"{_source_table(planned)}"
        "</details>"
        "</div>"
        "<details class=\"source-details\"><summary>Watchlist конкурентов Agent 1</summary>"
        f"{_source_table(competitor, mode='watch')}"
        "</details>"
        "<details class=\"source-details\" open><summary>Growth source map из лекции 15.05</summary>"
        "<p class=\"lead-text\">"
        f"Скоринг: {_e(source_map.get('lecture_growth_score_status', 'нет данных'))}. "
        f"Требуют approval или уточнения: {_e(lecture_growth_score_summary.get('approval_required_count', 'нет данных'))}."
        "</p>"
        f"{_source_table(lecture_growth, mode='watch')}"
        "</details>"
        "<details class=\"source-details\"><summary>Каналы Яники: 5 строк ждут ссылок</summary>"
        f"{_source_table(yanika, mode='watch')}"
        "</details>"
        "<article class=\"source-panel\"><h3>Backlog-источники</h3>"
        f"<div class=\"tags\">{_tag_list(backlog, 'tag tag--source')}</div></article>"
        "</section>"
    )


def _mini_rows(items: list[Any], id_key: str, value_key: str = "count", name_key: str = "name", limit: int = 8) -> str:
    rows = []
    for item in items[:limit]:
        if not isinstance(item, dict):
            continue
        label = item.get(id_key, item.get("id", ""))
        name = item.get(name_key, "")
        value = item.get(value_key, "")
        rows.append(
            "<tr>"
            f"<td>{_e(label)}</td>"
            f"<td>{_e(name)}</td>"
            f"<td>{_e(value)}</td>"
            "</tr>"
        )
    if not rows:
        return "<p class=\"muted\">нет данных</p>"
    return (
        "<div class=\"source-table-wrap\"><table class=\"source-table\">"
        "<thead><tr><th>ID</th><th>Название</th><th>Кол-во</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table></div>"
    )


def _bitrix_crm_hygiene_section(hygiene: dict[str, Any]) -> str:
    if not hygiene:
        return ""
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

    return (
        "<section class=\"source-map\" aria-label=\"Bitrix CRM hygiene\">"
        "<div class=\"section-heading\">"
        "<h2>Bitrix CRM hygiene</h2>"
        f"<span class=\"status-pill {_status_class(hygiene.get('status', 'NO_DATA'))}\">{_e(hygiene.get('status', 'NO_DATA'))}</span>"
        "</div>"
        "<p class=\"lead-text\">Read-only слой Agent 5: показывает качество CRM-базы, дубли и первую очередь ручной чистки. Dashboard не вызывает Bitrix24.</p>"
        "<div class=\"source-stat-grid\">"
        f"<article class=\"source-stat-card\"><span>Контакты</span><strong>{_e(counts.get('contacts', 0))}</strong></article>"
        f"<article class=\"source-stat-card\"><span>Лиды</span><strong>{_e(counts.get('leads_total', 0))}</strong></article>"
        f"<article class=\"source-stat-card\"><span>Активные лиды</span><strong>{_e(counts.get('leads_active', 0))}</strong></article>"
        f"<article class=\"source-stat-card\"><span>Сделки</span><strong>{_e(counts.get('deals_total', 0))}</strong></article>"
        f"<article class=\"source-stat-card\"><span>Контакты без связи</span><strong>{_e(quality.get('contacts_without_phone_or_email', 0))}</strong></article>"
        f"<article class=\"source-stat-card\"><span>Лиды без связи</span><strong>{_e(quality.get('leads_without_phone_or_email', 0))}</strong></article>"
        f"<article class=\"source-stat-card\"><span>Дубли контактов телефон/email</span><strong>{_e(duplicates.get('strong_groups_to_review_first', 0))}</strong></article>"
        f"<article class=\"source-stat-card\"><span>Дубли лидов телефон/email</span><strong>{_e(duplicates.get('leads_by_phone', 0) + duplicates.get('leads_by_email', 0))}</strong></article>"
        "</div>"
        "<div class=\"source-two-col\">"
        "<article class=\"source-panel\"><h3>Первая очередь чистки</h3>"
        f"<div class=\"tags\">{_tag_list(queue, 'tag tag--source')}</div></article>"
        "<article class=\"source-panel\"><h3>Файл отчёта</h3>"
        f"<div class=\"kv-grid small\">{_kv_grid({'report_file': hygiene.get('report_file', 'нет данных'), 'generated_at': hygiene.get('generated_at', 'нет данных'), 'limited_by_pages': hygiene.get('limited_by_pages', 'нет данных')})}</div></article>"
        "</div>"
        "<div class=\"source-two-col\">"
        "<details class=\"source-details\" open><summary>Источники лидов</summary>"
        f"{_mini_rows(lead_sources, 'source_id')}"
        "</details>"
        "<details class=\"source-details\" open><summary>Стадии сделок</summary>"
        f"{_mini_rows(deal_stages, 'stage_id', name_key='name')}"
        "</details>"
        "</div>"
        "</section>"
    )


def _vpp_ai_manager_dry_run_section(dry_run: dict[str, Any]) -> str:
    if not dry_run:
        return ""
    summary = dry_run.get("summary", {})
    scenarios = dry_run.get("scenarios", [])
    external_calls = dry_run.get("external_calls", {})
    if not isinstance(summary, dict):
        summary = {}
    if not isinstance(scenarios, list):
        scenarios = []
    if not isinstance(external_calls, dict):
        external_calls = {}

    scenario_cards: list[str] = []
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            continue
        missing = scenario.get("missing_data", [])
        if not isinstance(missing, list):
            missing = []
        missing_text = ", ".join(_safe_text(item) for item in missing) if missing else "нет"
        scenario_cards.append(
            "<article class=\"network-route\">"
            "<div class=\"network-route__head\">"
            f"<h3>{_e(scenario.get('title', 'нет данных'))}</h3>"
            f"<span class=\"status-pill {_status_class(scenario.get('bitrix_send_status', 'DRY_RUN_NOT_SENT'))}\">{_e(scenario.get('bitrix_send_status', 'DRY_RUN_NOT_SENT'))}</span>"
            "</div>"
            "<div class=\"network-meta\">"
            f"<div><span>Сегмент</span><strong>{_e(scenario.get('segment', 'нет данных'))}</strong></div>"
            f"<div><span>Flow / score</span><strong>{_e(scenario.get('flow', 'нет данных'))} / {_e(scenario.get('score', 'нет данных'))}</strong></div>"
            f"<div><span>Данные</span><strong>{_e(scenario.get('data_completeness', 'нет данных'))}</strong></div>"
            f"<div><span>КП за 24 часа</span><strong>{_e(_safe_text(scenario.get('kp_24h_allowed', False)))}</strong></div>"
            f"<div><span>Следующий шаг</span><strong>{_e(scenario.get('next_action', 'нет данных'))}</strong></div>"
            f"<div><span>Источник</span><strong>{_e(scenario.get('first_touch_channel', 'нет данных'))}</strong></div>"
            f"<div><span>Лендинг</span><strong>{_e(scenario.get('landing_page', 'нет данных'))}</strong></div>"
            f"<div><span>Не хватает</span><strong>{_e(missing_text)}</strong></div>"
            "</div>"
            f"<p>{_e(scenario.get('first_reply', 'нет данных'))}</p>"
            "</article>"
        )
    scenario_cards_html = "".join(scenario_cards) if scenario_cards else "<p class=\"muted\">нет данных</p>"

    return (
        "<section class=\"source-map\" aria-label=\"VPP AI-manager dry-run\">"
        "<div class=\"section-heading\">"
        "<h2>VPP AI-manager dry-run</h2>"
        f"<span class=\"status-pill {_status_class(dry_run.get('status', 'NO_DATA'))}\">{_e(dry_run.get('status', 'NO_DATA'))}</span>"
        "</div>"
        "<p class=\"lead-text\">Тестовый AI-менеджер разбирает входящее сообщение, определяет сегмент, готовность данных, следующий шаг и preview сделки Bitrix24. Это локальный dry-run, отправок нет.</p>"
        "<div class=\"source-stat-grid\">"
        f"<article class=\"source-stat-card\"><span>Сценариев</span><strong>{_e(dry_run.get('scenario_count', 0))}</strong></article>"
        f"<article class=\"source-stat-card\"><span>Готово к КП</span><strong>{_e(summary.get('enough_for_kp', 0))}</strong></article>"
        f"<article class=\"source-stat-card\"><span>Нужно уточнить</span><strong>{_e(summary.get('need_missing_data', 0))}</strong></article>"
        f"<article class=\"source-stat-card\"><span>Bitrix dry-run</span><strong>{_e(summary.get('bitrix_dry_run_not_sent', 0))}</strong></article>"
        "</div>"
        f"<div class=\"network-routes\">{scenario_cards_html}</div>"
        "<div class=\"source-two-col\">"
        "<article class=\"source-panel\"><h3>Файлы</h3>"
        f"<div class=\"kv-grid small\">{_kv_grid({'report_file': dry_run.get('report_file', 'нет данных'), 'markdown_report': dry_run.get('markdown_report', 'нет данных'), 'created_at': dry_run.get('created_at', 'нет данных')})}</div></article>"
        "<article class=\"source-panel\"><h3>Внешние вызовы</h3>"
        f"<div class=\"kv-grid small\">{_kv_grid(external_calls)}</div></article>"
        "</div>"
        f"<p class=\"muted\">{_e(dry_run.get('safety_note', ''))}</p>"
        "</section>"
    )


def _first_safe_growth_tests_section(report: dict[str, Any]) -> str:
    if not report:
        return ""
    tests = report.get("tests", [])
    deferred = report.get("deferred_items", [])
    if not isinstance(tests, list):
        tests = []
    if not isinstance(deferred, list):
        deferred = []

    cards = []
    for test in tests:
        if not isinstance(test, dict):
            continue
        cards.append(
            "<article class=\"network-route\">"
            "<div class=\"network-route__head\">"
            f"<h3>{_e(test.get('source_name', 'нет данных'))}</h3>"
            f"<span class=\"status-pill is-wait\">{_e(test.get('mode', 'нет данных'))}</span>"
            "</div>"
            "<div class=\"network-meta\">"
            f"<div><span>Test</span><strong>{_e(test.get('test_id', 'нет данных'))}</strong></div>"
            f"<div><span>Сегмент</span><strong>{_e(test.get('segment', 'нет данных'))}</strong></div>"
            f"<div><span>Владелец</span><strong>{_e(test.get('owner_agent', 'нет данных'))}</strong></div>"
            f"<div><span>Approval</span><strong>{_e(_safe_text(test.get('approval_required', True)))}</strong></div>"
            "</div>"
            f"<p>{_e(test.get('proposed_action', 'нет данных'))}</p>"
            f"<p class=\"muted\">Stop rule: {_e(test.get('stop_rule', 'нет данных'))}</p>"
            "</article>"
        )
    cards_html = "".join(cards) if cards else "<p class=\"muted\">нет данных</p>"

    return (
        "<section class=\"source-map\" aria-label=\"First safe growth tests\">"
        "<div class=\"section-heading\">"
        "<h2>First Safe Growth Tests</h2>"
        f"<span class=\"status-pill {_status_class(report.get('status', 'NO_DATA'))}\">{_e(report.get('status', 'NO_DATA'))}</span>"
        "</div>"
        "<p class=\"lead-text\">Первые безопасные тесты после лекции: только read-only или draft-only, без отправок и рекламы.</p>"
        f"<div class=\"network-routes\">{cards_html}</div>"
        "<article class=\"source-panel\"><h3>Отложено</h3>"
        f"<div class=\"tags\">{_tag_list(deferred, 'tag tag--source')}</div></article>"
        "</section>"
    )


def _bitrix_reactivation_readonly_plan_section(report: dict[str, Any]) -> str:
    if not report:
        return ""
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

    cleanup_rows = "".join(
        "<tr>"
        f"<td>{_e(item.get('title', ''))}</td>"
        f"<td>{_e(item.get('count', ''))}</td>"
        f"<td>{_e(item.get('priority', ''))}</td>"
        f"<td>{_e(item.get('action', ''))}</td>"
        "</tr>"
        for item in cleanup_queue
        if isinstance(item, dict)
    )
    bucket_tags = [
        f"{item.get('title', '')}: {item.get('first_message_status', '')}"
        for item in buckets
        if isinstance(item, dict)
    ]
    return (
        "<section class=\"source-map\" aria-label=\"Bitrix reactivation readonly plan\">"
        "<div class=\"section-heading\">"
        "<h2>Bitrix Reactivation Readonly Plan</h2>"
        f"<span class=\"status-pill {_status_class(report.get('status', 'NO_DATA'))}\">{_e(report.get('status', 'NO_DATA'))}</span>"
        "</div>"
        "<p class=\"lead-text\">План чистки и возможной ручной реактивации из локального Bitrix-аудита. Карточки не менялись, сообщения не отправлялись.</p>"
        "<div class=\"source-stat-grid\">"
        f"<article class=\"source-stat-card\"><span>Контактов в аудите</span><strong>{_e(summary.get('contacts', 0))}</strong></article>"
        f"<article class=\"source-stat-card\"><span>Лидов в аудите</span><strong>{_e(summary.get('leads_total', 0))}</strong></article>"
        f"<article class=\"source-stat-card\"><span>Сделок в аудите</span><strong>{_e(summary.get('deals_total', 0))}</strong></article>"
        f"<article class=\"source-stat-card\"><span>Групп дублей</span><strong>{_e(summary.get('total_duplicate_groups', 0))}</strong></article>"
        "</div>"
        f"<p class=\"muted\">Audit limited_by_pages: {_e(report.get('limited_by_pages', 'нет данных'))}</p>"
        "<details class=\"source-details\" open><summary>Очередь чистки</summary>"
        "<div class=\"source-table-wrap\"><table class=\"source-table\">"
        "<thead><tr><th>Очередь</th><th>Count</th><th>Priority</th><th>Action</th></tr></thead>"
        f"<tbody>{cleanup_rows}</tbody></table></div></details>"
        "<article class=\"source-panel\"><h3>Группы реактивации</h3>"
        f"<div class=\"tags\">{_tag_list(bucket_tags, 'tag tag--source')}</div></article>"
        "<article class=\"source-panel\"><h3>Approval нужен перед</h3>"
        f"<div class=\"tags\">{_tag_list(approvals, 'tag tag--source')}</div></article>"
        "</section>"
    )


def _tender_filter_pack_dry_run_section(report: dict[str, Any]) -> str:
    if not report:
        return ""
    checks = report.get("checks", [])
    approvals = report.get("approval_required_before", [])
    if not isinstance(checks, list):
        checks = []
    if not isinstance(approvals, list):
        approvals = []
    rows = "".join(
        "<tr>"
        f"<td>{_e(item.get('filter_id', ''))}</td>"
        f"<td>{_e(item.get('segment', ''))}</td>"
        f"<td>{_e(item.get('priority', ''))}</td>"
        f"<td>{_e(item.get('status', ''))}</td>"
        f"<td>{_e(item.get('stop_rule', ''))}</td>"
        "</tr>"
        for item in checks
        if isinstance(item, dict)
    )
    return (
        "<section class=\"source-map\" aria-label=\"Tender filter pack dry run\">"
        "<div class=\"section-heading\">"
        "<h2>Tender Filter Pack</h2>"
        f"<span class=\"status-pill {_status_class(report.get('status', 'NO_DATA'))}\">{_e(report.get('status', 'NO_DATA'))}</span>"
        "</div>"
        "<p class=\"lead-text\">Read-only фильтры тендеров под проектирование. Площадки не открывались, заявки не подавались.</p>"
        "<div class=\"source-stat-grid\">"
        f"<article class=\"source-stat-card\"><span>Фильтров</span><strong>{_e(report.get('filter_count', 0))}</strong></article>"
        f"<article class=\"source-stat-card\"><span>Файл</span><strong>{_e(report.get('filter_file', 'нет данных'))}</strong></article>"
        "</div>"
        "<details class=\"source-details\" open><summary>Фильтры</summary>"
        "<div class=\"source-table-wrap\"><table class=\"source-table\">"
        "<thead><tr><th>ID</th><th>Segment</th><th>Priority</th><th>Status</th><th>Stop rule</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></div></details>"
        "<article class=\"source-panel\"><h3>Approval нужен перед</h3>"
        f"<div class=\"tags\">{_tag_list(approvals, 'tag tag--source')}</div></article>"
        "</section>"
    )


def _client_acquisition_pack_dry_run_section(report: dict[str, Any]) -> str:
    if not report:
        return ""
    summary = report.get("summary", {})
    routes = report.get("routes", [])
    assets = report.get("supporting_assets", [])
    if not isinstance(summary, dict):
        summary = {}
    if not isinstance(routes, list):
        routes = []
    if not isinstance(assets, list):
        assets = []
    rows = "".join(
        "<tr>"
        f"<td>{_e(item.get('route_id', ''))}</td>"
        f"<td>{_e(item.get('segment', ''))}</td>"
        f"<td>{_e(item.get('priority', ''))}</td>"
        f"<td>{_e(item.get('primary_source', ''))}</td>"
        f"<td>{_e(item.get('offer', ''))}</td>"
        f"<td>{_e(item.get('approval_gate', ''))}</td>"
        "</tr>"
        for item in routes
        if isinstance(item, dict)
    )
    return (
        "<section class=\"source-map\" aria-label=\"Client acquisition pack\">"
        "<div class=\"section-heading\">"
        "<h2>Client Acquisition Pack</h2>"
        f"<span class=\"status-pill {_status_class(report.get('status', 'NO_DATA'))}\">{_e(report.get('status', 'NO_DATA'))}</span>"
        "</div>"
        "<p class=\"lead-text\">Применение техники лектора к ВПП: сегмент, источник, оффер, материал, UTM, Bitrix-метки и approval gate.</p>"
        "<div class=\"source-stat-grid\">"
        f"<article class=\"source-stat-card\"><span>Маршрутов</span><strong>{_e(report.get('route_count', 0))}</strong></article>"
        f"<article class=\"source-stat-card\"><span>Approval required</span><strong>{_e(summary.get('approval_required_routes', 0))}</strong></article>"
        "</div>"
        "<details class=\"source-details\" open><summary>Маршруты привлечения</summary>"
        "<div class=\"source-table-wrap\"><table class=\"source-table\">"
        "<thead><tr><th>Route</th><th>Segment</th><th>Priority</th><th>Source</th><th>Offer</th><th>Approval</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></div></details>"
        "<article class=\"source-panel\"><h3>Supporting assets</h3>"
        f"<div class=\"tags\">{_tag_list(assets, 'tag tag--source')}</div></article>"
        "</section>"
    )


def _three_qualified_leads_sprint_section(report: dict[str, Any]) -> str:
    if not report:
        return ""
    mapping = report.get("astrology_method_mapping", {})
    items = report.get("items", [])
    if not isinstance(mapping, dict):
        mapping = {}
    if not isinstance(items, list):
        items = []
    rows = "".join(
        "<tr>"
        f"<td>{_e(item.get('sprint_item_id', ''))}</td>"
        f"<td>{_e(item.get('week', ''))}</td>"
        f"<td>{_e(item.get('segment', ''))}</td>"
        f"<td>{_e(item.get('agent_owner', ''))}</td>"
        f"<td>{_e(item.get('source', ''))}</td>"
        f"<td>{_e(item.get('goal_metric', ''))}</td>"
        f"<td>{_e(item.get('status', ''))}</td>"
        "</tr>"
        for item in items
        if isinstance(item, dict)
    )
    mapping_tags = [f"{key}: {value}" for key, value in mapping.items()]
    return (
        "<section class=\"source-map\" aria-label=\"Three qualified leads sprint\">"
        "<div class=\"section-heading\">"
        "<h2>Three Qualified Leads Sprint</h2>"
        f"<span class=\"status-pill {_status_class(report.get('status', 'NO_DATA'))}\">{_e(report.get('status', 'NO_DATA'))}</span>"
        "</div>"
        "<p class=\"lead-text\">Спринт на первые 3 качественные заявки: перенос механики AI-астрологии в экспертный B2B-вход ВПП.</p>"
        "<div class=\"source-stat-grid\">"
        f"<article class=\"source-stat-card\"><span>Target leads</span><strong>{_e(report.get('qualified_lead_target_count', 0))}</strong></article>"
        f"<article class=\"source-stat-card\"><span>Sprint items</span><strong>{_e(report.get('sprint_items_count', 0))}</strong></article>"
        f"<article class=\"source-stat-card\"><span>Ready/draft</span><strong>{_e(report.get('ready_or_draft_items', 0))}</strong></article>"
        f"<article class=\"source-stat-card\"><span>Approval required</span><strong>{_e(report.get('approval_required_items', 0))}</strong></article>"
        "</div>"
        "<article class=\"source-panel\"><h3>Перенос астрометодики</h3>"
        f"<div class=\"tags\">{_tag_list(mapping_tags, 'tag tag--source')}</div></article>"
        "<details class=\"source-details\" open><summary>Sprint items</summary>"
        "<div class=\"source-table-wrap\"><table class=\"source-table\">"
        "<thead><tr><th>ID</th><th>Week</th><th>Segment</th><th>Agent</th><th>Source</th><th>Metric</th><th>Status</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></div></details>"
        "</section>"
    )


def _agent_sources(agent: dict[str, Any]) -> str:
    scope = agent.get("source_scope", {})
    if not isinstance(scope, dict):
        return "<p class=\"muted\">нет данных</p>"
    primary = scope.get("primary_sources", [])
    watchlist = scope.get("watchlist_sources", [])
    yanika_pending = scope.get("yanika_pending_sources", [])
    backlog = scope.get("backlog_sources", [])
    content_surfaces = scope.get("content_surfaces", [])
    direct_owner = scope.get("direct_owner_sources", [])
    if not isinstance(primary, list):
        primary = []
    if not isinstance(watchlist, list):
        watchlist = []
    if not isinstance(yanika_pending, list):
        yanika_pending = []
    if not isinstance(backlog, list):
        backlog = []
    if not isinstance(content_surfaces, list):
        content_surfaces = []
    if not isinstance(direct_owner, list):
        direct_owner = []
    return (
        "<div class=\"agent-source-panel\">"
        "<h3>Источники по агенту</h3>"
        f"<p>{_e(scope.get('summary', 'нет данных'))}</p>"
        "<div class=\"source-mini-grid\">"
        f"<span><strong>{_e(scope.get('source_count', len(primary)))}</strong> основных</span>"
        f"<span><strong>{_e(scope.get('watchlist_count', len(watchlist)))}</strong> watchlist</span>"
        f"<span><strong>{_e(scope.get('yanika_pending_count', len(yanika_pending)))}</strong> ждут Янику</span>"
        f"<span><strong>{_e(scope.get('content_surface_count', len(content_surfaces)))}</strong> поверхностей</span>"
        "</div>"
        "<h4>Основные источники</h4>"
        f"<div class=\"tags\">{_source_tags(primary)}</div>"
        + (
            "<h4>Прямые источники-владельцы</h4>"
            f"<div class=\"tags\">{_source_tags(direct_owner)}</div>"
            if direct_owner else ""
        )
        + (
            "<h4>Контентные поверхности</h4>"
            f"<div class=\"tags\">{_tag_list(content_surfaces, 'tag tag--source')}</div>"
            if content_surfaces else ""
        )
        + (
            "<h4>Watchlist / конкуренты</h4>"
            f"<div class=\"tags\">{_source_tags(watchlist)}</div>"
            if watchlist else ""
        )
        + (
            "<h4>Каналы Яники ждут заполнения</h4>"
            f"<div class=\"tags\">{_source_tags(yanika_pending)}</div>"
            if yanika_pending else ""
        )
        + (
            "<h4>Backlog-источники</h4>"
            f"<div class=\"tags\">{_tag_list(backlog, 'tag tag--source')}</div>"
            if backlog else ""
        )
        + "</div>"
    )


def _agent_cards(agents: list[dict[str, Any]]) -> str:
    cards = []
    for index, agent in enumerate(agents):
        active = " is-active" if index == 0 else ""
        status = agent.get("panel_status", "NO_DATA")
        readiness = agent.get("readiness_percent", "нет данных")
        okr_readiness = agent.get("okr_readiness_percent", readiness)
        cards.append(
            "<button class=\"agent-card"
            f"{active}\" type=\"button\" data-agent=\"{_e(agent.get('agent_id', ''))}\">"
            "<span class=\"agent-card__top\">"
            f"<strong>{_e(agent.get('title', 'нет данных'))}</strong>"
            f"<em class=\"status-pill {_status_class(status)}\">KR {_e(okr_readiness)}%</em>"
            "</span>"
            f"<span>{_e(agent.get('department', 'нет данных'))}</span>"
            f"<small>{_e(agent.get('description', 'нет данных'))}</small>"
            "</button>"
        )
    return "\n".join(cards)


def _subrole_list(subroles: list[Any]) -> str:
    rows = []
    for subrole in subroles:
        if not isinstance(subrole, dict):
            continue
        rows.append(
            "<article class=\"subrole-card\">"
            f"<strong>{_e(subrole.get('name', 'нет данных'))}</strong>"
            f"<span>{_e(subrole.get('responsibility', 'нет данных'))}</span>"
            f"<small>Артефакт: {_e(subrole.get('artifact', 'нет данных'))}</small>"
            f"<small>KPI: {_e(subrole.get('kpi', 'нет данных'))}</small>"
            "</article>"
        )
    return "\n".join(rows) if rows else "<p class=\"muted\">нет данных</p>"


def _agent_details(agents: list[dict[str, Any]]) -> str:
    blocks = []
    for index, agent in enumerate(agents):
        active = " is-active" if index == 0 else ""
        checker_status = agent.get("checker_status")
        if not isinstance(checker_status, dict):
            checker_status = {}
        blocks.append(
            "<article class=\"agent-detail"
            f"{active}\" data-agent-detail=\"{_e(agent.get('agent_id', ''))}\">"
            "<div class=\"section-heading\">"
            f"<h2>{_e(agent.get('title', 'нет данных'))}</h2>"
            f"<span class=\"status-pill {_status_class(agent.get('panel_status'))}\">KR готово на {_e(agent.get('okr_readiness_percent', agent.get('readiness_percent', 'нет данных')))}%</span>"
            "</div>"
            f"<p class=\"lead-text\">{_e(agent.get('description', 'нет данных'))}</p>"
            f"<p class=\"lead-text\">{_e(agent.get('okr', 'нет данных'))}</p>"
            f"{_main_metric(agent.get('main_metric', {}))}"
            f"{_agent_sources(agent)}"
            "<div class=\"detail-grid\">"
            "<div><h3>OKR/KR метрики</h3><div class=\"okr-metric-list\">"
            f"{_okr_metric_list(agent.get('okr_metrics', []))}"
            "</div></div>"
            "<div><h3>Защитные метрики</h3><div class=\"tags\">"
            f"{_tag_list(agent.get('guard_metrics', []), 'tag tag--guard')}"
            "</div></div>"
            "</div>"
            "<div class=\"detail-grid\">"
            "<div><h3>Суброли</h3><div class=\"subrole-grid\">"
            f"{_subrole_list(agent.get('subroles', []))}"
            "</div></div>"
            "<div><h3>Скиллы</h3><div class=\"tags\">"
            f"{_tag_list(agent.get('skills', []))}"
            "</div></div>"
            "</div>"
            "<div class=\"detail-grid\">"
            "<div><h3>Готовность</h3>"
            f"<div class=\"readiness-card\"><strong>{_e(agent.get('readiness_percent', 'нет данных'))}%</strong>"
            f"<span>{_e(agent.get('panel_status', 'NO_DATA'))}</span></div>"
            "</div>"
            "</div>"
            "<div class=\"next-action\">"
            "<span>Что доделать</span>"
            f"<strong>{_e(agent.get('todo', agent.get('next_action', 'нет данных')))}</strong>"
            "</div>"
            "</article>"
        )
    return "\n".join(blocks)


def _events(events: list[dict[str, Any]], limit: int = 6) -> str:
    rows = []
    for event in events[:limit]:
        status = event.get("status", "NO_DATA")
        rows.append(
            "<article class=\"event-row\">"
            "<div>"
            f"<strong>{_e(event.get('summary', 'нет данных'))}</strong>"
            f"<span>{_e(event.get('created_at', 'нет данных'))}</span>"
            "</div>"
            f"<em class=\"status-pill {_status_class(status)}\">{_e(status)}</em>"
            f"<code>{_e(event.get('report_file', 'нет данных'))}</code>"
            "</article>"
        )
    return "\n".join(rows) if rows else "<p class=\"muted\">нет событий</p>"


def _metrics(metrics: dict[str, Any]) -> str:
    cards = []
    for group_name, values in metrics.items():
        if not isinstance(values, dict):
            continue
        cards.append(
            "<article class=\"metric-card\">"
            f"<h3>{_e(group_name)}</h3>"
            f"<div class=\"kv-grid small\">{_kv_grid(values)}</div>"
            "</article>"
        )
    return "\n".join(cards)


def _locks(locks: dict[str, Any]) -> str:
    labels = {
        "scheduler_locked": "scheduler",
        "mass_collection_locked": "массовый сбор",
        "real_publish_locked": "реальные публикации",
        "real_outreach_locked": "реальный outreach",
        "secrets_visible": "секреты",
    }
    chips = []
    for key, value in locks.items():
        display_key = labels.get(key, key)
        if key == "secrets_visible":
            label = "видны" if value is True else "скрыты"
            class_name = "is-locked" if value is True else "is-open"
        else:
            label = "закрыто" if value is True else "открыто" if value is False else _safe_text(value)
            class_name = "is-locked" if value is True else "is-open"
        chips.append(
            f"<span class=\"lock-chip {class_name}\">"
            f"{_e(display_key)}: {_e(label)}"
            "</span>"
        )
    return "\n".join(chips)


def _external_flags(flags: dict[str, Any]) -> str:
    return "\n".join(
        f"<span class=\"flag {'is-on' if value else 'is-off'}\">{_e(key)}: {_e(_safe_text(value))}</span>"
        for key, value in flags.items()
    )


def _department_cards(departments: list[dict[str, Any]]) -> str:
    if not departments:
        return "<p class=\"muted\">нет данных</p>"
    cards = []
    for item in departments:
        status = item.get("status", "NO_DATA")
        cards.append(
            "<article class=\"department-card\">"
            "<div class=\"department-card__top\">"
            f"<strong>{_e(item.get('title', 'нет данных'))}</strong>"
            f"<span class=\"status-pill {_status_class(status)}\">{_e(status)}</span>"
            "</div>"
            f"<span>{_e(item.get('owner', 'нет данных'))}</span>"
            f"<p>{_e(item.get('purpose', 'нет данных'))}</p>"
            "</article>"
        )
    return "\n".join(cards)


def _flow_steps(steps: list[dict[str, Any]]) -> str:
    if not steps:
        return "<p class=\"muted\">нет данных</p>"
    items = []
    for step in steps:
        items.append(
            "<article class=\"flow-step\">"
            f"<span>{_e(step.get('step', ''))}</span>"
            f"<strong>{_e(step.get('title', 'нет данных'))}</strong>"
            f"<em>{_e(step.get('owner', 'нет данных'))}</em>"
            f"<p>{_e(step.get('result', 'нет данных'))}</p>"
            "</article>"
        )
    return "\n".join(items)


def _handoff_cards(handoffs: list[dict[str, Any]]) -> str:
    if not handoffs:
        return "<p class=\"muted\">нет данных</p>"
    rows = []
    for handoff in handoffs:
        rows.append(
            "<article class=\"handoff-card\">"
            "<div class=\"handoff-route\">"
            f"<strong>{_e(handoff.get('from', 'нет данных'))}</strong>"
            "<span>-></span>"
            f"<strong>{_e(handoff.get('to', 'нет данных'))}</strong>"
            "</div>"
            "<div class=\"handoff-grid\">"
            "<div><span>Что передается</span>"
            f"<strong>{_e(handoff.get('payload', 'нет данных'))}</strong></div>"
            "<div><span>Формат</span>"
            f"<strong>{_e(handoff.get('format', 'нет данных'))}</strong></div>"
            "<div><span>Где лежит</span>"
            f"<strong>{_e(handoff.get('storage', 'нет данных'))}</strong></div>"
            "<div><span>Кто проверяет</span>"
            f"<strong>{_e(handoff.get('checked_by', 'нет данных'))}</strong></div>"
            "</div>"
            "</article>"
        )
    return "\n".join(rows)


def _control_blocks(blocks: list[dict[str, Any]]) -> str:
    if not blocks:
        return "<p class=\"muted\">нет данных</p>"
    items = []
    for block in blocks:
        items.append(
            "<article class=\"control-card\">"
            f"<strong>{_e(block.get('title', 'нет данных'))}</strong>"
            f"<code>{_e(block.get('command', 'нет данных'))}</code>"
            f"<span>{_e(block.get('mode', 'нет данных'))} / external_calls={_e(block.get('external_calls', 'False'))}</span>"
            "</article>"
        )
    return "\n".join(items)


def _interaction_routes(routes: list[dict[str, Any]]) -> str:
    if not routes:
        return "<p class=\"muted\">нет данных</p>"
    items = []
    for route in routes:
        status = route.get("status", "NO_DATA")
        nodes = route.get("nodes", [])
        if not isinstance(nodes, list):
            nodes = []
        node_html = []
        for index, node in enumerate(nodes):
            node_html.append(f"<span class=\"network-node\">{_e(node)}</span>")
            if index < len(nodes) - 1:
                node_html.append("<span class=\"network-arrow\">-></span>")
        items.append(
            "<article class=\"network-route\">"
            "<div class=\"network-route__head\">"
            f"<h3>{_e(route.get('title', 'нет данных'))}</h3>"
            f"<span class=\"status-pill {_status_class(status)}\">{_e(status)}</span>"
            "</div>"
            f"<div class=\"network-chain\">{''.join(node_html)}</div>"
            "<div class=\"network-meta\">"
            "<div><span>Что проходит по потоку</span>"
            f"<strong>{_e(route.get('payload', 'нет данных'))}</strong></div>"
            "<div><span>Ограничение</span>"
            f"<strong>{_e(route.get('safe_note', 'нет данных'))}</strong></div>"
            "</div>"
            "</article>"
        )
    return "\n".join(items)


def _management_protocol(protocol: dict[str, Any]) -> str:
    if not protocol:
        return "<p class=\"muted\">нет данных</p>"

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

    chain_items: list[str] = []
    for index, step in enumerate(nervous_system):
        chain_items.append(f"<span class=\"network-node\">{_e(step)}</span>")
        if index < len(nervous_system) - 1:
            chain_items.append("<span class=\"network-arrow\">-></span>")
    chain_html = "".join(chain_items) if chain_items else "<span class=\"muted\">нет данных</span>"

    template_cards: list[str] = []
    for template in templates:
        if not isinstance(template, dict):
            continue
        fields = template.get("fields", [])
        if not isinstance(fields, list):
            fields = []
        template_cards.append(
            "<article class=\"protocol-card\">"
            f"<strong>{_e(template.get('name', 'нет данных'))}</strong>"
            f"<p>{_e(template.get('purpose', 'нет данных'))}</p>"
            f"<div class=\"tags\">{_tag_list(fields)}</div>"
            "</article>"
        )

    return (
        "<div class=\"protocol-grid\">"
        "<article class=\"protocol-card protocol-card--wide\">"
        "<h3>Chief of Staff</h3>"
        f"<p><strong>{_e(chief.get('owner', 'CLAUDE.md / AGENTS.md / REPORT.md'))}</strong></p>"
        f"<p>{_e(chief.get('meaning', 'режим координации, не новый агент'))}</p>"
        f"<p>{_e(chief.get('responsibility', 'принять задачу, выбрать маршрут, проверить результат'))}</p>"
        f"<code>{_e(protocol.get('rule', 'агент = роль; skill = действие'))}</code>"
        "</article>"
        "<article class=\"protocol-card protocol-card--wide\">"
        "<h3>Нервная система</h3>"
        f"<div class=\"network-chain\">{chain_html}</div>"
        "</article>"
        f"{''.join(template_cards)}"
        "<article class=\"protocol-card protocol-card--wide\">"
        "<h3>Когда эскалировать Янике</h3>"
        "<ul class=\"compact-list\">"
        + "".join(f"<li>{_e(rule)}</li>" for rule in escalation_rules)
        + "</ul>"
        f"<p><strong>Weekly digest:</strong> {_e(protocol.get('weekly_digest_owner', 'Agent 5/dashboard позже'))}</p>"
        "</article>"
        "</div>"
    )


def _mas_reference_layer(layer: dict[str, Any]) -> str:
    if not layer:
        return "<p class=\"muted\">нет данных</p>"

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

    block_cards: list[str] = []
    for block in adopted_blocks:
        if not isinstance(block, dict):
            continue
        block_cards.append(
            "<article class=\"protocol-card\">"
            f"<strong>{_e(block.get('name', 'нет данных'))}</strong>"
            f"<p>{_e(block.get('meaning', 'нет данных'))}</p>"
            f"<p><span class=\"muted\">Где:</span> {_e(block.get('where', 'нет данных'))}</p>"
            f"<span class=\"status-pill {_status_class(block.get('mvp_status', 'planned'))}\">{_e(block.get('mvp_status', 'planned'))}</span>"
            "</article>"
        )

    scenario_cards: list[str] = []
    for scenario in scenario_timelines:
        if not isinstance(scenario, dict):
            continue
        steps = scenario.get("steps", [])
        if not isinstance(steps, list):
            steps = []
        chain_items: list[str] = []
        for index, step in enumerate(steps):
            chain_items.append(f"<span class=\"network-node\">{_e(step)}</span>")
            if index < len(steps) - 1:
                chain_items.append("<span class=\"network-arrow\">-></span>")
        scenario_cards.append(
            "<article class=\"network-route\">"
            "<div class=\"network-route__head\">"
            f"<h3>{_e(scenario.get('name', 'нет данных'))}</h3>"
            "<span class=\"status-pill is-wait\">planned</span>"
            "</div>"
            f"<div class=\"network-chain\">{''.join(chain_items)}</div>"
            "<div class=\"network-meta\">"
            "<div><span>Артефакт</span>"
            f"<strong>{_e(scenario.get('artifact', 'нет данных'))}</strong></div>"
            "</div>"
            "</article>"
        )

    artifact_cards: list[str] = []
    for item in required_artifacts:
        if not isinstance(item, dict):
            continue
        artifact_cards.append(
            "<article class=\"protocol-card\">"
            f"<strong>{_e(item.get('stage', 'нет данных'))}</strong>"
            f"<p>{_e(item.get('artifact', 'нет данных'))}</p>"
            "</article>"
        )

    return (
        "<div class=\"protocol-grid\">"
        "<article class=\"protocol-card protocol-card--wide\">"
        "<h3>О чём модель</h3>"
        f"<p>{_e(layer.get('model_summary', 'нет данных'))}</p>"
        f"<p><strong>Правило:</strong> {_e(layer.get('application_rule', 'нет данных'))}</p>"
        f"<p><strong>Источник:</strong> {_e(layer.get('source_doc', 'нет данных'))}</p>"
        "</article>"
        f"{''.join(block_cards)}"
        "<article class=\"protocol-card protocol-card--wide\">"
        "<h3>Status model</h3>"
        f"<div class=\"tags\">{_tag_list(statuses)}</div>"
        "</article>"
        "<article class=\"protocol-card protocol-card--wide\">"
        "<h3>OSINT без Agent 7</h3>"
        "<ul class=\"compact-list\">"
        + "".join(f"<li>{_e(rule)}</li>" for rule in osint_rules)
        + "</ul>"
        "</article>"
        "<article class=\"protocol-card protocol-card--wide\">"
        "<h3>Later-locks</h3>"
        "<ul class=\"compact-list\">"
        + "".join(f"<li>{_e(rule)}</li>" for rule in later_locks)
        + "</ul>"
        "</article>"
        "</div>"
        "<div class=\"section-heading section-heading--sub\"><h3>Scenario Timeline</h3></div>"
        f"<div class=\"network-routes\">{''.join(scenario_cards)}</div>"
        "<div class=\"section-heading section-heading--sub\"><h3>Artifact Tracker</h3></div>"
        f"<div class=\"protocol-grid\">{''.join(artifact_cards)}</div>"
    )


def _security_agent_control_layer(layer: dict[str, Any]) -> str:
    if not layer:
        return "<p class=\"muted\">нет данных</p>"

    red_lines = layer.get("red_lines", [])
    green_corridor = layer.get("green_corridor", [])
    risks = layer.get("ai_specific_risks", [])
    applied_to = layer.get("applied_to", [])
    touchpoints = layer.get("agent_touchpoints", [])
    if not isinstance(red_lines, list):
        red_lines = []
    if not isinstance(green_corridor, list):
        green_corridor = []
    if not isinstance(risks, list):
        risks = []
    if not isinstance(applied_to, list):
        applied_to = []
    if not isinstance(touchpoints, list):
        touchpoints = []

    touchpoint_cards: list[str] = []
    for item in touchpoints:
        if not isinstance(item, dict):
            continue
        touchpoint_cards.append(
            "<article class=\"protocol-card\">"
            f"<strong>{_e(item.get('agent', 'нет данных'))}</strong>"
            f"<p>{_e(item.get('control', 'нет данных'))}</p>"
            "</article>"
        )

    return (
        "<div class=\"protocol-grid\">"
        "<article class=\"protocol-card protocol-card--wide\">"
        "<h3>AGENT_SECURITY.md</h3>"
        f"<p>{_e(layer.get('purpose', 'контроль безопасности для всех агентов'))}</p>"
        f"<p><strong>Источник:</strong> {_e(layer.get('source_file', 'agents/Агент безопастности/AGENT_SECURITY.md'))}</p>"
        f"<p><strong>Документ:</strong> {_e(layer.get('control_doc', 'docs/security-agent-control-layer.md'))}</p>"
        f"<p><strong>не Agent 7:</strong> {_e(layer.get('not_agent_7', True))}</p>"
        "</article>"
        "<article class=\"protocol-card protocol-card--wide\">"
        "<h3>Красные линии</h3>"
        "<ul class=\"compact-list\">"
        + "".join(f"<li>{_e(item)}</li>" for item in red_lines)
        + "</ul>"
        "</article>"
        "<article class=\"protocol-card protocol-card--wide\">"
        "<h3>Зелёный коридор</h3>"
        "<ul class=\"compact-list\">"
        + "".join(f"<li>{_e(item)}</li>" for item in green_corridor)
        + "</ul>"
        "</article>"
        "<article class=\"protocol-card protocol-card--wide\">"
        "<h3>AI-риски</h3>"
        f"<div class=\"tags\">{_tag_list(risks)}</div>"
        "</article>"
        "<article class=\"protocol-card protocol-card--wide\">"
        "<h3>Куда подключён</h3>"
        f"<div class=\"tags\">{_tag_list(applied_to)}</div>"
        "</article>"
        f"{''.join(touchpoint_cards)}"
        "</div>"
    )


def _scenario_artifact_contract(contract: dict[str, Any]) -> str:
    if not contract:
        return "<p class=\"muted\">нет данных</p>"

    scenarios = contract.get("scenarios", [])
    statuses = contract.get("statuses", [])
    forbidden_actions = contract.get("forbidden_actions", [])
    if not isinstance(scenarios, list):
        scenarios = []
    if not isinstance(statuses, list):
        statuses = []
    if not isinstance(forbidden_actions, list):
        forbidden_actions = []

    scenario_cards: list[str] = []
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            continue
        timeline = scenario.get("timeline", [])
        artifacts = scenario.get("required_artifacts", [])
        if not isinstance(timeline, list):
            timeline = []
        if not isinstance(artifacts, list):
            artifacts = []
        chain_items: list[str] = []
        for index, step in enumerate(timeline):
            chain_items.append(f"<span class=\"network-node\">{_e(step)}</span>")
            if index < len(timeline) - 1:
                chain_items.append("<span class=\"network-arrow\">-></span>")
        scenario_cards.append(
            "<article class=\"network-route\">"
            "<div class=\"network-route__head\">"
            f"<h3>{_e(scenario.get('name', 'нет данных'))}</h3>"
            f"<span class=\"status-pill {_status_class(scenario.get('mvp_status', 'manual'))}\">{_e(scenario.get('mvp_status', 'manual'))}</span>"
            "</div>"
            f"<div class=\"network-chain\">{''.join(chain_items)}</div>"
            f"<div class=\"tags\">{_tag_list(artifacts, 'tag tag--source')}</div>"
            "</article>"
        )

    return (
        "<div class=\"protocol-grid\">"
        "<article class=\"protocol-card protocol-card--wide\">"
        "<h3>Scenario Artifact Contract</h3>"
        f"<p>{_e(contract.get('rule', 'каждый этап закрыт только проверяемым артефактом'))}</p>"
        f"<p><strong>Документ:</strong> {_e(contract.get('source_doc', 'нет данных'))}</p>"
        f"<p><strong>Суброли:</strong> {_e(contract.get('subroles_doc', 'нет данных'))}</p>"
        "</article>"
        "<article class=\"protocol-card protocol-card--wide\">"
        "<h3>Status model</h3>"
        f"<div class=\"tags\">{_tag_list(statuses)}</div>"
        "</article>"
        "<article class=\"protocol-card protocol-card--wide\">"
        "<h3>Запреты</h3>"
        "<ul class=\"compact-list\">"
        + "".join(f"<li>{_e(item)}</li>" for item in forbidden_actions)
        + "</ul>"
        "</article>"
        "</div>"
        f"<div class=\"network-routes\">{''.join(scenario_cards)}</div>"
    )


WORKFLOW_POSITIONS = {
    "chief_orchestrator": (40, 36),
    "agent1_scout": (6, 8),
    "agent2_collector": (37, 5),
    "agent3_processor": (68, 8),
    "agent4_publisher": (6, 64),
    "agent5_crm": (68, 64),
    "agent6_outreach": (37, 75),
}

CHIEF_NODE = {
    "node_id": "chief_orchestrator",
    "title": "Главный агент-оркестратор",
    "kind": "главный",
    "description": "Держит правила проекта, память, порядок шагов и проверку результата.",
    "okr": "Не дать системе расползтись: один следующий шаг, один ответственный агент, одна проверка.",
    "skills": ["маршрутизация", "контроль правил", "handoff", "escalation", "обновление REPORT"],
    "todo": "После каждого шага проверять, закрыт он или нет, и обновлять REPORT.md.",
    "readiness_percent": 90,
    "status": "active",
}

WORKFLOW_EDGES = [
    ("chief_orchestrator", "agent1_scout"),
    ("chief_orchestrator", "agent2_collector"),
    ("chief_orchestrator", "agent3_processor"),
    ("chief_orchestrator", "agent4_publisher"),
    ("chief_orchestrator", "agent5_crm"),
    ("chief_orchestrator", "agent6_outreach"),
    ("agent1_scout", "agent2_collector"),
    ("agent1_scout", "agent4_publisher"),
    ("agent1_scout", "agent5_crm"),
    ("agent2_collector", "agent3_processor"),
    ("agent3_processor", "agent5_crm"),
    ("agent4_publisher", "agent5_crm"),
    ("agent6_outreach", "agent5_crm"),
]


def _workflow_node(
    *,
    node_id: str,
    title: object,
    kind: object,
    description: object,
    okr: object,
    skills: list[Any],
    todo: object,
    readiness_percent: object,
    okr_readiness_percent: object,
    status: object,
    is_agent: bool,
) -> str:
    left, top = WORKFLOW_POSITIONS.get(node_id, (10, 10))
    agent_attr = f" data-agent=\"{_e(node_id)}\"" if is_agent else ""
    modifier = " workflow-node--agent" if is_agent else " workflow-node--chief"
    return (
        "<button class=\"workflow-node"
        f"{modifier}\" type=\"button\" data-node-id=\"{_e(node_id)}\""
        f"{agent_attr} data-left=\"{_e(left)}\" data-top=\"{_e(top)}\""
        f" aria-label=\"Переместить узел {_e(title)}\">"
        f"<span class=\"workflow-node__kind\">{_e(kind)}</span>"
        f"<strong>{_e(title)}</strong>"
        f"<small>{_e(description)}</small>"
        "<span class=\"workflow-progress\">"
        f"<span style=\"width: {_e(readiness_percent)}%\"></span>"
        "</span>"
        f"<em class=\"status-pill {_status_class(status)}\">готово {_e(readiness_percent)}%</em>"
        f"<span class=\"workflow-node__okr\"><b>OKR:</b> {_e(okr)}</span>"
        f"<span class=\"workflow-node__todo\"><b>Доделать:</b> {_e(todo)}</span>"
        f"<span class=\"workflow-node__okr\"><b>KR готовность:</b> {_e(okr_readiness_percent)}%</span>"
        f"<span class=\"workflow-node__skills\">{_tag_list(skills)}</span>"
        "</button>"
    )


def _draggable_workflow_board(agents: list[dict[str, Any]]) -> str:
    agent_by_id = {
        str(agent.get("agent_id", "")): agent
        for agent in agents
        if isinstance(agent, dict) and agent.get("agent_id")
    }
    agent_order = [
        "agent1_scout",
        "agent2_collector",
        "agent3_processor",
        "agent4_publisher",
        "agent5_crm",
        "agent6_outreach",
    ]

    nodes = []
    nodes.append(
        _workflow_node(
            node_id=CHIEF_NODE["node_id"],
            title=CHIEF_NODE["title"],
            kind=CHIEF_NODE["kind"],
            description=CHIEF_NODE["description"],
            okr=CHIEF_NODE["okr"],
            skills=CHIEF_NODE["skills"],
            todo=CHIEF_NODE["todo"],
            readiness_percent=CHIEF_NODE["readiness_percent"],
            okr_readiness_percent=CHIEF_NODE["readiness_percent"],
            status=CHIEF_NODE["status"],
            is_agent=False,
        )
    )
    for agent_id in agent_order:
        agent = agent_by_id.get(agent_id)
        if not agent:
            continue
        nodes.append(
            _workflow_node(
                node_id=agent_id,
                title=agent.get("title", agent_id),
                kind="агент",
                description=agent.get("description", "нет данных"),
                okr=agent.get("okr", "нет данных"),
                skills=agent.get("skills", []),
                todo=agent.get("todo", agent.get("next_action", "нет данных")),
                readiness_percent=agent.get("readiness_percent", "нет данных"),
                okr_readiness_percent=agent.get("okr_readiness_percent", agent.get("readiness_percent", "нет данных")),
                status=agent.get("panel_status", "NO_DATA"),
                is_agent=True,
            )
        )

    edge_html = "\n".join(
        "<line class=\"workflow-edge\""
        f" data-from=\"{_e(start)}\" data-to=\"{_e(end)}\"></line>"
        for start, end in WORKFLOW_EDGES
    )
    return (
        "<section class=\"workflow-board\" aria-label=\"Перемещаемая карта агентов\">"
        "<div class=\"section-heading\">"
        "<h2>Перемещаемая карта агентов</h2>"
        "<button class=\"ghost-button\" type=\"button\" data-workflow-reset>"
        "Сбросить расположение"
        "</button>"
        "</div>"
        "<p class=\"lead-text\">"
        "В центре главный агент-оркестратор. Вокруг него 6 рабочих агентов, их связи, OKR, скиллы, процент готовности и что нужно доделать."
        "</p>"
        "<div class=\"workflow-canvas\" id=\"workflowCanvas\">"
        "<svg class=\"workflow-svg\" id=\"workflowSvg\" aria-hidden=\"true\">"
        f"{edge_html}"
        "</svg>"
        f"{''.join(nodes)}"
        "</div>"
        "<p class=\"workflow-help\">"
        "Карточки можно двигать как на доске Obsidian. Положение запоминается только на этом компьютере."
        "</p>"
        "</section>"
    )


def build_html(dashboard: dict[str, Any]) -> str:
    top_panel = dashboard.get("top_panel", {})
    visual_display = dashboard.get("visual_display", {})
    source_map = dashboard.get("source_map", {})
    bitrix_crm_hygiene = dashboard.get("bitrix_crm_hygiene", {})
    vpp_ai_manager_dry_run = dashboard.get("vpp_ai_manager_dry_run", {})
    first_safe_growth_tests = dashboard.get("first_safe_growth_tests", {})
    bitrix_reactivation_readonly_plan = dashboard.get("bitrix_reactivation_readonly_plan", {})
    tender_filter_pack_dry_run = dashboard.get("tender_filter_pack_dry_run", {})
    client_acquisition_pack_dry_run = dashboard.get("client_acquisition_pack_dry_run", {})
    three_qualified_leads_sprint = dashboard.get("three_qualified_leads_sprint", {})
    interaction_graph = dashboard.get("interaction_graph", {})
    management_protocol = dashboard.get("management_protocol", {})
    mas_reference_layer = dashboard.get("mas_reference_layer", {})
    security_agent_control_layer = dashboard.get("security_agent_control_layer", {})
    scenario_artifact_contract = dashboard.get("scenario_artifact_contract", {})
    agent_map = dashboard.get("agent_map", {})
    agents = dashboard.get("agent_details", [])
    events = dashboard.get("event_stream", [])
    metrics = dashboard.get("metrics_dashboard", {})
    checker = dashboard.get("checker", {})
    locks = top_panel.get("locks", {})
    top_external_calls = top_panel.get("external_calls", {})
    generated_at = _utc_now()

    if not isinstance(top_panel, dict):
        top_panel = {}
    if not isinstance(visual_display, dict):
        visual_display = {}
    if not isinstance(source_map, dict):
        source_map = {}
    if not isinstance(bitrix_crm_hygiene, dict):
        bitrix_crm_hygiene = {}
    if not isinstance(vpp_ai_manager_dry_run, dict):
        vpp_ai_manager_dry_run = {}
    if not isinstance(first_safe_growth_tests, dict):
        first_safe_growth_tests = {}
    if not isinstance(bitrix_reactivation_readonly_plan, dict):
        bitrix_reactivation_readonly_plan = {}
    if not isinstance(tender_filter_pack_dry_run, dict):
        tender_filter_pack_dry_run = {}
    if not isinstance(client_acquisition_pack_dry_run, dict):
        client_acquisition_pack_dry_run = {}
    if not isinstance(three_qualified_leads_sprint, dict):
        three_qualified_leads_sprint = {}
    if not isinstance(interaction_graph, dict):
        interaction_graph = {}
    if not isinstance(management_protocol, dict):
        management_protocol = {}
    if not isinstance(mas_reference_layer, dict):
        mas_reference_layer = {}
    if not isinstance(security_agent_control_layer, dict):
        security_agent_control_layer = {}
    if not isinstance(scenario_artifact_contract, dict):
        scenario_artifact_contract = {}
    if not isinstance(agent_map, dict):
        agent_map = {}
    if not isinstance(agents, list):
        agents = []
    if not isinstance(events, list):
        events = []
    if not isinstance(metrics, dict):
        metrics = {}
    if not isinstance(checker, dict):
        checker = {}
    if not isinstance(locks, dict):
        locks = {}
    if not isinstance(top_external_calls, dict):
        top_external_calls = {}

    departments = visual_display.get("departments", [])
    operating_flow = visual_display.get("operating_flow", [])
    handoffs = visual_display.get("handoffs", [])
    control_blocks = visual_display.get("control_blocks", [])
    interaction_routes = interaction_graph.get("routes", [])
    if not isinstance(departments, list):
        departments = []
    if not isinstance(operating_flow, list):
        operating_flow = []
    if not isinstance(handoffs, list):
        handoffs = []
    if not isinstance(control_blocks, list):
        control_blocks = []
    if not isinstance(interaction_routes, list):
        interaction_routes = []

    workflow_board = _draggable_workflow_board(agents)
    workflow_css = """
    .workflow-board {
      margin-top: 14px;
      padding: 14px;
      display: grid;
      gap: 12px;
    }
    .ghost-button {
      appearance: none;
      border: 1px solid var(--accent);
      border-radius: 999px;
      padding: 7px 11px;
      background: #ffffff;
      color: var(--accent);
      cursor: pointer;
      font: inherit;
      font-size: 12px;
      font-weight: 800;
    }
    .ghost-button:hover {
      background: var(--accent-bg);
    }
    .workflow-canvas {
      position: relative;
      min-height: 760px;
      overflow: hidden;
      border: 1px dashed #b8cbd6;
      border-radius: 12px;
      background:
        linear-gradient(90deg, rgba(45, 95, 134, .06) 1px, transparent 1px),
        linear-gradient(0deg, rgba(45, 95, 134, .06) 1px, transparent 1px),
        #ffffff;
      background-size: 34px 34px;
      touch-action: none;
    }
    .workflow-svg {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 1;
    }
    .workflow-edge {
      stroke: rgba(45, 95, 134, .44);
      stroke-width: 2;
      stroke-linecap: round;
      stroke-dasharray: 7 7;
    }
    .workflow-node {
      position: absolute;
      z-index: 2;
      width: 292px;
      min-height: 248px;
      display: grid;
      align-content: start;
      gap: 8px;
      padding: 13px;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: rgba(255, 253, 248, .96);
      color: inherit;
      box-shadow: 0 12px 26px rgba(23, 32, 38, .08);
      cursor: grab;
      text-align: left;
      font: inherit;
      user-select: none;
      touch-action: none;
    }
    .workflow-node:hover,
    .workflow-node.is-active {
      border-color: var(--accent);
      box-shadow: 0 14px 30px rgba(45, 95, 134, .16);
    }
    .workflow-node.is-dragging {
      cursor: grabbing;
      z-index: 5;
      box-shadow: 0 18px 38px rgba(23, 32, 38, .2);
    }
    .workflow-node--agent {
      border-color: #a9c4d6;
    }
    .workflow-node--chief {
      width: 324px;
      min-height: 268px;
      background:
        radial-gradient(circle at 12% 10%, rgba(255, 255, 255, .7), transparent 34%),
        linear-gradient(135deg, #13354a, #2d5f86);
      color: #ffffff;
      border-color: #13354a;
      box-shadow: 0 18px 46px rgba(19, 53, 74, .28);
    }
    .workflow-node__kind {
      width: max-content;
      padding: 3px 7px;
      border-radius: 999px;
      background: #eef4f7;
      color: var(--accent);
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
    }
    .workflow-node strong {
      font-size: 14px;
    }
    .workflow-node--chief strong {
      font-size: 16px;
    }
    .workflow-node small {
      color: var(--muted);
      font-size: 12px;
      overflow-wrap: anywhere;
    }
    .workflow-node--chief small,
    .workflow-node--chief .workflow-node__okr,
    .workflow-node--chief .workflow-node__todo {
      color: rgba(255, 255, 255, .86);
    }
    .workflow-node .status-pill {
      width: max-content;
    }
    .workflow-progress {
      display: block;
      width: 100%;
      height: 7px;
      overflow: hidden;
      border-radius: 999px;
      background: rgba(45, 95, 134, .14);
    }
    .workflow-progress span {
      display: block;
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, #64a889, #2d5f86);
    }
    .workflow-node--chief .workflow-progress {
      background: rgba(255, 255, 255, .2);
    }
    .workflow-node--chief .workflow-progress span {
      background: linear-gradient(90deg, #f5e7c4, #ffffff);
    }
    .workflow-node__okr,
    .workflow-node__todo {
      color: var(--muted);
      font-size: 12px;
      overflow-wrap: anywhere;
    }
    .workflow-node__skills {
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
    }
    .workflow-node__skills .tag {
      min-height: 20px;
      padding: 2px 7px;
      font-size: 11px;
    }
    .workflow-node--chief .tag {
      color: #17364a;
      background: rgba(255, 255, 255, .86);
    }
    .workflow-help {
      color: var(--muted);
      font-size: 12px;
    }
"""
    workflow_script = """
    function initDraggableWorkflow() {
      const canvas = document.getElementById('workflowCanvas');
      const svg = document.getElementById('workflowSvg');
      if (!canvas || !svg) return;

      const storageKey = 'leadEngineAgentWorkflowPositionsV1';
      const nodes = Array.from(canvas.querySelectorAll('.workflow-node'));
      const edges = Array.from(svg.querySelectorAll('.workflow-edge'));
      const resetButton = document.querySelector('[data-workflow-reset]');

      function readSavedPositions() {
        try {
          return JSON.parse(window.localStorage.getItem(storageKey) || '{}');
        } catch (error) {
          return {};
        }
      }

      function savePositions() {
        const payload = {};
        nodes.forEach((node) => {
          payload[node.dataset.nodeId] = {
            x: node.offsetLeft,
            y: node.offsetTop,
          };
        });
        try {
          window.localStorage.setItem(storageKey, JSON.stringify(payload));
        } catch (error) {
          // localStorage can be unavailable in strict private modes; the board
          // still works for the current view even without persistence.
        }
      }

      function applyPositions(savedPositions) {
        nodes.forEach((node) => {
          const saved = savedPositions[node.dataset.nodeId];
          if (saved && Number.isFinite(saved.x) && Number.isFinite(saved.y)) {
            node.style.left = `${saved.x}px`;
            node.style.top = `${saved.y}px`;
          } else {
            node.style.left = `${node.dataset.left}%`;
            node.style.top = `${node.dataset.top}%`;
          }
        });
      }

      function updateEdges() {
        const canvasRect = canvas.getBoundingClientRect();
        edges.forEach((edge) => {
          const from = canvas.querySelector(`[data-node-id="${edge.dataset.from}"]`);
          const to = canvas.querySelector(`[data-node-id="${edge.dataset.to}"]`);
          if (!from || !to) return;
          const fromRect = from.getBoundingClientRect();
          const toRect = to.getBoundingClientRect();
          edge.setAttribute('x1', fromRect.left - canvasRect.left + fromRect.width / 2);
          edge.setAttribute('y1', fromRect.top - canvasRect.top + fromRect.height / 2);
          edge.setAttribute('x2', toRect.left - canvasRect.left + toRect.width / 2);
          edge.setAttribute('y2', toRect.top - canvasRect.top + toRect.height / 2);
        });
      }

      function clamp(value, min, max) {
        return Math.min(Math.max(value, min), max);
      }

      nodes.forEach((node) => {
        node.addEventListener('pointerdown', (event) => {
          if (event.button !== undefined && event.button !== 0) return;
          const startX = event.clientX;
          const startY = event.clientY;
          const originLeft = node.offsetLeft;
          const originTop = node.offsetTop;

          node.classList.add('is-dragging');
          node.setPointerCapture(event.pointerId);

          function onMove(moveEvent) {
            const maxLeft = canvas.clientWidth - node.offsetWidth - 8;
            const maxTop = canvas.clientHeight - node.offsetHeight - 8;
            const nextLeft = clamp(originLeft + moveEvent.clientX - startX, 8, maxLeft);
            const nextTop = clamp(originTop + moveEvent.clientY - startY, 8, maxTop);
            node.style.left = `${nextLeft}px`;
            node.style.top = `${nextTop}px`;
            updateEdges();
          }

          function onEnd(endEvent) {
            node.classList.remove('is-dragging');
            node.removeEventListener('pointermove', onMove);
            node.removeEventListener('pointerup', onEnd);
            node.removeEventListener('pointercancel', onEnd);
            try {
              node.releasePointerCapture(endEvent.pointerId);
            } catch (error) {
              // If capture was already released, no action is needed.
            }
            savePositions();
            updateEdges();
          }

          node.addEventListener('pointermove', onMove);
          node.addEventListener('pointerup', onEnd);
          node.addEventListener('pointercancel', onEnd);
          event.preventDefault();
        });
      });

      if (resetButton) {
        resetButton.addEventListener('click', () => {
          try {
            window.localStorage.removeItem(storageKey);
          } catch (error) {
            // Safe no-op.
          }
          applyPositions({});
          requestAnimationFrame(updateEdges);
        });
      }

      applyPositions(readSavedPositions());
      requestAnimationFrame(updateEdges);
      window.addEventListener('resize', updateEdges);
    }
"""

    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <title>Agent Dashboard — design-studio-lead-engine</title>
  <style>
    :root {{
      --bg: #f7f5ef;
      --panel: #fffdf8;
      --ink: #172026;
      --muted: #68737d;
      --line: #d8d3c8;
      --ok: #116b4f;
      --ok-bg: #dff3e9;
      --wait: #8a5c13;
      --wait-bg: #f5e7c4;
      --bad: #9b2933;
      --bad-bg: #f6d8dc;
      --neutral: #46525c;
      --neutral-bg: #e8ecef;
      --accent: #2d5f86;
      --accent-bg: #dcecf6;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.35;
    }}
    main {{
      width: min(1480px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 18px 0 28px;
    }}
    h1, h2, h3, p {{ margin: 0; }}
    h1 {{ font-size: 26px; line-height: 1.1; }}
    h2 {{ font-size: 18px; }}
    h3 {{ font-size: 13px; color: var(--muted); text-transform: uppercase; }}
    code {{ font-family: Menlo, Consolas, monospace; font-size: 12px; overflow-wrap: anywhere; }}
    .top-panel, .lecture-map, .source-map, .workflow-board, .interaction-map, .protocol-map, .dashboard-grid > section, .agent-card, .agent-detail, .event-row, .metric-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    .top-panel {{
      display: grid;
      grid-template-columns: minmax(240px, 1.1fr) minmax(280px, 1.7fr) minmax(220px, .9fr);
      gap: 14px;
      padding: 16px;
    }}
    .top-panel__meta {{
      display: grid;
      gap: 8px;
    }}
    .stage-box {{
      display: grid;
      gap: 8px;
      padding: 12px;
      background: #ffffff;
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    .stage-box span, .muted, .agent-card small, .event-row span {{
      color: var(--muted);
      font-size: 12px;
    }}
    .status-pill, .flag, .lock-chip, .tag {{
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      border-radius: 999px;
      padding: 3px 9px;
      font-size: 12px;
      font-style: normal;
      font-weight: 700;
      white-space: nowrap;
    }}
    .is-ok {{ color: var(--ok); background: var(--ok-bg); }}
    .is-wait {{ color: var(--wait); background: var(--wait-bg); }}
    .is-bad {{ color: var(--bad); background: var(--bad-bg); }}
    .is-neutral {{ color: var(--neutral); background: var(--neutral-bg); }}
    .lock-chip.is-locked {{ color: var(--bad); background: var(--bad-bg); }}
    .lock-chip.is-open {{ color: var(--ok); background: var(--ok-bg); }}
    .flag.is-on {{ color: var(--bad); background: var(--bad-bg); }}
    .flag.is-off {{ color: var(--ok); background: var(--ok-bg); }}
    .chip-row, .tags {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }}
    .tag {{
      color: var(--accent);
      background: var(--accent-bg);
      font-weight: 600;
      white-space: normal;
    }}
    .tag--guard {{
      color: var(--bad);
      background: var(--bad-bg);
    }}
    .safety-list {{
      display: grid;
      gap: 6px;
      padding-left: 18px;
      margin: 0;
      color: var(--bad);
      font-size: 13px;
    }}
    .source-map {{
      margin-top: 14px;
      padding: 14px;
      display: grid;
      gap: 12px;
    }}
    .source-stat-grid {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 8px;
    }}
    .source-stat-card {{
      display: grid;
      gap: 3px;
      min-height: 76px;
      align-content: center;
      padding: 10px;
      border: 1px solid #cbdce5;
      border-radius: 8px;
      background: #f8fbfc;
    }}
    .source-stat-card span {{
      color: var(--muted);
      font-size: 11px;
    }}
    .source-stat-card strong {{
      color: var(--accent);
      font-size: 24px;
      line-height: 1;
    }}
    .source-two-col {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }}
    .source-panel, .source-details {{
      display: grid;
      gap: 9px;
      padding: 11px;
      background: #ffffff;
      border: 1px solid var(--line);
      border-radius: 8px;
      min-width: 0;
    }}
    .source-details summary {{
      cursor: pointer;
      color: var(--accent);
      font-weight: 850;
    }}
    .source-table-wrap {{
      max-height: 360px;
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #ffffff;
    }}
    .source-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
    }}
    .source-table th, .source-table td {{
      padding: 8px;
      border-bottom: 1px solid #ece7dd;
      text-align: left;
      vertical-align: top;
    }}
    .source-table th {{
      position: sticky;
      top: 0;
      background: #f8fbfc;
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      z-index: 1;
    }}
    .tag--source {{
      align-items: flex-start;
      flex-direction: column;
      gap: 2px;
      border-radius: 8px;
      white-space: normal;
    }}
    .tag--source small {{
      color: var(--muted);
      font-size: 10px;
      font-weight: 500;
    }}
    .agent-source-panel {{
      display: grid;
      gap: 9px;
      padding: 11px;
      border: 1px solid #cbdce5;
      border-radius: 8px;
      background: #ffffff;
    }}
    .agent-source-panel p {{
      color: var(--muted);
      font-size: 13px;
    }}
    .agent-source-panel h4 {{
      margin: 0;
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
    }}
    .source-mini-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 6px;
    }}
    .source-mini-grid span {{
      display: grid;
      gap: 2px;
      padding: 8px;
      border: 1px solid #d7e3e8;
      border-radius: 7px;
      background: #f8fbfc;
      color: var(--muted);
      font-size: 11px;
    }}
    .source-mini-grid strong {{
      color: var(--accent);
      font-size: 18px;
      line-height: 1;
    }}
    .dashboard-grid {{
      display: grid;
      grid-template-columns: minmax(360px, .85fr) minmax(560px, 1.15fr);
      gap: 14px;
      margin-top: 14px;
    }}
    .lecture-map {{
      margin-top: 14px;
      padding: 14px;
      display: grid;
      gap: 14px;
    }}
    .interaction-map {{
      margin-top: 14px;
      padding: 14px;
      display: grid;
      gap: 12px;
    }}
    .protocol-map {{
      margin-top: 14px;
      padding: 14px;
      display: grid;
      gap: 12px;
    }}
    .protocol-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }}
    .protocol-card {{
      display: grid;
      gap: 8px;
      padding: 12px;
      background: #ffffff;
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    .protocol-card--wide {{
      grid-column: 1 / -1;
    }}
    .network-routes {{
      display: grid;
      gap: 10px;
    }}
    .network-route {{
      display: grid;
      gap: 10px;
      padding: 12px;
      background: #ffffff;
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    .network-route__head {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
    }}
    .network-chain {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 6px;
    }}
    .network-node {{
      display: inline-flex;
      align-items: center;
      min-height: 34px;
      padding: 7px 10px;
      border-radius: 8px;
      background: #eef4f7;
      border: 1px solid #cbdce5;
      color: var(--ink);
      font-size: 13px;
      font-weight: 700;
    }}
    .network-arrow {{
      color: var(--accent);
      font-size: 18px;
      font-weight: 900;
      line-height: 1;
    }}
    .network-meta {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }}
    .network-meta div {{
      display: grid;
      gap: 3px;
      min-width: 0;
      padding: 8px;
      border-radius: 6px;
      background: #f7fafb;
      border: 1px solid #d7e3e8;
    }}
    .network-meta span {{
      color: var(--muted);
      font-size: 11px;
    }}
    .network-meta strong {{
      font-size: 12px;
      overflow-wrap: anywhere;
    }}
    .lecture-layout {{
      display: grid;
      grid-template-columns: minmax(260px, .75fr) minmax(520px, 1.25fr);
      gap: 14px;
    }}
    .department-grid, .handoff-list, .control-grid {{
      display: grid;
      gap: 8px;
    }}
    .department-card, .flow-step, .handoff-card, .control-card {{
      background: #ffffff;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px;
    }}
    .department-card {{
      display: grid;
      gap: 6px;
    }}
    .department-card__top {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 8px;
    }}
    .department-card span, .department-card p, .flow-step em, .flow-step p, .control-card span {{
      color: var(--muted);
      font-size: 12px;
      font-style: normal;
    }}
    .flow-rail {{
      display: grid;
      grid-template-columns: repeat(5, minmax(120px, 1fr));
      gap: 8px;
      margin-bottom: 12px;
    }}
    .flow-step {{
      min-height: 136px;
      display: grid;
      align-content: start;
      gap: 7px;
      position: relative;
    }}
    .flow-step > span {{
      width: 28px;
      height: 28px;
      display: inline-grid;
      place-items: center;
      border-radius: 999px;
      color: #ffffff;
      background: var(--accent);
      font-size: 13px;
      font-weight: 800;
    }}
    .handoff-card {{
      display: grid;
      gap: 8px;
    }}
    .handoff-route {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 7px;
    }}
    .handoff-route span {{
      color: var(--accent);
      font-weight: 800;
    }}
    .handoff-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 6px;
    }}
    .handoff-grid div {{
      display: grid;
      gap: 3px;
      padding: 7px;
      background: #f7fafb;
      border: 1px solid #d7e3e8;
      border-radius: 6px;
      min-width: 0;
    }}
    .handoff-grid span {{
      color: var(--muted);
      font-size: 11px;
    }}
    .handoff-grid strong {{
      font-size: 12px;
      overflow-wrap: anywhere;
    }}
    .control-grid {{
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }}
    .control-card {{
      display: grid;
      gap: 6px;
    }}
    .dashboard-grid > section {{
      padding: 14px;
      min-width: 0;
    }}
    .section-heading {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 10px;
    }}
    .agent-cards {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
    }}
    .agent-card {{
      display: grid;
      gap: 8px;
      min-height: 108px;
      padding: 11px;
      color: inherit;
      text-align: left;
      cursor: pointer;
      appearance: none;
      font: inherit;
    }}
    .agent-card:hover, .agent-card.is-active {{
      border-color: var(--accent);
      box-shadow: inset 0 0 0 1px var(--accent);
    }}
    .agent-card__top {{
      display: flex;
      justify-content: space-between;
      gap: 8px;
      align-items: flex-start;
    }}
    .agent-card span:not(.agent-card__top) {{
      color: var(--muted);
      font-size: 13px;
    }}
    .agent-detail {{
      display: none;
      padding: 14px;
    }}
    .agent-detail.is-active {{
      display: grid;
      gap: 12px;
    }}
    .lead-text {{
      font-size: 14px;
    }}
    .detail-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}
    .main-metric-card, .okr-metric-row {{
      display: grid;
      gap: 5px;
      padding: 10px;
      border-radius: 8px;
      border: 1px solid #cbdce5;
      background: #f8fbfc;
    }}
    .main-metric-card span, .okr-metric-row span {{
      color: var(--muted);
      font-size: 12px;
    }}
    .main-metric-card strong {{
      color: var(--ink);
      font-size: 17px;
    }}
    .main-metric-card em, .okr-metric-row strong {{
      color: var(--accent);
      font-style: normal;
      font-weight: 850;
    }}
    .main-metric-card p {{
      color: var(--muted);
      font-size: 13px;
    }}
    .okr-metric-list {{
      display: grid;
      gap: 6px;
    }}
    .subrole-grid {{
      display: grid;
      gap: 7px;
    }}
    .subrole-card {{
      display: grid;
      gap: 4px;
      padding: 9px;
      border-radius: 8px;
      border: 1px solid #cbdce5;
      background: #f8fbfc;
    }}
    .subrole-card strong {{
      color: var(--ink);
      font-size: 13px;
    }}
    .subrole-card span,
    .subrole-card small {{
      color: var(--muted);
      font-size: 12px;
    }}
    .compact-list {{
      display: grid;
      gap: 5px;
      margin: 8px 0 0;
      padding-left: 18px;
      font-size: 13px;
    }}
    .readiness-card {{
      display: grid;
      gap: 4px;
      margin-top: 8px;
      padding: 10px;
      border-radius: 8px;
      background: #eef4f7;
      border: 1px solid #cbdce5;
    }}
    .readiness-card strong {{
      color: var(--accent);
      font-size: 28px;
      line-height: 1;
    }}
    .readiness-card span {{
      color: var(--muted);
      font-size: 12px;
    }}
    .next-action {{
      display: grid;
      gap: 4px;
      padding: 10px;
      background: #eef4f7;
      border: 1px solid #cbdce5;
      border-radius: 8px;
    }}
    .next-action span {{
      color: var(--muted);
      font-size: 12px;
    }}
    .lower-grid {{
      display: grid;
      grid-template-columns: minmax(420px, 1fr) minmax(420px, 1fr);
      gap: 14px;
      margin-top: 14px;
    }}
    .event-list, .metric-grid {{
      display: grid;
      gap: 8px;
    }}
    .event-row {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 8px;
      padding: 10px;
    }}
    .event-row code {{
      grid-column: 1 / -1;
      color: var(--muted);
    }}
    .event-row div {{
      display: grid;
      gap: 3px;
      min-width: 0;
    }}
    .metric-grid {{
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }}
    .metric-card {{
      padding: 10px;
      display: grid;
      gap: 8px;
    }}
    .kv-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 6px;
    }}
    .kv-grid.small {{
      grid-template-columns: 1fr;
    }}
    .kv-item {{
      display: grid;
      gap: 2px;
      min-width: 0;
      padding: 7px;
      background: #ffffff;
      border: 1px solid var(--line);
      border-radius: 6px;
    }}
    .kv-item span {{
      color: var(--muted);
      font-size: 11px;
      overflow-wrap: anywhere;
    }}
    .kv-item strong {{
      font-size: 12px;
      overflow-wrap: anywhere;
    }}
    .footer-note {{
      margin-top: 14px;
      color: var(--muted);
      font-size: 12px;
    }}
{workflow_css}
    @media (max-width: 980px) {{
      main {{ width: min(100vw - 20px, 760px); }}
      .top-panel, .lecture-layout, .source-two-col, .dashboard-grid, .lower-grid, .detail-grid, .network-meta {{
        grid-template-columns: 1fr;
      }}
      .agent-cards, .metric-grid, .kv-grid, .flow-rail, .handoff-grid, .control-grid, .source-stat-grid, .source-mini-grid {{
        grid-template-columns: 1fr;
      }}
      .workflow-canvas {{
        min-height: 980px;
      }}
      .workflow-node {{
        width: min(292px, calc(100% - 20px));
      }}
      .workflow-node--chief {{
        width: min(324px, calc(100% - 20px));
      }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="top-panel" aria-label="Общий статус">
      <div class="top-panel__meta">
        <div class="section-heading">
          <h1>{_e(top_panel.get("project_name", "design-studio-lead-engine"))}</h1>
          <span class="status-pill {_status_class(top_panel.get("overall_status"))}">{_e(top_panel.get("overall_status", "NO_DATA"))}</span>
        </div>
        <div class="chip-row">
          <span class="status-pill is-neutral">6 агентов: {_e(agent_map.get("agents_count", len(agents)))}</span>
          <span class="status-pill is-neutral">JSON: data/reports/agent_dashboard.json</span>
        </div>
        <div class="chip-row">{_external_flags(top_external_calls)}</div>
      </div>

      <div class="stage-box">
        <span>Текущий этап</span>
        <strong>{_e(top_panel.get("current_stage", "нет данных"))}</strong>
        <span>Следующий маленький шаг</span>
        <strong>{_e(top_panel.get("next_small_step", dashboard.get("next_small_step", "нет данных")))}</strong>
        <span>Последняя проверка: {_e(top_panel.get("last_checked_at", "нет данных"))}</span>
      </div>

      <div class="stage-box" aria-label="Запреты">
        <span>Запреты</span>
        <div class="chip-row">{_locks(locks)}</div>
        <ul class="safety-list">
          {''.join(f"<li>{_e(item)}</li>" for item in PROHIBITIONS)}
        </ul>
      </div>
    </section>

    <section class="lecture-map" aria-label="Схема по лекции 5">
      <div class="section-heading">
        <h2>Схема по лекции 5</h2>
        <span class="status-pill is-neutral">{_e(visual_display.get("display_status", "read_only"))}</span>
      </div>
      <p class="lead-text">{_e(visual_display.get("lecture_model", "главный оркестратор -> департаменты -> агенты -> результат -> метрики -> REPORT"))}</p>
      <div class="lecture-layout">
        <div>
          <div class="section-heading">
            <h3>Департаменты</h3>
            <span class="status-pill is-neutral">{_e(len(departments))}</span>
          </div>
          <div class="department-grid">
            {_department_cards(departments)}
          </div>
        </div>
        <div>
          <div class="section-heading">
            <h3>Поток результата</h3>
            <span class="status-pill is-neutral">оркестратор -> REPORT</span>
          </div>
          <div class="flow-rail">
            {_flow_steps(operating_flow)}
          </div>
          <div class="section-heading">
            <h3>Связи и handoff</h3>
            <span class="status-pill is-neutral">кто -> кому</span>
          </div>
          <div class="handoff-list">
            {_handoff_cards(handoffs)}
          </div>
        </div>
      </div>
      <div>
        <div class="section-heading">
          <h3>Read-only команды контроля</h3>
          <span class="status-pill is-ok">без внешних сервисов</span>
        </div>
        <div class="control-grid">
          {_control_blocks(control_blocks)}
        </div>
      </div>
    </section>

    {_source_map_section(source_map)}

    {_bitrix_crm_hygiene_section(bitrix_crm_hygiene)}

    {_vpp_ai_manager_dry_run_section(vpp_ai_manager_dry_run)}

    {_first_safe_growth_tests_section(first_safe_growth_tests)}

    {_bitrix_reactivation_readonly_plan_section(bitrix_reactivation_readonly_plan)}

    {_tender_filter_pack_dry_run_section(tender_filter_pack_dry_run)}

    {_client_acquisition_pack_dry_run_section(client_acquisition_pack_dry_run)}

    {_three_qualified_leads_sprint_section(three_qualified_leads_sprint)}

    {workflow_board}

    <section class="interaction-map" aria-label="Карта взаимодействий агентов">
      <div class="section-heading">
        <h2>Карта взаимодействий агентов</h2>
        <span class="status-pill is-neutral">{_e(interaction_graph.get("graph_status", "read_only"))}</span>
      </div>
      <p class="lead-text">{_e(interaction_graph.get("purpose", "как агенты передают результат друг другу"))}</p>
      <div class="network-routes">
        {_interaction_routes(interaction_routes)}
      </div>
    </section>

    <section class="protocol-map" aria-label="Chief of Staff / Handoff / Escalation / Weekly digest">
      <div class="section-heading">
        <h2>Chief of Staff / Handoff / Escalation / Weekly digest</h2>
        <span class="status-pill {_status_class(management_protocol.get("protocol_status", "read_only"))}">{_e(management_protocol.get("protocol_status", "read_only"))}</span>
      </div>
      <p class="lead-text">
        Управленческий слой без Agent 7: вход задачи -> маршрутизация -> агенты -> QA/checker -> результат -> память.
      </p>
      {_management_protocol(management_protocol)}
    </section>

    <section class="protocol-map" aria-label="MAS reference layer">
      <div class="section-heading">
        <h2>MAS reference layer</h2>
        <span class="status-pill {_status_class(mas_reference_layer.get("status", "read_only"))}">{_e(mas_reference_layer.get("status", "read_only"))}</span>
      </div>
      <p class="lead-text">
        Применяем внешний референс как модель управления: инспектор агента, timeline сценариев, артефакты, статусы и OSINT-протокол без Agent 7.
      </p>
      {_mas_reference_layer(mas_reference_layer)}
    </section>

    <section class="protocol-map" aria-label="Security Agent Control Layer">
      <div class="section-heading">
        <h2>Security Agent Control Layer</h2>
        <span class="status-pill {_status_class(security_agent_control_layer.get("status", "read_only"))}">{_e(security_agent_control_layer.get("status", "read_only"))}</span>
      </div>
      <p class="lead-text">
        AGENT_SECURITY.md подключён как контроль безопасности для всех 6 агентов, checker/dashboard, LLM и MCP/API. Это не Agent 7.
      </p>
      {_security_agent_control_layer(security_agent_control_layer)}
    </section>

    <section class="protocol-map" aria-label="Scenario Artifact Contract">
      <div class="section-heading">
        <h2>Scenario Artifact Contract</h2>
        <span class="status-pill {_status_class(scenario_artifact_contract.get("status", "read_only"))}">{_e(scenario_artifact_contract.get("status", "read_only"))}</span>
      </div>
      <p class="lead-text">
        Контракт из урока: сценарий -> шаг -> агент -> суброль -> артефакт -> статус -> проверка -> следующий шаг.
      </p>
      {_scenario_artifact_contract(scenario_artifact_contract)}
    </section>

    <div class="dashboard-grid">
      <section aria-label="Карточки агентов">
        <div class="section-heading">
          <h2>6 агентов</h2>
          <span class="status-pill is-neutral">только просмотр</span>
        </div>
        <div class="agent-cards">
          {_agent_cards(agents)}
        </div>
      </section>

      <section aria-label="Детали агента">
        <div class="section-heading">
          <h2>Детали агента</h2>
          <span class="status-pill {_status_class(checker.get("agent_contract_status"))}">checker: {_e(checker.get("agent_contract_status", "NO_DATA"))}</span>
        </div>
        {_agent_details(agents)}
      </section>
    </div>

    <div class="lower-grid">
      <section aria-label="Последние события">
        <div class="section-heading">
          <h2>Последние события</h2>
          <span class="status-pill is-neutral">{_e(len(events))} в JSON</span>
        </div>
        <div class="event-list">
          {_events(events)}
        </div>
      </section>

      <section aria-label="Метрики">
        <div class="section-heading">
          <h2>Метрики</h2>
          <span class="status-pill is-neutral">без live API</span>
        </div>
        <div class="metric-grid">
          {_metrics(metrics)}
        </div>
      </section>
    </div>

    <p class="footer-note">
      Сгенерировано: {_e(generated_at)}. Источник: data/reports/agent_dashboard.json.
      Redis, Bitrix24, Telegram, IMAP, LLM, scheduler и publisher этим просмотрщиком не запускаются.
    </p>
  </main>

  <script>
    const cards = document.querySelectorAll('[data-agent]');
    const details = document.querySelectorAll('[data-agent-detail]');
    cards.forEach((card) => {{
      card.addEventListener('click', () => {{
        const id = card.getAttribute('data-agent');
        cards.forEach((item) => item.classList.toggle('is-active', item === card));
        details.forEach((item) => item.classList.toggle('is-active', item.getAttribute('data-agent-detail') === id));
      }});
    }});
{workflow_script}
    initDraggableWorkflow();
  </script>
</body>
</html>
"""


def run() -> dict[str, Any]:
    dashboard = _load_dashboard()
    html = build_html(dashboard)
    DASHBOARD_HTML_PATH.write_text(html, encoding="utf-8")
    return {
        "dashboard_viewer_build_status": "OK",
        "source_file": str(DASHBOARD_JSON_PATH.relative_to(PROJECT_ROOT)),
        "viewer_file": str(DASHBOARD_HTML_PATH.relative_to(PROJECT_ROOT)),
        "agents_count": len(dashboard.get("agent_details", [])),
        "event_count": len(dashboard.get("event_stream", [])),
        "external_calls": {
            "redis": False,
            "bitrix24": False,
            "telegram_send": False,
            "imap": False,
            "llm": False,
            "scheduler": False,
            "publisher": False,
        },
    }


def main() -> int:
    result = run()
    for key in [
        "dashboard_viewer_build_status",
        "source_file",
        "viewer_file",
        "agents_count",
        "event_count",
    ]:
        print(f"{key}={result[key]}")
    print(
        "external_calls="
        + ",".join(f"{key}:{value}" for key, value in result["external_calls"].items())
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
