"""Build a local read-only JSON dashboard for the six-agent system.

This script reads only project documents and local JSON reports. It does not
import runtime agent modules and does not call Redis, Bitrix24, Telegram, IMAP,
LLM APIs, scheduler, publisher, or any paid service.
"""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = PROJECT_ROOT / "data" / "reports"
DASHBOARD_REPORT_PATH = REPORTS_DIR / "agent_dashboard.json"
CHECKER_REPORT_PATH = REPORTS_DIR / "agent_okr_contract_check.json"
BITRIX_AUDIT_PATH = REPORTS_DIR / "bitrix_readonly_audit.json"
VPP_AI_MANAGER_DRY_RUN_PATH = REPORTS_DIR / "vpp_ai_manager_dry_run.json"
LECTURE_GROWTH_SOURCE_SCORE_PATH = REPORTS_DIR / "lecture_growth_source_score.json"
FIRST_SAFE_GROWTH_TESTS_PATH = REPORTS_DIR / "first_safe_growth_tests.json"
BITRIX_REACTIVATION_READONLY_PLAN_PATH = REPORTS_DIR / "bitrix_reactivation_readonly_plan.json"
TENDER_FILTER_PACK_DRY_RUN_PATH = REPORTS_DIR / "tender_filter_pack_dry_run.json"
CLIENT_ACQUISITION_PACK_DRY_RUN_PATH = REPORTS_DIR / "client_acquisition_pack_dry_run.json"
THREE_QUALIFIED_LEADS_SPRINT_PATH = REPORTS_DIR / "three_qualified_leads_sprint.json"
CHANNEL_REGISTRY_PATH = PROJECT_ROOT / "content" / "library" / "sources" / "channel-registry-mvp.csv"
COMPETITOR_WATCHLIST_PATH = PROJECT_ROOT / "content" / "library" / "sources" / "competitor-channel-watchlist.csv"
YANIKA_KNOWN_CHANNELS_PATH = PROJECT_ROOT / "content" / "library" / "sources" / "yanika-known-channels-template.csv"
LECTURE_GROWTH_SOURCE_MAP_PATH = PROJECT_ROOT / "content" / "library" / "sources" / "lecture-2026-05-15-growth-source-map.csv"
SECURITY_AGENT_PATH = PROJECT_ROOT / "agents" / "Агент безопастности" / "AGENT_SECURITY.md"
SECURITY_CONTROL_DOC_PATH = PROJECT_ROOT / "docs" / "security-agent-control-layer.md"


CONTENT_SURFACES = [
    "MAX-канал СИЛА Проекта",
    "Telegram",
    "VK",
    "Дзен",
    "Яндекс Карты",
    "2GIS",
    "новый сайт / блог",
]

BACKLOG_SOURCES = [
    "2GIS как отдельный lead/referrer source",
    "VK-группы и обсуждения",
    "коммерческие тендерные площадки",
    "HH.ru вакансии как сигнал спроса на проектирование",
    "партнёры: риелторы, дизайнеры, юристы, кадастровые инженеры",
    "сайт / лендинги / SEO-страницы услуг",
    "лид-магнит ПРОВЕРКА перепланировки",
    "ЕИС и госзакупки",
    "закупки девелоперов и сетевых компаний",
    "каталоги франшиз и коммерческой недвижимости",
    "банки, ипотечные брокеры, оценщики и страховые",
    "БТИ / кадастровые / юридические партнёры",
    "поставщики, подрядчики fit-out и вывесок",
    "форумы, Яндекс Q, TenChat",
    "GEO/AI visibility: ChatGPT, Perplexity, Яндекс/Алиса и нейропоиск",
    "Reels/shorts radar и ROMI по контенту позже",
]

AGENT_SOURCE_NOTES = {
    "agent1_scout": "Смотрит весь рынок: 17 системных каналов, конкурентов, каналы Яники и backlog-источники.",
    "agent2_collector": "Собирает входящие лиды из разрешённых площадок первой волны.",
    "agent3_processor": "Не ходит наружу: принимает RawLead от Agent 2/6 и должен уметь обработать лиды из всех каналов первой волны.",
    "agent4_publisher": "Отвечает за каналы доверия, контентные поверхности, сайт, карты и будущие платные/органические источники.",
    "agent5_crm": "Считает всю сквозную аналитику по 17 каналам и принимает CRM-события.",
    "agent6_outreach": "Готовит первое касание по диалогам и ручному outbound, но ничего не отправляет без approval.",
}


AGENT_CONFIG: dict[str, dict[str, Any]] = {
    "agent1_scout": {
        "title": "Agent 1 Scout",
        "department": "Разведка источников",
        "panel_status": "planned/manual",
        "description": "Ищет, где могут появляться будущие заказчики и какие темы важны рынку.",
        "readiness_percent": 35,
        "okr": "Дать системе понятный список перспективных источников и первый следующий шаг по каждому источнику.",
        "inputs": ["рынок", "конкуренты", "отзывы", "карты", "тендерные площадки"],
        "outputs": ["source cards для Agent 2", "темы и боли для Agent 4", "каналы для Agent 5"],
        "skills": ["поиск источников", "анализ конкурентов", "анализ отзывов", "поиск тендерного спроса"],
        "mcp_api": ["Browser Use позже", "Context7", "Firecrawl/Apify позже"],
        "todo": "Сделать первую source card для одного выбранного источника и передать её Agent 2.",
        "next_action": "Сделать первую source card для одного выбранного источника и передать её Agent 2.",
        "main_metric": {
            "name": "Покрытие карты источников",
            "current_value": 17,
            "target_value": 17,
            "unit": "каналов",
            "done_when": "все каналы системы есть в справочнике и имеют владельца",
        },
        "okr_metrics": [
            {"name": "Учтены все каналы системы", "current_value": 17, "target_value": 17, "unit": "каналов"},
            {"name": "Каналы первой волны разложены по агентам", "current_value": 9, "target_value": 9, "unit": "каналов"},
            {"name": "Planned-каналы из дашборда лектора учтены", "current_value": 8, "target_value": 8, "unit": "каналов"},
            {"name": "Конкурентные и рыночные источники в watchlist", "current_value": 15, "target_value": 15, "unit": "строк"},
            {"name": "Source cards первой волны готовы", "current_value": 0, "target_value": 9, "unit": "карточек"},
            {"name": "Личные каналы Яники заполнены", "current_value": 0, "target_value": 5, "unit": "ссылок"},
        ],
        "guard_metrics": [
            "0 источников переводятся в активный сбор без владельца, next_action и проверки риска",
            "0 неподтверждённых утверждений о конкурентах попадает в итоговые рекомендации",
        ],
    },
    "agent2_collector": {
        "title": "Agent 2 Collector",
        "department": "Сбор лидов",
        "panel_status": "partial",
        "description": "Забирает лиды из разрешённого источника и превращает их в сырые карточки.",
        "readiness_percent": 45,
        "okr": "Безопасно получить первый тестовый лид из одного источника и передать его на квалификацию.",
        "inputs": ["один разрешённый источник", "IMAP/tender email", "future marketplace signals"],
        "outputs": ["RawLead в Redis leads:raw"],
        "skills": ["разбор писем", "разметка источника", "нормализация данных"],
        "mcp_api": ["IMAP", "Redis", "Playwright/Apify позже"],
        "todo": "Провести один безопасный тест сбора из одного источника без массового парсинга.",
        "next_action": "Провести один безопасный тест сбора из одного источника без массового парсинга.",
        "main_metric": {
            "name": "Покрытие источников сбора Agent 2",
            "current_value": 1,
            "target_value": 4,
            "unit": "источников",
            "done_when": "по каждому источнику Agent 2 есть хотя бы один тестовый RawLead или ручной сигнал",
        },
        "okr_metrics": [
            {"name": "Источники сбора Agent 2 учтены", "current_value": 4, "target_value": 4, "unit": "каналов"},
            {"name": "Автоматизированный или проверенный сбор", "current_value": 1, "target_value": 4, "unit": "источников"},
            {"name": "Тестовые RawLead для покрытия Agent 2", "current_value": 1, "target_value": 4, "unit": "лидов"},
            {"name": "Месячный пилот сбора", "current_value": 0, "target_value": 20, "unit": "RawLead"},
            {"name": "Redis-передача RawLead доказана", "current_value": 1, "target_value": 1, "unit": "тест"},
        ],
        "guard_metrics": [
            "0 массовых сборов, парсингов и реальных площадок без отдельного подтверждения",
            "дубли должны отсекаться до передачи дальше; целевой порог дублей после фильтра — 0",
        ],
    },
    "agent3_processor": {
        "title": "Agent 3 Processor",
        "department": "Обработка и скоринг",
        "panel_status": "tested_partial",
        "description": "Очищает лид, понимает его смысл, ставит приоритет и предлагает следующий шаг.",
        "readiness_percent": 70,
        "okr": "Отделить сильные заявки от слабых и дать менеджеру понятное действие по каждому лиду.",
        "inputs": ["RawLead из Redis leads:raw"],
        "outputs": ["QualifiedLead в Redis leads:qualified"],
        "skills": ["очистка данных", "выделение сути", "скоринг лида", "подготовка оффера"],
        "mcp_api": ["Redis", "shared/llm_client.py", "OpenRouter/Anthropic/dry_run"],
        "todo": "Закрыть полный handoff: Agent 3 -> Agent 5 на одном тестовом лиде.",
        "next_action": "Закрыть полный handoff: Agent 3 -> Agent 5 на одном тестовом лиде.",
        "main_metric": {
            "name": "Обработанные тестовые лиды по первой волне",
            "current_value": 1,
            "target_value": 9,
            "unit": "лидов",
            "done_when": "по одному тестовому лиду из каждого wave_1 канала проходит score и next_action",
        },
        "okr_metrics": [
            {"name": "Сквозной тест лида обработан", "current_value": 1, "target_value": 1, "unit": "тест"},
            {"name": "Покрытие первой волны источников", "current_value": 1, "target_value": 9, "unit": "лидов"},
            {"name": "Режимы скоринга проверены", "current_value": 2, "target_value": 2, "unit": "режима"},
            {"name": "CRM-handoff проверен", "current_value": 1, "target_value": 1, "unit": "тест"},
            {"name": "Категории score проверены", "current_value": 1, "target_value": 4, "unit": "категорий"},
        ],
        "guard_metrics": [
            "ошибочные hot-лиды после появления реальной выборки — не выше 10%",
            "0 QualifiedLead без source, score_reason и recommended_action",
        ],
    },
    "agent4_publisher": {
        "title": "Agent 4 Publisher",
        "department": "Контент и доверие",
        "panel_status": "dry_run/manual",
        "description": "Готовит контент, который объясняет экспертизу студии и усиливает доверие.",
        "readiness_percent": 40,
        "okr": "Стабильно готовить черновики контента и материалы доверия без автопубликации.",
        "inputs": ["темы", "бренд", "контент-план", "approval человека"],
        "outputs": ["черновики", "dry-run материалы", "content:published позже"],
        "skills": ["копирайтинг", "SEO-темы", "визуальные промпты", "UTM-логика"],
        "mcp_api": ["shared/llm_client.py -> OpenRouter/Anthropic/dry_run", "imagegen/OpenAI image позже", "MAX/PostMyPost позже"],
        "todo": "Держать публикации в dry-run и позже связать контент-события с аналитикой Agent 5.",
        "next_action": "Держать публикации в dry-run и позже связать контент-события с аналитикой Agent 5.",
        "main_metric": {
            "name": "Контентные поверхности учтены",
            "current_value": 5,
            "target_value": 7,
            "unit": "поверхностей",
            "done_when": "MAX, Telegram, VK, Дзен, Яндекс Карты, 2GIS и сайт/блог учитываются отдельно",
        },
        "okr_metrics": [
            {"name": "Контентные поверхности учтены", "current_value": 5, "target_value": 7, "unit": "поверхностей"},
            {"name": "Черновики первой недели", "current_value": 0, "target_value": 5, "unit": "материалов"},
            {"name": "Ядро месячного плана", "current_value": 0, "target_value": 20, "unit": "тем"},
            {"name": "Полный адаптированный план после MVP", "current_value": 0, "target_value": 52, "unit": "материала"},
            {"name": "Поля согласования в шаблоне", "current_value": 3, "target_value": 3, "unit": "поля"},
        ],
        "guard_metrics": [
            "0 реальных публикаций без отдельного подтверждения Яники",
            "0 материалов с персональными данными или обещаниями без доказательств",
            "стоимость генерации должна быть заполнена у 100% материалов перед публикацией",
        ],
    },
    "agent5_crm": {
        "title": "Agent 5 CRM",
        "department": "CRM и аналитика",
        "panel_status": "tested",
        "description": "Создаёт лид в CRM, отправляет уведомление и считает результативность каналов.",
        "readiness_percent": 80,
        "okr": "Довести квалифицированный лид до CRM, уведомления и отчёта по результативности.",
        "inputs": ["QualifiedLead", "OutreachLead", "content:published"],
        "outputs": ["Bitrix24 лид", "Telegram alert", "CSV/ROMI отчёт"],
        "skills": ["Bitrix24", "воронка CRM", "сквозная аналитика", "отчёты"],
        "mcp_api": ["Bitrix24 REST", "Telegram Bot API", "CSV", "Supabase/Sheets позже"],
        "todo": "Закрыть один сквозной тест: квалифицированный лид -> Bitrix24 -> Telegram -> отчёт.",
        "next_action": "Закрыть один сквозной тест: квалифицированный лид -> Bitrix24 -> Telegram -> отчёт.",
        "main_metric": {
            "name": "Каналы в сквозной аналитике",
            "current_value": 17,
            "target_value": 17,
            "unit": "каналов",
            "done_when": "каждый канал есть в registry, costs, facts и итоговом channel_report",
        },
        "okr_metrics": [
            {"name": "Каналы в сквозной аналитике", "current_value": 17, "target_value": 17, "unit": "каналов"},
            {"name": "Каналы первой волны отслеживаются", "current_value": 9, "target_value": 9, "unit": "каналов"},
            {"name": "Сквозной CRM-тест закрыт", "current_value": 1, "target_value": 1, "unit": "тест"},
            {"name": "CRM-цепочка урока 5 покрыта", "current_value": 5, "target_value": 6, "unit": "шагов"},
            {"name": "Тестовые Bitrix24-создания", "current_value": 4, "target_value": 3, "unit": "теста"},
            {"name": "Метрика лектора CR visit->deal", "current_value": 0, "target_value": 1, "unit": "метрика"},
        ],
        "guard_metrics": [
            "0 секретов, webhook и token-значений в отчётах",
            "0 реальных клиентских данных в тестовых лидах",
            "доля лидов без source в реальной работе должна быть не выше 10%",
        ],
    },
    "agent6_outreach": {
        "title": "Agent 6 Outreach",
        "department": "Первое касание",
        "panel_status": "planned/locked",
        "description": "Готовит аккуратное первое касание, но не отправляет его без согласования человека.",
        "readiness_percent": 25,
        "okr": "Подготовить безопасный первый контакт по найденному диалогу, но отправлять только после одобрения.",
        "inputs": ["Telegram/VK/forum/MAX/TenChat/Yandex Q candidates", "approval человека"],
        "outputs": ["approved reply", "OutreachLead", "интерес в Agent 5"],
        "skills": ["поиск диалогов", "текст первого касания", "согласование", "продажный диалог"],
        "mcp_api": ["Telethon", "Telegram Bot API", "VK API позже", "MAX/TenChat позже"],
        "todo": "Сначала сделать approval-flow на черновике без реальной отправки сообщений.",
        "next_action": "Сначала сделать approval-flow на черновике без реальной отправки сообщений.",
        "main_metric": {
            "name": "Outreach-источники первой волны проверены",
            "current_value": 0,
            "target_value": 2,
            "unit": "источников",
            "done_when": "Telegram-чаты и outbound manual прошли ручной кандидат-тест без отправки спама",
        },
        "okr_metrics": [
            {"name": "Outreach-источники первой волны учтены", "current_value": 2, "target_value": 2, "unit": "источника"},
            {"name": "Кандидаты для ручной проверки", "current_value": 0, "target_value": 10, "unit": "кандидатов"},
            {"name": "Черновики первых ответов", "current_value": 0, "target_value": 5, "unit": "ответов"},
            {"name": "Outreach -> CRM тест", "current_value": 0, "target_value": 1, "unit": "тест"},
            {"name": "Реальные отправки до approval", "current_value": 0, "target_value": 0, "unit": "сообщений", "direction": "at_most"},
        ],
        "guard_metrics": [
            "0 сообщений без approval",
            "после разрешения пилотный лимит — не больше 5 отправок в день",
            "0 жалоб/спам-сигналов",
        ],
    },
}


AGENT_PATHS = {
    agent_id: PROJECT_ROOT / "agents" / agent_id / "__init__.py" for agent_id in AGENT_CONFIG
}

SUBROLE_CONFIG: dict[str, list[dict[str, str]]] = {
    "agent1_scout": [
        {"name": "Market Research Agent", "responsibility": "рыночный спрос, сегменты, темы", "artifact": "SignalCard", "kpi": "5+ полезных сигналов перед запуском нового источника"},
        {"name": "Competitor Analyst", "responsibility": "конкуренты, упаковка, доказательства", "artifact": "competitor_note", "kpi": "у каждого конкурента есть ссылка, сегмент, сильная сторона и risk_notes"},
        {"name": "Source Radar", "responsibility": "новые каналы лидов и контента", "artifact": "source_signal_card", "kpi": "100% новых источников имеют owner_agent и next_action"},
        {"name": "Reviews/Maps Monitor", "responsibility": "карты, отзывы, вопросы клиентов", "artifact": "review_signal", "kpi": "отзывы превращаются в боли, FAQ и темы, без копирования"},
        {"name": "Demand Signal Curator", "responsibility": "отбор сигналов и handoff", "artifact": "handoff_recommendation", "kpi": "100% SignalCard имеют recommended_action, handoff_to, risk_notes"},
    ],
    "agent2_collector": [
        {"name": "Tender/Email Collector", "responsibility": "почта и тендерные письма", "artifact": "raw_lead", "kpi": "RawLead создаётся без потери source и raw_text"},
        {"name": "Marketplace Collector", "responsibility": "Avito, Profi, Яндекс Услуги позже", "artifact": "marketplace_raw_lead", "kpi": "один источник за раз, не все платформы сразу"},
        {"name": "Directory Collector", "responsibility": "карты и каталоги позже", "artifact": "directory_signal", "kpi": "только разрешённые публичные сигналы"},
        {"name": "Lead Normalizer", "responsibility": "единый формат RawLead", "artifact": "normalized_raw_lead", "kpi": "100% RawLead имеют source, flow, raw_text, created_at"},
        {"name": "Duplicate Guard", "responsibility": "дубли до передачи дальше", "artifact": "duplicate_decision", "kpi": "явные дубли не уходят в Agent 3"},
    ],
    "agent3_processor": [
        {"name": "Cleaner", "responsibility": "шум, мусор, оффтопик", "artifact": "clean_lead", "kpi": "оффтопик не попадает в CRM"},
        {"name": "Enricher", "responsibility": "город, объект, площадь, контакт", "artifact": "lead_enrichment", "kpi": "доступные поля извлекаются из текста"},
        {"name": "Scorer", "responsibility": "hot/warm/cold/off", "artifact": "score_result", "kpi": "каждый score имеет score_reason"},
        {"name": "Offer/Next-Step Architect", "responsibility": "оффер и следующий шаг", "artifact": "qualified_lead", "kpi": "каждый QualifiedLead имеет recommended_action"},
        {"name": "QA Classifier", "responsibility": "проверка завышенного score", "artifact": "processor_quality_note", "kpi": "после выборки ошибочные hot-лиды не выше 10%"},
    ],
    "agent4_publisher": [
        {"name": "Content Strategist", "responsibility": "рубрика, формат, этап воронки", "artifact": "content_brief", "kpi": "у каждого материала есть формат, воронка и канал"},
        {"name": "Copywriter", "responsibility": "черновик в стиле СИЛА Проекта", "artifact": "content_draft", "kpi": "посты не повторяют одну структуру подряд"},
        {"name": "Editor", "responsibility": "стиль, доказательства, запреты", "artifact": "editor_check", "kpi": "0 неподтверждённых обещаний и общих рекламных фраз"},
        {"name": "Visual/Media Brief Creator", "responsibility": "ТЗ на визуал, анимацию, видео позже", "artifact": "media_brief", "kpi": "медиа только как ТЗ или dry-run до approval"},
        {"name": "Approval Coordinator", "responsibility": "согласование и правки", "artifact": "approval_card", "kpi": "100% материалов имеют статус, стоимость, причину перегенерации при правках"},
        {"name": "Content Metrics Analyst", "responsibility": "связь постов с метриками и лидами позже", "artifact": "content_metric_event", "kpi": "каждый опубликованный материал позже получает content_metric_event"},
    ],
    "agent5_crm": [
        {"name": "CRM Router", "responsibility": "Bitrix24 payload для лида/сделки", "artifact": "crm_payload_preview", "kpi": "payload создаётся локально до реальной отправки"},
        {"name": "Notifier", "responsibility": "уведомление человека", "artifact": "notification_event", "kpi": "уведомления без секретов и лишних персональных данных"},
        {"name": "Attribution Agent", "responsibility": "first_touch, last_touch, канал, UTM", "artifact": "attribution_record", "kpi": "100% тестовых лидов имеют first_touch_channel и last_touch_channel"},
        {"name": "ROMI Reporter", "responsibility": "CPL, CAC, profit, ROMI", "artifact": "channel_report", "kpi": "spend -> leads -> deals -> revenue -> profit -> ROMI"},
        {"name": "CRM Hygiene Analyst", "responsibility": "дубли, пустые поля, слабые карточки", "artifact": "crm_hygiene_report", "kpi": "дубли и пустые поля попадают в очередь ручной чистки"},
        {"name": "Weekly Digest Owner", "responsibility": "недельный итог системы позже", "artifact": "weekly_digest", "kpi": "лиды, CRM, контент, ROMI и блокеры раз в неделю"},
    ],
    "agent6_outreach": [
        {"name": "Social Listening Monitor", "responsibility": "релевантные обсуждения", "artifact": "outreach_candidate", "kpi": "кандидат не создаётся без URL/контекста и причины релевантности"},
        {"name": "Candidate Qualifier", "responsibility": "риск спама и релевантность", "artifact": "outreach_decision", "kpi": "спорные кандидаты идут в escalation-to-yana"},
        {"name": "Reply Draft Writer", "responsibility": "человеческий ответ", "artifact": "reply_draft", "kpi": "ответ полезный, не спамный, без давления"},
        {"name": "Approval Gatekeeper", "responsibility": "запрет отправки без человека", "artifact": "approval_required", "kpi": "0 реальных отправок без approval"},
        {"name": "Outreach Sender", "responsibility": "отправка после approval", "artifact": "sent_outreach_event", "kpi": "после разрешения не больше 5 отправок в день на пилоте"},
        {"name": "Dialog Converter", "responsibility": "интерес -> OutreachLead", "artifact": "outreach_lead", "kpi": "заинтересованный ответ уходит в Agent 5"},
    ],
}

SCENARIO_ARTIFACT_CONTRACT: dict[str, Any] = {
    "status": "read_only/local_contract",
    "source_doc": "docs/agent-scenario-artifact-contract.md",
    "subroles_doc": "docs/agent-subroles-and-kpi-map.md",
    "rule": "каждый этап закрыт только если есть вход, выход, статус, next_step и проверяемый артефакт",
    "statuses": [
        "locked",
        "manual",
        "draft",
        "approval_ready",
        "approved",
        "queued",
        "running",
        "needs_review",
        "failed",
        "done",
        "published_manual_unverified_public",
    ],
    "scenarios": [
        {
            "name": "Первый входящий запрос",
            "timeline": ["site/MAX/Telegram/email", "intake_card", "Agent 3", "Agent 5", "crm_payload_preview", "human_next_step"],
            "required_artifacts": ["intake_card", "qualified_lead", "crm_payload_preview", "human_next_step"],
            "mvp_status": "OK_LOCAL_DRY_RUN_READY_FOR_MANUAL_REVIEW",
        },
        {
            "name": "Контент даёт лид",
            "timeline": ["SignalCard", "content_brief", "content_draft", "approval_card", "content_metric_event", "Agent 5 analytics"],
            "required_artifacts": ["SignalCard", "content_brief", "content_draft", "approval_card", "content_metric_event"],
            "mvp_status": "draft/manual",
        },
        {
            "name": "Тендерный лид",
            "timeline": ["Gmail/IMAP tender", "Agent 2", "raw_lead", "Agent 3", "qualified_lead", "Agent 5", "Bitrix24/human"],
            "required_artifacts": ["raw_lead", "normalized_raw_lead", "qualified_lead", "crm_payload_preview"],
            "mvp_status": "partial_tested",
        },
        {
            "name": "ROMI канала",
            "timeline": ["source", "cost", "lead", "deal", "revenue", "profit", "ROMI", "channel_decision"],
            "required_artifacts": ["channel_registry_row", "channel_cost_row", "channel_fact_row", "channel_report", "channel_decision"],
            "mvp_status": "csv_mvp_exists",
        },
    ],
    "forbidden_actions": [
        "не создавать Agent 7",
        "не запускать scheduler без отдельного подтверждения",
        "не запускать массовый сбор",
        "не публиковать и не отправлять outreach без approval",
        "не показывать секреты",
    ],
}

DEPARTMENT_VIEW: list[dict[str, str]] = [
    {
        "department_id": "orchestrator",
        "title": "Оркестратор",
        "owner": "CLAUDE.md / AGENTS.md / REPORT.md",
        "status": "active",
        "purpose": "держит правила, память проекта, запреты и следующий маленький шаг",
    },
    {
        "department_id": "research",
        "title": "Исследование источников",
        "owner": "Agent 1 Scout",
        "status": "planned/manual",
        "purpose": "находит источники, боли рынка, конкурентов и передает source cards",
    },
    {
        "department_id": "lead_collection",
        "title": "Сбор лидов",
        "owner": "Agent 2 Collector",
        "status": "partial",
        "purpose": "создает RawLead и передает его в leads:raw",
    },
    {
        "department_id": "qualification",
        "title": "Квалификация",
        "owner": "Agent 3 Processor",
        "status": "tested_partial",
        "purpose": "делает flow, enrich, score, offer и QualifiedLead",
    },
    {
        "department_id": "content_trust",
        "title": "Контент и доверие",
        "owner": "Agent 4 Publisher",
        "status": "dry_run/manual",
        "purpose": "готовит черновики, доверие, сайт и future content events",
    },
    {
        "department_id": "crm_analytics",
        "title": "CRM и аналитика",
        "owner": "Agent 5 CRM",
        "status": "tested",
        "purpose": "принимает QualifiedLead/OutreachLead/content events и ведет CRM/отчеты",
    },
    {
        "department_id": "outreach",
        "title": "Первое касание",
        "owner": "Agent 6 Outreach",
        "status": "planned/locked",
        "purpose": "готовит human-like replies только через approval",
    },
    {
        "department_id": "checker",
        "title": "Checker / QA",
        "owner": "scripts/check_agent_okr_contract.py",
        "status": "active",
        "purpose": "сверяет визуальную систему с реальными файлами, OKR, метриками и отчетами",
    },
]

OPERATING_FLOW: list[dict[str, str]] = [
    {
        "step": "1",
        "title": "Источник",
        "owner": "Agent 1 / Agent 2",
        "result": "source card или RawLead",
    },
    {
        "step": "2",
        "title": "Квалификация",
        "owner": "Agent 3",
        "result": "QualifiedLead: flow, score, offer, next action",
    },
    {
        "step": "3",
        "title": "CRM",
        "owner": "Agent 5",
        "result": "Bitrix24 lead, Telegram alert, analytics event",
    },
    {
        "step": "4",
        "title": "Контент/доверие",
        "owner": "Agent 4",
        "result": "drafts, site trust blocks, future content:published",
    },
    {
        "step": "5",
        "title": "Проверка",
        "owner": "Checker",
        "result": "JSON report + запись в REPORT.md",
    },
]

HANDOFF_VIEW: list[dict[str, str]] = [
    {
        "from": "Agent 1 Scout",
        "to": "Agent 2 Collector",
        "payload": "source card для сбора",
        "format": "future research/table",
        "storage": "research/* или content/library/sources/*",
        "checked_by": "REPORT.md + checker по мере появления source cards",
    },
    {
        "from": "Agent 1 Scout",
        "to": "Agent 4 Publisher",
        "payload": "боли, темы, конкуренты",
        "format": "Markdown/CSV source notes",
        "storage": "content/library/sources/*, research/*",
        "checked_by": "docs/multi-agent-visual-control-map.md",
    },
    {
        "from": "Agent 2 Collector",
        "to": "Agent 3 Processor",
        "payload": "RawLead",
        "format": "shared.models.RawLead",
        "storage": "Redis leads:raw",
        "checked_by": "scripts/test_agent3_redis_processing_llm.py",
    },
    {
        "from": "Agent 3 Processor",
        "to": "Agent 5 CRM",
        "payload": "QualifiedLead",
        "format": "shared.models.QualifiedLead",
        "storage": "Redis leads:qualified",
        "checked_by": "scripts/test_agent3_to_agent5_handoff_local.py",
    },
    {
        "from": "Agent 4 Publisher",
        "to": "Agent 5 CRM",
        "payload": "content_published event",
        "format": "JSON event",
        "storage": "Redis content:published",
        "checked_by": "future content event test",
    },
    {
        "from": "Agent 6 Outreach",
        "to": "Agent 5 CRM",
        "payload": "OutreachLead после интереса",
        "format": "shared.models.OutreachLead -> QualifiedLead",
        "storage": "Redis leads:outreach",
        "checked_by": "future approval/outreach test",
    },
]

INTERACTION_ROUTES: list[dict[str, Any]] = [
    {
        "route_id": "lead_flow",
        "title": "Основной поток лида",
        "status": "partly_tested",
        "nodes": [
            "Agent 1 Scout",
            "Agent 2 Collector",
            "Redis leads:raw",
            "Agent 3 Processor",
            "Redis leads:qualified",
            "Agent 5 CRM",
            "Bitrix24 / Telegram / отчёт",
        ],
        "payload": "source card -> RawLead -> QualifiedLead -> CRM record",
        "safe_note": "Полный runtime с настоящим LLM и Agent 5 пока запускать только отдельным контролируемым тестом.",
    },
    {
        "route_id": "content_flow",
        "title": "Контентный поток",
        "status": "dry_run/manual",
        "nodes": [
            "Agent 1 Scout",
            "Agent 4 Publisher",
            "content:published",
            "Agent 5 CRM",
            "ROMI / канал-отчёт",
        ],
        "payload": "боли рынка -> черновик/публикация -> событие контента -> аналитика канала",
        "safe_note": "Реальные публикации заблокированы без отдельного подтверждения.",
    },
    {
        "route_id": "outreach_flow",
        "title": "Outreach поток",
        "status": "planned/locked",
        "nodes": [
            "Agent 6 Outreach",
            "approval человека",
            "leads:outreach",
            "Agent 5 CRM",
            "Bitrix24 / следующий шаг",
        ],
        "payload": "кандидат -> одобренный ответ -> заинтересованный диалог -> CRM",
        "safe_note": "Отправка сообщений и real outreach заблокированы.",
    },
    {
        "route_id": "checker_flow",
        "title": "Контрольный поток",
        "status": "active/read_only",
        "nodes": [
            "REPORT.md",
            "6 agent files",
            "scripts/check_agent_okr_contract.py",
            "agent_dashboard.json",
            "agent_dashboard.html",
        ],
        "payload": "факты из файлов -> checker report -> визуальная панель",
        "safe_note": "Checker только читает локальные файлы и пишет локальный JSON-отчёт.",
    },
]

MANAGEMENT_PROTOCOL: dict[str, Any] = {
    "protocol_status": "read_only/planned_runtime_later",
    "title": "Chief of Staff / Handoff / Escalation / Weekly digest",
    "source_doc": "docs/chief-of-staff-handoff-protocol.md",
    "rule": "агент = роль / ответственность; skill = действие внутри роли",
    "chief_of_staff": {
        "owner": "CLAUDE.md / AGENTS.md / REPORT.md",
        "meaning": "режим координации, а не Agent 7",
        "responsibility": "принять задачу, восстановить контекст, выбрать маршрут, проверить результат и обновить память",
    },
    "nervous_system": [
        "вход задачи",
        "маршрутизация",
        "агенты",
        "QA/checker",
        "результат",
        "память",
    ],
    "templates": [
        {
            "name": "task-handoff",
            "purpose": "передать задачу от слоя/агента к следующему владельцу",
            "fields": ["от кого", "кому", "цель", "контекст", "формат результата", "риски", "нужна ли Яника"],
        },
        {
            "name": "agent-result",
            "purpose": "вернуть итог работы агента в едином формате",
            "fields": ["что сделано", "что проверено", "статус", "отчёты", "риски", "следующий шаг"],
        },
        {
            "name": "escalation-to-yana",
            "purpose": "остановиться и вынести решение человеку",
            "fields": ["ситуация", "вариант 1", "плюсы/минусы", "вариант 2", "рекомендация", "что решить Янике"],
        },
        {
            "name": "weekly digest",
            "purpose": "будущий недельный итог Agent 5/dashboard",
            "fields": ["фокус недели", "что сделано", "лиды и CRM", "контент", "ROMI", "блокеры", "план"],
        },
    ],
    "escalation_rules": [
        "платный API или рост бюджета",
        "реальная публикация",
        "массовый сбор лидов",
        "реальная outreach-отправка",
        "изменение CRM-логики",
        "персональные данные или юридические обещания",
    ],
    "weekly_digest_owner": "Agent 5 CRM/Analytics + dashboard reports позже",
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

MAS_REFERENCE_LAYER: dict[str, Any] = {
    "status": "read_only/spec_only",
    "title": "MAS reference layer from 193.233.131.92",
    "source_doc": "research/external-mas-ip-analysis-2026-05-15.md",
    "reference_url": "http://193.233.131.92/",
    "model_summary": (
        "Внешняя модель описывает операционный центр: входящая задача -> Chief Orchestrator "
        "-> департамент -> профильный агент -> сценарий выполнения -> артефакт -> контроль качества -> следующий шаг."
    ),
    "application_rule": "берём принципы управления, но не расширяем систему: остаются 6 агентов + checker, не Agent 7",
    "adopted_blocks": [
        {
            "name": "Agent Inspector",
            "meaning": "карточка выбранного агента: роль, входы, выходы, правила, KPI, файлы, блокеры",
            "where": "правая панель dashboard",
            "mvp_status": "planned",
        },
        {
            "name": "Scenario Timeline",
            "meaning": "путь задачи по шагам, чтобы видеть где она находится",
            "where": "нижняя timeline-панель",
            "mvp_status": "planned",
        },
        {
            "name": "Artifact Tracker",
            "meaning": "каждый этап закрывается только проверяемым артефактом",
            "where": "детали сценария и event stream",
            "mvp_status": "planned",
        },
        {
            "name": "Status model",
            "meaning": "единые статусы: locked/manual/ready/queued/running/needs_review/failed/done",
            "where": "карта агентов, event stream, детали агента",
            "mvp_status": "planned",
        },
        {
            "name": "OSINT protocol",
            "meaning": "проверка фактов и рисков по открытым источникам",
            "where": "Agent 1 Scout и Agent 5 CRM, без нового агента",
            "mvp_status": "future_safe_protocol",
        },
        {
            "name": "AI Operator Chat",
            "meaning": "чат понимает, какой агент выбран оператором",
            "where": "future-layer после read-only dashboard",
            "mvp_status": "later_locked",
        },
    ],
    "scenario_timelines": [
        {
            "name": "Первый входящий запрос",
            "steps": ["сайт/MAX/Telegram/email", "AI-менеджер", "Agent 3", "Agent 5", "Bitrix24 сделка", "человек"],
            "artifact": "intake_card + bitrix_deal",
        },
        {
            "name": "Тендерный лид",
            "steps": ["Gmail tender", "Agent 2", "Agent 3", "Agent 5", "Bitrix24", "analytics"],
            "artifact": "raw_lead + qualified_lead + crm_event",
        },
        {
            "name": "Контентный сигнал",
            "steps": ["Agent 1 Scout", "Agent 4 Publisher", "content event", "Agent 5", "ROMI later"],
            "artifact": "source_signal_card + content_draft/content_event",
        },
        {
            "name": "CRM hygiene",
            "steps": ["Bitrix24 audit", "Agent 5", "duplicate queue", "human cleanup"],
            "artifact": "crm_hygiene_report",
        },
        {
            "name": "ROMI",
            "steps": ["source", "lead", "deal", "revenue", "channel", "profit", "ROMI"],
            "artifact": "channel_report / romi_report",
        },
    ],
    "required_artifacts": [
        {"stage": "Agent 1 Scout", "artifact": "source_signal_card"},
        {"stage": "Agent 2 Collector", "artifact": "raw_lead"},
        {"stage": "Agent 3 Processor", "artifact": "qualified_lead"},
        {"stage": "AI-менеджер", "artifact": "intake_card"},
        {"stage": "Agent 4 Publisher", "artifact": "content_draft или published_content_event"},
        {"stage": "Agent 5 CRM", "artifact": "bitrix_deal или crm_hygiene_report"},
        {"stage": "Agent 5 Analytics", "artifact": "channel_report или romi_report"},
        {"stage": "Agent 6 Outreach", "artifact": "approved_reply или outreach_lead"},
        {"stage": "Checker", "artifact": "agent_okr_contract_check.json"},
    ],
    "statuses": ["locked", "manual", "ready", "queued", "running", "needs_review", "failed", "done"],
    "osint_rules": [
        "важный факт подтверждать 2-3 источниками",
        "хранить URL, дату проверки и уровень доверия",
        "не использовать серые методы, взлом, утечки и закрытые персональные данные",
        "не принимать автоматическое решение по крупной сделке без человека",
        "для крупной сделки отдавать человеку короткий risk-summary",
    ],
    "later_locks": [
        "AI Operator Chat не запускать до правил доступа и контроля стоимости LLM",
        "POST /api/chat и /api/chat/audio внешнего референса не тестировать без отдельного решения",
        "OSINT/MCP-интеграции не подключать до первого MVP и preflight",
    ],
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


SAFE_STATUS_KEYS = {
    "test_type",
    "config_status",
    "agent_contract_status",
    "visual_map_status",
    "admin_dashboard_spec_status",
    "dashboard_build_status",
    "report_write_status",
    "canonical_test_status",
    "redis_ping_status",
    "queue_guard_status",
    "redis_push_raw_status",
    "agent3_run_status",
    "agent5_run_status",
    "qualified_output_status",
    "bitrix_send_status",
    "telegram_send_status",
    "cleanup_status",
    "llm_config_status",
    "llm_score_status",
    "llm_offer_status",
    "anthropic_api_key_status",
    "openrouter_api_key_status",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except json.JSONDecodeError as exc:
        return {"read_status": "FAILED_JSON_DECODE", "error": str(exc)}


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return [
            {key: (value or "").strip() for key, value in row.items()}
            for row in csv.DictReader(file)
            if any((value or "").strip() for value in row.values())
        ]


def _relative(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def _count_by(rows: list[dict[str, str]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = row.get(key, "нет данных") or "нет данных"
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def _simplify_channel(row: dict[str, str]) -> dict[str, str]:
    return {
        "channel_id": row.get("channel_id", ""),
        "channel_name": row.get("channel_name", ""),
        "status": row.get("status", ""),
        "priority_wave": row.get("priority_wave", ""),
        "source_type": row.get("source_type", ""),
        "traffic_channel": row.get("traffic_channel", ""),
        "utm_source": row.get("utm_source", ""),
        "utm_medium": row.get("utm_medium", ""),
        "first_touch": row.get("default_first_touch_channel", ""),
        "last_touch": row.get("default_last_touch_channel", ""),
        "owner_agent": row.get("owner_agent", ""),
        "flow": row.get("flow", ""),
        "notes": row.get("notes", ""),
    }


def _simplify_watch_source(row: dict[str, str]) -> dict[str, str]:
    return {
        "source_id": row.get("source_id", ""),
        "source_name": row.get("source_name", ""),
        "source_url": row.get("source_url", ""),
        "platform": row.get("platform", ""),
        "segment": row.get("segment", ""),
        "source_type": row.get("source_type", ""),
        "owner_agent": row.get("owner_agent", ""),
        "status": row.get("status", ""),
        "why_watch": row.get("why_watch", ""),
    }


def _channels_for_owner(rows: list[dict[str, str]], owner_agent: str) -> list[dict[str, str]]:
    return [_simplify_channel(row) for row in rows if row.get("owner_agent") == owner_agent]


def _agent_source_scope(
    agent_id: str,
    *,
    registry_rows: list[dict[str, str]],
    competitor_rows: list[dict[str, str]],
    yanika_rows: list[dict[str, str]],
) -> dict[str, Any]:
    canonical = [_simplify_channel(row) for row in registry_rows]
    wave_1 = [channel for channel in canonical if channel["priority_wave"] == "wave_1"]
    owned = _channels_for_owner(registry_rows, agent_id)
    watchlist = [
        _simplify_watch_source(row)
        for row in competitor_rows
        if row.get("owner_agent") == agent_id
    ]
    yanika_pending = [
        _simplify_watch_source(row)
        for row in yanika_rows
        if row.get("owner_agent") == agent_id
    ]

    if agent_id == "agent1_scout":
        return {
            "summary": AGENT_SOURCE_NOTES[agent_id],
            "primary_sources": canonical,
            "source_count": len(canonical),
            "watchlist_sources": watchlist,
            "watchlist_count": len(watchlist),
            "yanika_pending_sources": yanika_pending,
            "yanika_pending_count": len(yanika_pending),
            "backlog_sources": BACKLOG_SOURCES,
        }

    if agent_id == "agent3_processor":
        return {
            "summary": AGENT_SOURCE_NOTES[agent_id],
            "primary_sources": wave_1,
            "source_count": len(wave_1),
            "watchlist_sources": [],
            "watchlist_count": 0,
            "yanika_pending_sources": [],
            "yanika_pending_count": 0,
            "backlog_sources": ["после MVP обработка всех 17 каналов, а не только wave_1"],
        }

    if agent_id == "agent4_publisher":
        return {
            "summary": AGENT_SOURCE_NOTES[agent_id],
            "primary_sources": owned,
            "source_count": len(owned),
            "content_surfaces": CONTENT_SURFACES,
            "content_surface_count": len(CONTENT_SURFACES),
            "watchlist_sources": watchlist,
            "watchlist_count": len(watchlist),
            "yanika_pending_sources": [],
            "yanika_pending_count": 0,
            "backlog_sources": [
                "новый сайт / SEO-страницы",
                "лид-магнит ПРОВЕРКА",
                "GEO/AI visibility",
                "Reels/shorts radar",
                "ROMI по контенту",
            ],
        }

    if agent_id == "agent5_crm":
        return {
            "summary": AGENT_SOURCE_NOTES[agent_id],
            "primary_sources": canonical,
            "source_count": len(canonical),
            "direct_owner_sources": owned,
            "direct_owner_count": len(owned),
            "watchlist_sources": [],
            "watchlist_count": 0,
            "yanika_pending_sources": [],
            "yanika_pending_count": 0,
            "backlog_sources": ["visit_count", "visitor_id", "CR visit->deal", "ROMI по контенту"],
        }

    return {
        "summary": AGENT_SOURCE_NOTES.get(agent_id, "нет данных"),
        "primary_sources": owned,
        "source_count": len(owned),
        "watchlist_sources": watchlist,
        "watchlist_count": len(watchlist),
        "yanika_pending_sources": yanika_pending,
        "yanika_pending_count": len(yanika_pending),
        "backlog_sources": [],
    }


def _source_map() -> dict[str, Any]:
    registry_rows = _read_csv_rows(CHANNEL_REGISTRY_PATH)
    competitor_rows = _read_csv_rows(COMPETITOR_WATCHLIST_PATH)
    yanika_rows = _read_csv_rows(YANIKA_KNOWN_CHANNELS_PATH)
    lecture_growth_rows = _read_csv_rows(LECTURE_GROWTH_SOURCE_MAP_PATH)
    lecture_growth_score = _read_json(LECTURE_GROWTH_SOURCE_SCORE_PATH)
    if not isinstance(lecture_growth_score, dict):
        lecture_growth_score = {}
    canonical = [_simplify_channel(row) for row in registry_rows]
    wave_1 = [channel for channel in canonical if channel["priority_wave"] == "wave_1"]
    planned = [channel for channel in canonical if channel["status"] == "planned"]
    by_owner = {
        agent_id: _channels_for_owner(registry_rows, agent_id)
        for agent_id in AGENT_CONFIG
    }

    return {
        "source_map_status": "OK" if registry_rows else "MISSING_REGISTRY",
        "registry_file": _relative(CHANNEL_REGISTRY_PATH),
        "competitor_watchlist_file": _relative(COMPETITOR_WATCHLIST_PATH),
        "yanika_channels_file": _relative(YANIKA_KNOWN_CHANNELS_PATH),
        "summary": {
            "canonical_mvp_channels": len(canonical),
            "wave_1_channels": len(wave_1),
            "wave_2_channels": sum(1 for channel in canonical if channel["priority_wave"] == "wave_2"),
            "wave_3_channels": sum(1 for channel in canonical if channel["priority_wave"] == "wave_3"),
            "active_channels": sum(1 for channel in canonical if channel["status"] == "active"),
            "manual_channels": sum(1 for channel in canonical if channel["status"] == "manual"),
            "planned_channels": len(planned),
            "competitor_watchlist_sources": len(competitor_rows),
            "lecture_growth_sources": len(lecture_growth_rows),
            "yanika_pending_sources": len(yanika_rows),
            "content_surfaces": len(CONTENT_SURFACES),
            "backlog_sources": len(BACKLOG_SOURCES),
        },
        "counts_by_owner": _count_by(registry_rows, "owner_agent"),
        "counts_by_wave": _count_by(registry_rows, "priority_wave"),
        "counts_by_status": _count_by(registry_rows, "status"),
        "canonical_channels": canonical,
        "first_wave_channels": wave_1,
        "planned_channels": planned,
        "channels_by_owner": by_owner,
        "content_surfaces": CONTENT_SURFACES,
        "competitor_watchlist": [_simplify_watch_source(row) for row in competitor_rows],
        "lecture_growth_source_map_file": _relative(LECTURE_GROWTH_SOURCE_MAP_PATH),
        "lecture_growth_source_map": [_simplify_watch_source(row) for row in lecture_growth_rows],
        "lecture_growth_score_report": _relative(LECTURE_GROWTH_SOURCE_SCORE_PATH),
        "lecture_growth_score_status": lecture_growth_score.get("status", "MISSING_SCORE"),
        "lecture_growth_score_summary": lecture_growth_score.get("summary", {}),
        "yanika_pending_channels": [_simplify_watch_source(row) for row in yanika_rows],
        "backlog_sources": BACKLOG_SOURCES,
    }


def _bitrix_crm_hygiene() -> dict[str, Any]:
    audit = _read_json(BITRIX_AUDIT_PATH)
    if not audit:
        return {
            "status": "MISSING_AUDIT",
            "report_file": _relative(BITRIX_AUDIT_PATH),
            "next_action": "запустить .venv/bin/python scripts/audit_bitrix_readonly.py",
            "external_calls": {"bitrix24": False},
        }

    counts = audit.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    quality = audit.get("quality_flags")
    if not isinstance(quality, dict):
        quality = {}
    duplicates = audit.get("duplicates")
    if not isinstance(duplicates, dict):
        duplicates = {}

    contact_phone = duplicates.get("contacts_by_phone") if isinstance(duplicates.get("contacts_by_phone"), list) else []
    contact_email = duplicates.get("contacts_by_email") if isinstance(duplicates.get("contacts_by_email"), list) else []
    contact_name = duplicates.get("contacts_by_name_hash") if isinstance(duplicates.get("contacts_by_name_hash"), list) else []
    lead_phone = duplicates.get("leads_by_phone") if isinstance(duplicates.get("leads_by_phone"), list) else []
    lead_email = duplicates.get("leads_by_email") if isinstance(duplicates.get("leads_by_email"), list) else []

    duplicate_group_count = len(contact_phone) + len(contact_email) + len(lead_phone) + len(lead_email)
    empty_contacts = int(quality.get("contacts_without_phone_or_email") or 0)
    empty_leads = int(quality.get("leads_without_phone_or_email") or 0)
    active_leads = int(counts.get("leads_active") or 0)

    limited_by_pages = bool(audit.get("limited_by_pages"))
    if limited_by_pages:
        status = "LIMITED_AUDIT"
    elif duplicate_group_count or empty_contacts or empty_leads:
        status = "NEEDS_CLEANUP"
    else:
        status = "OK"

    return {
        "status": status,
        "report_file": _relative(BITRIX_AUDIT_PATH),
        "generated_at": audit.get("generated_at", "нет данных"),
        "readonly": audit.get("readonly", True),
        "limited_by_pages": limited_by_pages,
        "counts": {
            "contacts": counts.get("contacts", 0),
            "leads_total": counts.get("leads_total", 0),
            "leads_active": active_leads,
            "deals_total": counts.get("deals_total", 0),
            "statuses": counts.get("statuses", 0),
            "sources": counts.get("sources", 0),
        },
        "quality_flags": {
            "leads_without_source": quality.get("leads_without_source", 0),
            "leads_without_phone_or_email": empty_leads,
            "contacts_without_phone_or_email": empty_contacts,
        },
        "duplicate_groups": {
            "contacts_by_phone": len(contact_phone),
            "contacts_by_email": len(contact_email),
            "contacts_by_name_hash": len(contact_name),
            "leads_by_phone": len(lead_phone),
            "leads_by_email": len(lead_email),
            "strong_groups_to_review_first": len(contact_phone) + len(contact_email),
            "total_phone_email_groups": duplicate_group_count,
        },
        "lead_statuses": audit.get("lead_statuses", []),
        "lead_sources": audit.get("lead_sources", []),
        "deal_stages": audit.get("deal_stages", []),
        "first_cleanup_queue": [
            "контакты-дубли по телефону",
            "контакты-дубли по обычному email",
            "лиды-дубли по телефону",
            "контакты без телефона/email, у которых нет сделок",
            "расшифровать стадии сделок UC_*",
        ],
        "safety_note": "Только локальный отчёт; dashboard не вызывает Bitrix24 и не объединяет записи. Если limited_by_pages=true, это не вся CRM.",
        "external_calls": {"bitrix24": False},
    }


def _vpp_ai_manager_dry_run() -> dict[str, Any]:
    report = _read_json(VPP_AI_MANAGER_DRY_RUN_PATH)
    if not report:
        return {
            "status": "MISSING_DRY_RUN",
            "report_file": _relative(VPP_AI_MANAGER_DRY_RUN_PATH),
            "next_action": ".venv/bin/python scripts/dry_run_vpp_ai_manager.py",
            "external_calls": {
                "redis": False,
                "bitrix24": False,
                "telegram_send": False,
                "max_send": False,
                "imap": False,
                "llm": False,
                "scheduler": False,
                "publisher": False,
                "ads": False,
            },
        }

    scenarios = report.get("scenarios", [])
    if not isinstance(scenarios, list):
        scenarios = []

    scenario_rows: list[dict[str, Any]] = []
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            continue
        source_card = scenario.get("source_card", {})
        intake_card = scenario.get("intake_card", {})
        qualified = scenario.get("qualified_lead", {})
        manager = scenario.get("vpp_ai_manager", {})
        deal = scenario.get("bitrix_deal_preview", {})
        if not isinstance(source_card, dict):
            source_card = {}
        if not isinstance(intake_card, dict):
            intake_card = {}
        if not isinstance(qualified, dict):
            qualified = {}
        if not isinstance(manager, dict):
            manager = {}
        if not isinstance(deal, dict):
            deal = {}

        scenario_rows.append(
            {
                "scenario_id": scenario.get("scenario_id", "нет данных"),
                "title": scenario.get("scenario_title", "нет данных"),
                "segment": manager.get("segment", "нет данных"),
                "flow": qualified.get("flow", "нет данных"),
                "score": qualified.get("score", "нет данных"),
                "client_type": manager.get("client_type", "нет данных"),
                "data_completeness": manager.get("data_completeness", "нет данных"),
                "missing_data": manager.get("missing_data", []),
                "next_action": manager.get("next_action", "нет данных"),
                "kp_24h_allowed": manager.get("kp_24h_allowed", False),
                "human_control_required": manager.get("human_control_required", True),
                "source": source_card.get("source", qualified.get("source", "нет данных")),
                "first_touch_channel": source_card.get("first_touch_channel", qualified.get("first_touch_channel", "нет данных")),
                "landing_page": source_card.get("landing_page", qualified.get("landing_page", "нет данных")),
                "bitrix_send_status": deal.get("send_status", "нет данных"),
                "first_reply": intake_card.get("first_reply", "нет данных"),
                "artifact_file": f"data/reports/vpp_ai_manager_dry_run/{scenario.get('scenario_id', 'unknown')}.json",
            }
        )

    enough_for_kp = sum(1 for item in scenario_rows if item.get("data_completeness") == "enough_for_kp")
    missing_data_total = sum(
        len(item.get("missing_data", []))
        for item in scenario_rows
        if isinstance(item.get("missing_data"), list)
    )
    scenario_count = int(report.get("scenario_count") or len(scenario_rows))
    status = "READY" if report.get("dry_run") is True and scenario_count >= 3 and scenario_rows else "NEEDS_REVIEW"

    return {
        "status": status,
        "test_type": report.get("test_type", "vpp_ai_manager_dry_run"),
        "dry_run": bool(report.get("dry_run")),
        "created_at": report.get("created_at", "нет данных"),
        "scenario_count": scenario_count,
        "summary": {
            "scenarios_ready": len(scenario_rows),
            "enough_for_kp": enough_for_kp,
            "need_missing_data": max(0, len(scenario_rows) - enough_for_kp),
            "missing_data_total": missing_data_total,
            "bitrix_dry_run_not_sent": sum(1 for item in scenario_rows if item.get("bitrix_send_status") == "DRY_RUN_NOT_SENT"),
        },
        "scenarios": scenario_rows,
        "report_file": _relative(VPP_AI_MANAGER_DRY_RUN_PATH),
        "markdown_report": "data/reports/vpp_ai_manager_dry_run.md",
        "next_action": "после проверки Яникой выбрать один сценарий и разрешить только следующий безопасный тест",
        "safety_note": "Это локальный dry-run: контакты заредактированы, Bitrix24/Redis/MAX/Telegram/LLM/реклама не вызывались.",
        "external_calls": report.get(
            "external_calls",
            {
                "redis": False,
                "bitrix24": False,
                "telegram_send": False,
                "max_send": False,
                "imap": False,
                "llm": False,
                "scheduler": False,
                "publisher": False,
                "ads": False,
            },
        ),
    }


def _first_safe_growth_tests() -> dict[str, Any]:
    report = _read_json(FIRST_SAFE_GROWTH_TESTS_PATH)
    if not report:
        return {
            "status": "MISSING_REPORT",
            "report_file": _relative(FIRST_SAFE_GROWTH_TESTS_PATH),
            "next_action": ".venv/bin/python scripts/dry_run_first_safe_growth_tests.py",
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
    report["report_file"] = _relative(FIRST_SAFE_GROWTH_TESTS_PATH)
    return report


def _bitrix_reactivation_readonly_plan() -> dict[str, Any]:
    report = _read_json(BITRIX_REACTIVATION_READONLY_PLAN_PATH)
    if not report:
        return {
            "status": "MISSING_REPORT",
            "report_file": _relative(BITRIX_REACTIVATION_READONLY_PLAN_PATH),
            "next_action": ".venv/bin/python scripts/dry_run_bitrix_reactivation_readonly.py",
            "external_calls": {"bitrix24": False},
        }
    report["report_file"] = _relative(BITRIX_REACTIVATION_READONLY_PLAN_PATH)
    return report


def _tender_filter_pack_dry_run() -> dict[str, Any]:
    report = _read_json(TENDER_FILTER_PACK_DRY_RUN_PATH)
    if not report:
        return {
            "status": "MISSING_REPORT",
            "report_file": _relative(TENDER_FILTER_PACK_DRY_RUN_PATH),
            "next_action": ".venv/bin/python scripts/dry_run_tender_filter_pack.py",
            "external_calls": {"tender_platform": False, "bitrix24": False},
        }
    report["report_file"] = _relative(TENDER_FILTER_PACK_DRY_RUN_PATH)
    return report


def _client_acquisition_pack_dry_run() -> dict[str, Any]:
    report = _read_json(CLIENT_ACQUISITION_PACK_DRY_RUN_PATH)
    if not report:
        return {
            "status": "MISSING_REPORT",
            "report_file": _relative(CLIENT_ACQUISITION_PACK_DRY_RUN_PATH),
            "next_action": ".venv/bin/python scripts/dry_run_client_acquisition_pack.py",
            "external_calls": {"bitrix24": False, "max": False, "ads": False},
        }
    report["report_file"] = _relative(CLIENT_ACQUISITION_PACK_DRY_RUN_PATH)
    return report


def _three_qualified_leads_sprint() -> dict[str, Any]:
    report = _read_json(THREE_QUALIFIED_LEADS_SPRINT_PATH)
    if not report:
        return {
            "status": "MISSING_REPORT",
            "report_file": _relative(THREE_QUALIFIED_LEADS_SPRINT_PATH),
            "next_action": ".venv/bin/python scripts/dry_run_three_qualified_leads_sprint.py",
            "external_calls": {"bitrix24": False, "max": False, "ads": False},
        }
    report["report_file"] = _relative(THREE_QUALIFIED_LEADS_SPRINT_PATH)
    return report


def _report_entries(report_text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for match in re.finditer(r"^###\s+(.+?)\n(.*?)(?=^###\s+|\Z)", report_text, re.MULTILINE | re.DOTALL):
        entries.append({"title": match.group(1).strip(), "body": match.group(2).strip()})
    return entries


def _is_agent_system_entry(title: str) -> bool:
    title_lower = title.lower()
    keywords = [
        "agent",
        "агент",
        "checker",
        "dashboard",
        "админ",
        "llm",
        "openrouter",
        "handoff",
        "okr",
        "метрик",
        "канал",
        "redis",
        "mvp",
        "crm",
        "bitrix",
        "telegram",
        "romi",
        "суброл",
        "сценар",
        "артефакт",
    ]
    return any(keyword in title_lower for keyword in keywords)


def _latest_system_report_entry(report_text: str) -> dict[str, str]:
    entries = _report_entries(report_text)
    for entry in entries:
        if _is_agent_system_entry(entry["title"]):
            return entry
    return entries[0] if entries else {"title": "нет данных", "body": ""}


def _latest_report_title(report_text: str) -> str:
    return _latest_system_report_entry(report_text)["title"]


def _latest_next_step(report_text: str) -> str:
    body = _latest_system_report_entry(report_text)["body"]
    match = re.search(r"^- Следующий маленький шаг:\s*(.+)$", body, re.MULTILINE)
    return match.group(1).strip() if match else "нет данных"


def _extract_okr(agent_text: str) -> str:
    match = re.search(
        r"Ожидаемый конечный результат:\s*(.*?)(?:\n\nМетрики:|\nМетрики:)",
        agent_text,
        re.DOTALL,
    )
    if not match:
        return "нет данных"
    return " ".join(line.strip() for line in match.group(1).splitlines() if line.strip())


def _extract_metrics(agent_text: str) -> list[str]:
    match = re.search(
        r"Метрики:\s*(.*?)(?:\n\nФизическая память OKR:|\nФизическая память OKR:|\n\"\"\"|\Z)",
        agent_text,
        re.DOTALL,
    )
    if not match:
        return []
    metrics: list[str] = []
    for line in match.group(1).splitlines():
        cleaned = line.strip()
        if cleaned.startswith("- "):
            metrics.append(cleaned[2:].strip())
    return metrics


def _metric_completion(metric: dict[str, Any]) -> float | None:
    try:
        current = float(metric.get("current_value", 0))
        target = float(metric.get("target_value", 0))
    except (TypeError, ValueError):
        return None
    direction = metric.get("direction", "at_least")
    if direction == "at_most":
        return 100.0 if current <= target else 0.0
    if target <= 0:
        return 100.0 if current <= 0 else 0.0
    return max(0.0, min(100.0, (current / target) * 100.0))


def _okr_readiness_percent(metrics: list[dict[str, Any]]) -> int | None:
    completions = [
        completion
        for metric in metrics
        if (completion := _metric_completion(metric)) is not None
    ]
    if not completions:
        return None
    return round(sum(completions) / len(completions))


def _safe_report_summary(path: Path) -> dict[str, Any]:
    data = _read_json(path)
    stat = path.stat()
    safe_statuses: dict[str, Any] = {}
    for key, value in data.items():
        if key in SAFE_STATUS_KEYS or key.endswith("_status"):
            if isinstance(value, (str, int, float, bool)) or value is None:
                safe_statuses[key] = value

    external_calls = data.get("external_calls")
    if not isinstance(external_calls, dict):
        external_calls = {}

    primary_status = (
        safe_statuses.get("agent_contract_status")
        or safe_statuses.get("dashboard_build_status")
        or safe_statuses.get("llm_offer_status")
        or safe_statuses.get("llm_score_status")
        or safe_statuses.get("bitrix_send_status")
        or safe_statuses.get("telegram_send_status")
        or safe_statuses.get("config_status")
        or safe_statuses.get("test_type")
        or "нет данных"
    )

    return {
        "event_id": path.stem,
        "created_at": data.get("created_at")
        or datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "event_type": data.get("test_type") or path.stem,
        "status": primary_status,
        "summary": f"{path.name}: {primary_status}",
        "report_file": _relative(path),
        "safe_statuses": safe_statuses,
        "external_calls": external_calls,
        "next_action": "см. REPORT.md" if path.name != "agent_dashboard.json" else "обновляется этим скриптом",
    }


def _recent_events(limit: int = 12) -> list[dict[str, Any]]:
    if not REPORTS_DIR.exists():
        return []
    report_files = sorted(
        REPORTS_DIR.glob("*.json"),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    return [_safe_report_summary(path) for path in report_files[:limit]]


def _build_agents(checker_report: dict[str, Any]) -> list[dict[str, Any]]:
    checked_agents = checker_report.get("checked_agents")
    if not isinstance(checked_agents, dict):
        checked_agents = {}
    registry_rows = _read_csv_rows(CHANNEL_REGISTRY_PATH)
    competitor_rows = _read_csv_rows(COMPETITOR_WATCHLIST_PATH)
    yanika_rows = _read_csv_rows(YANIKA_KNOWN_CHANNELS_PATH)

    agents: list[dict[str, Any]] = []
    for agent_id, config in AGENT_CONFIG.items():
        init_path = AGENT_PATHS[agent_id]
        text = _read_text(init_path)
        checker_status = checked_agents.get(agent_id, {})
        if not isinstance(checker_status, dict):
            checker_status = {}
        okr_metrics = config.get("okr_metrics", [])
        if not isinstance(okr_metrics, list):
            okr_metrics = []
        okr_readiness_percent = _okr_readiness_percent(okr_metrics)

        agents.append(
            {
                "agent_id": agent_id,
                "title": config["title"],
                "department": config["department"],
                "panel_status": config["panel_status"],
                "file": _relative(init_path),
                "folder": _relative(init_path.parent),
                "file_status": "FOUND" if init_path.is_file() else "MISSING",
                "checker_status": checker_status,
                "role": config["department"],
                "description": config["description"],
                "readiness_percent": config["readiness_percent"],
                "okr_readiness_percent": okr_readiness_percent,
                "main_metric": config.get("main_metric", {}),
                "okr_metrics": okr_metrics,
                "guard_metrics": config.get("guard_metrics", []),
                "todo": config["todo"],
                "inputs": config["inputs"],
                "outputs": config["outputs"],
                "okr": config["okr"],
                "source_okr_status": "FOUND" if _extract_okr(text) != "нет данных" else "MISSING",
                "source_scope": _agent_source_scope(
                    agent_id,
                    registry_rows=registry_rows,
                    competitor_rows=competitor_rows,
                    yanika_rows=yanika_rows,
                ),
                "metrics": _extract_metrics(text),
                "skills": config["skills"],
                "subroles": SUBROLE_CONFIG.get(agent_id, []),
                "mcp_api": config["mcp_api"],
                "next_action": config["next_action"],
            }
        )
    return agents


def _overall_status(checker_report: dict[str, Any]) -> str:
    required_ok = [
        checker_report.get("agent_contract_status"),
        checker_report.get("visual_map_status"),
        checker_report.get("admin_dashboard_spec_status"),
    ]
    return "OK" if all(status == "OK" for status in required_ok) else "NEEDS_REVIEW"


def _visual_display() -> dict[str, Any]:
    return {
        "display_status": "read_only",
        "lecture_model": "главный оркестратор -> департаменты -> агенты -> входы/выходы -> проверяемый результат -> метрики -> REPORT",
        "source_lesson_files": [
            "../../lessons/system/multi-agent-visual-dashboard-description-2026-05-08.md",
            "../../lessons/system/lesson-5-turnkey-agent-org-chart.md",
            "../../lessons/system/lesson-5-part-2-product-system-rules-2026-05-07.md",
        ],
        "departments": DEPARTMENT_VIEW,
        "operating_flow": OPERATING_FLOW,
        "handoffs": HANDOFF_VIEW,
        "control_blocks": [
            {
                "title": "Проверить систему",
                "command": ".venv/bin/python scripts/check_agent_okr_contract.py",
                "mode": "read_only/local_report",
                "external_calls": "False",
            },
            {
                "title": "Обновить JSON",
                "command": ".venv/bin/python scripts/build_agent_dashboard.py",
                "mode": "read_only/local_report",
                "external_calls": "False",
            },
            {
                "title": "Обновить HTML",
                "command": ".venv/bin/python scripts/build_agent_dashboard_viewer.py",
                "mode": "read_only/static_html",
                "external_calls": "False",
            },
        ],
        "safety_note": "Это отображение ничего не запускает: только показывает локальные JSON/Markdown данные.",
    }


def _interaction_graph() -> dict[str, Any]:
    return {
        "graph_status": "read_only",
        "purpose": "показать, как агенты взаимодействуют между собой и через какие очереди/файлы передают результат",
        "routes": INTERACTION_ROUTES,
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


def _security_agent_control_layer() -> dict[str, Any]:
    security_text = _read_text(SECURITY_AGENT_PATH)
    required_markers = [
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
    missing_markers = [marker for marker in required_markers if marker not in security_text]
    status = "ACTIVE" if SECURITY_AGENT_PATH.is_file() and not missing_markers else "NEEDS_REVIEW"
    return {
        "status": status,
        "source_file": _relative(SECURITY_AGENT_PATH),
        "control_doc": _relative(SECURITY_CONTROL_DOC_PATH),
        "is_product_agent": False,
        "not_agent_7": True,
        "purpose": "единый контроль безопасности для всех 6 агентов, checker/dashboard, LLM, MCP/API и будущих интеграций",
        "required_markers_status": "OK" if not missing_markers else "FAILED",
        "missing_markers": missing_markers,
        "applied_to": [
            "CLAUDE.md",
            "AGENTS.md",
            ".claude/rules/security.md",
            "docs/claude-project-rules.md",
            "docs/security-agent-control-layer.md",
            "scripts/check_agent_okr_contract.py",
            "data/reports/agent_dashboard.json",
            "data/reports/agent_dashboard.md",
            "data/reports/agent_dashboard.html",
        ],
        "red_lines": [
            "деньги, лимиты, подписки и платные API только после явного подтверждения",
            "production, deploy, реальные публикации, outreach и массовые действия только после approval",
            "секреты, токены, cookies, session-файлы, PII и CRM-данные не показывать и не отправлять наружу",
            "новые MCP/API, внешняя telemetry и скрытые фоновые действия только через preflight",
        ],
        "green_corridor": [
            "локальные dry-run и read-only проверки",
            "локальные тесты, compileall, checker и dashboard builder",
            "синтетические или обезличенные данные",
            "обычные правки файлов без внешних отправок",
        ],
        "ai_specific_risks": [
            "prompt injection",
            "lethal trifecta",
            "SSRF",
            "slopsquatting",
            "markdown/image exfiltration",
            "неструктурированный LLM output",
            "небезопасные MCP-инструменты",
        ],
        "agent_touchpoints": [
            {"agent": "Agent 1 Scout", "control": "только публичные источники, без закрытых персональных данных"},
            {"agent": "Agent 2 Collector", "control": "один источник сначала, без массового сбора и без серых методов"},
            {"agent": "Agent 3 Processor", "control": "structured LLM I/O, prompt injection guard, без PII наружу"},
            {"agent": "Agent 4 Publisher", "control": "нет публикаций без approval, нет неподтверждённых обещаний"},
            {"agent": "Agent 5 CRM", "control": "CRM/Bitrix24/Telegram только по разрешённому сценарию, секреты не выводить"},
            {"agent": "Agent 6 Outreach", "control": "нет массовых отправок и первого касания без approval человека"},
            {"agent": "Checker/dashboard", "control": "read-only, статусы без секретов, без внешних вызовов"},
        ],
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


def build_dashboard() -> dict[str, Any]:
    report_text = _read_text(PROJECT_ROOT / "REPORT.md")
    checker_report = _read_json(CHECKER_REPORT_PATH)
    events = _recent_events()
    agents = _build_agents(checker_report)
    source_map = _source_map()
    bitrix_crm_hygiene = _bitrix_crm_hygiene()
    vpp_ai_manager_dry_run = _vpp_ai_manager_dry_run()
    first_safe_growth_tests = _first_safe_growth_tests()
    bitrix_reactivation_readonly_plan = _bitrix_reactivation_readonly_plan()
    tender_filter_pack_dry_run = _tender_filter_pack_dry_run()
    client_acquisition_pack_dry_run = _client_acquisition_pack_dry_run()
    three_qualified_leads_sprint = _three_qualified_leads_sprint()
    source_summary = source_map.get("summary", {})
    if not isinstance(source_summary, dict):
        source_summary = {}
    security_agent_control_layer = _security_agent_control_layer()

    dashboard = {
        "dashboard_build_status": "OK",
        "generated_at": _utc_now(),
        "source_documents": [
            "REPORT.md",
            "README.md",
            "AGENTS.md",
            "CLAUDE.md",
            "docs/admin-dashboard-spec.md",
            "docs/multi-agent-visual-control-map.md",
            "docs/agent-okr-and-checker-map.md",
            "content/library/sources/channel-registry-mvp.csv",
            "content/library/sources/competitor-channel-watchlist.csv",
            "content/library/sources/lecture-2026-05-15-growth-source-map.csv",
            "data/reports/lecture_growth_source_score.json",
            "data/reports/first_safe_growth_tests.json",
            "data/reports/bitrix_reactivation_readonly_plan.json",
            "data/reports/tender_filter_pack_dry_run.json",
            "content/library/sources/tender-filter-pack-vpp.csv",
            "data/reports/client_acquisition_pack_dry_run.json",
            "content/growth/acquisition-route-pack-vpp.csv",
            "data/reports/three_qualified_leads_sprint.json",
            "content/growth/three-qualified-leads-sprint.csv",
            "scripts/check_first_inbound_scenario_artifacts.py",
            "data/reports/first_inbound_scenario_artifact_check.json",
            "docs/three-qualified-leads-sprint-from-astrology-method.md",
            "docs/client-acquisition-operating-system-from-lecture.md",
            "content/library/sources/yanika-known-channels-template.csv",
            "docs/lecture-2026-05-15-growth-and-agent-system-for-vpp.md",
            "research/traffic-and-first-touch-map.md",
            "research/cross-channel-analytics-romi.md",
            "research/external-mas-ip-analysis-2026-05-15.md",
            "docs/lecturer-mas-reference-comparison-2026-05-17.md",
            "docs/agent-subroles-and-kpi-map.md",
            "docs/agent-scenario-artifact-contract.md",
            "agents/Агент безопастности/AGENT_SECURITY.md",
            "docs/security-agent-control-layer.md",
            "data/reports/agent_okr_contract_check.json",
        ],
        "top_panel": {
            "project_name": "design-studio-lead-engine",
            "overall_status": _overall_status(checker_report),
            "current_stage": _latest_report_title(report_text),
            "last_checked_at": checker_report.get("created_at", "нет данных"),
            "next_small_step": _latest_next_step(report_text),
            "locks": {
                "scheduler_locked": True,
                "mass_collection_locked": True,
                "real_publish_locked": True,
                "real_outreach_locked": True,
                "secrets_visible": False,
            },
            "external_calls": {
                "redis": False,
                "bitrix24": False,
                "telegram_send": False,
                "imap": False,
                "llm": False,
                "scheduler": False,
                "publisher": False,
            },
        },
        "visual_display": _visual_display(),
        "source_map": source_map,
        "bitrix_crm_hygiene": bitrix_crm_hygiene,
        "vpp_ai_manager_dry_run": vpp_ai_manager_dry_run,
        "first_safe_growth_tests": first_safe_growth_tests,
        "bitrix_reactivation_readonly_plan": bitrix_reactivation_readonly_plan,
        "tender_filter_pack_dry_run": tender_filter_pack_dry_run,
        "client_acquisition_pack_dry_run": client_acquisition_pack_dry_run,
        "three_qualified_leads_sprint": three_qualified_leads_sprint,
        "interaction_graph": _interaction_graph(),
        "management_protocol": MANAGEMENT_PROTOCOL,
        "mas_reference_layer": MAS_REFERENCE_LAYER,
        "security_agent_control_layer": security_agent_control_layer,
        "scenario_artifact_contract": SCENARIO_ARTIFACT_CONTRACT,
        "agent_map": {
            "agents_count": len(agents),
            "agents": [
                {
                    "agent_id": agent["agent_id"],
                    "title": agent["title"],
                    "department": agent["department"],
                    "panel_status": agent["panel_status"],
                    "file": agent["file"],
                }
                for agent in agents
            ],
            "edges": [
                {"from": "agent1_scout", "to": "agent2_collector", "passes": "source card"},
                {"from": "agent1_scout", "to": "agent4_publisher", "passes": "боли, темы, конкуренты"},
                {"from": "agent1_scout", "to": "agent5_crm", "passes": "каналы для аналитики"},
                {"from": "agent2_collector", "to": "agent3_processor", "passes": "RawLead -> leads:raw"},
                {"from": "agent3_processor", "to": "agent5_crm", "passes": "QualifiedLead -> leads:qualified"},
                {"from": "agent4_publisher", "to": "agent5_crm", "passes": "content_published -> content:published"},
                {"from": "agent6_outreach", "to": "agent5_crm", "passes": "OutreachLead -> leads:outreach"},
            ],
        },
        "agent_details": agents,
        "event_stream": events,
        "metrics_dashboard": {
            "agent_health": {
                "agent_contract_status": checker_report.get("agent_contract_status", "нет данных"),
                "visual_map_status": checker_report.get("visual_map_status", "нет данных"),
                "admin_dashboard_spec_status": checker_report.get("admin_dashboard_spec_status", "нет данных"),
                "dashboard_viewer_status": checker_report.get("dashboard_viewer_status", "нет данных"),
                "agents_count": len(agents),
            },
            "system_scope": {
                "total_channels": source_summary.get("canonical_mvp_channels", 0),
                "wave_1_channels": source_summary.get("wave_1_channels", 0),
                "wave_2_channels": source_summary.get("wave_2_channels", 0),
                "wave_3_channels": source_summary.get("wave_3_channels", 0),
                "active_channels": source_summary.get("active_channels", 0),
                "manual_channels": source_summary.get("manual_channels", 0),
                "planned_channels": source_summary.get("planned_channels", 0),
                "competitor_watchlist_sources": source_summary.get("competitor_watchlist_sources", 0),
                "yanika_pending_sources": source_summary.get("yanika_pending_sources", 0),
                "agent2_collection_channels": len(source_map.get("channels_by_owner", {}).get("agent2_collector", [])),
                "agent6_outreach_channels": len(source_map.get("channels_by_owner", {}).get("agent6_outreach", [])),
                "content_surfaces_target": source_summary.get("content_surfaces", len(CONTENT_SURFACES)),
                "crm_lesson_5_chain_steps": 6,
            },
            "lead_funnel": {
                "pipeline_health_test_leads": "1/1",
                "wave_1_source_coverage_target": "1/9",
                "agent2_source_coverage_target": "1/4",
                "monthly_pilot_raw_leads_target": "0/20",
                "bitrix_test_creations": "4",
            },
            "quality": {
                "score_categories_checked": "1/4",
                "llm_modes_checked": "2/2",
                "max_false_hot_rate_after_real_sample": "<=10%",
                "qualified_without_source_target": "0",
            },
            "crm_sla": {
                "lesson_5_crm_chain_covered": "5/6",
                "bitrix24_send_status": "OK",
                "telegram_send_status": "OK",
                "missing_crm_layer": "personal КП/landing status + visit_count/visitor_id",
            },
            "crm_hygiene": {
                "status": bitrix_crm_hygiene.get("status", "нет данных"),
                "contacts": bitrix_crm_hygiene.get("counts", {}).get("contacts", 0),
                "leads_total": bitrix_crm_hygiene.get("counts", {}).get("leads_total", 0),
                "leads_active": bitrix_crm_hygiene.get("counts", {}).get("leads_active", 0),
                "deals_total": bitrix_crm_hygiene.get("counts", {}).get("deals_total", 0),
                "contacts_without_phone_or_email": bitrix_crm_hygiene.get("quality_flags", {}).get("contacts_without_phone_or_email", 0),
                "leads_without_phone_or_email": bitrix_crm_hygiene.get("quality_flags", {}).get("leads_without_phone_or_email", 0),
                "contact_phone_duplicate_groups": bitrix_crm_hygiene.get("duplicate_groups", {}).get("contacts_by_phone", 0),
                "contact_email_duplicate_groups": bitrix_crm_hygiene.get("duplicate_groups", {}).get("contacts_by_email", 0),
                "lead_phone_duplicate_groups": bitrix_crm_hygiene.get("duplicate_groups", {}).get("leads_by_phone", 0),
                "lead_email_duplicate_groups": bitrix_crm_hygiene.get("duplicate_groups", {}).get("leads_by_email", 0),
                "report_file": bitrix_crm_hygiene.get("report_file", "нет данных"),
            },
            "vpp_ai_manager": {
                "status": vpp_ai_manager_dry_run.get("status", "нет данных"),
                "scenario_count": vpp_ai_manager_dry_run.get("scenario_count", 0),
                "enough_for_kp": vpp_ai_manager_dry_run.get("summary", {}).get("enough_for_kp", 0),
                "need_missing_data": vpp_ai_manager_dry_run.get("summary", {}).get("need_missing_data", 0),
                "bitrix_dry_run_not_sent": vpp_ai_manager_dry_run.get("summary", {}).get("bitrix_dry_run_not_sent", 0),
                "report_file": vpp_ai_manager_dry_run.get("report_file", "нет данных"),
            },
            "content": {
                "content_surfaces_tracked_now": "5/7",
                "first_week_drafts_target": "0/5",
                "monthly_core_topics_target": "0/20",
                "monthly_adapted_items_later": "0/52",
                "approval_fields_in_template": "3/3",
            },
            "outreach": {
                "wave_1_outreach_sources": "2/2",
                "candidate_review_target": "0/10",
                "reply_drafts_target": "0/5",
                "outreach_to_crm_test": "0/1",
                "real_sends_without_approval": 0,
            },
            "romi": {
                "status": "CSV MVP есть; visit->deal из дашборда лектора ещё не закрыт",
                "report_file": "data/reports/channel_report_mvp.csv",
                "registry_channels": "17/17",
                "cost_rows": "17/17",
                "fact_rows": "17/17",
                "report_rows": "17/17",
                "missing_visit_to_deal": "visit_count + visitor_id + CR_visit_to_deal",
            },
            "safety": {
                "security_agent_status": security_agent_control_layer.get("status", "нет данных"),
                "security_agent_file": security_agent_control_layer.get("source_file", "нет данных"),
                "locked_actions": [
                    "scheduler",
                    "mass_collection",
                    "real_publish",
                    "real_outreach",
                ],
                "secrets_visible": False,
            },
        },
        "checker": {
            "script": "scripts/check_agent_okr_contract.py",
            "report_file": "data/reports/agent_okr_contract_check.json",
            "agent_contract_status": checker_report.get("agent_contract_status", "нет данных"),
            "visual_map_status": checker_report.get("visual_map_status", "нет данных"),
            "admin_dashboard_spec_status": checker_report.get("admin_dashboard_spec_status", "нет данных"),
            "security_agent_status": checker_report.get("security_agent_status", "нет данных"),
            "dashboard_viewer_builder_status": checker_report.get("dashboard_viewer_builder_status", "нет данных"),
            "dashboard_viewer_status": checker_report.get("dashboard_viewer_status", "нет данных"),
            "dashboard_viewer_file": checker_report.get("dashboard_viewer_file", "data/reports/agent_dashboard.html"),
        },
        "next_small_step": _latest_next_step(report_text),
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
    return dashboard


def main() -> int:
    dashboard = build_dashboard()
    DASHBOARD_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DASHBOARD_REPORT_PATH.write_text(
        json.dumps(dashboard, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"dashboard_build_status={dashboard['dashboard_build_status']}")
    print(f"overall_status={dashboard['top_panel']['overall_status']}")
    print(f"agents_count={dashboard['agent_map']['agents_count']}")
    print(f"source_map_status={dashboard['source_map']['source_map_status']}")
    print(f"bitrix_crm_hygiene_status={dashboard['bitrix_crm_hygiene']['status']}")
    print(f"vpp_ai_manager_dry_run_status={dashboard['vpp_ai_manager_dry_run']['status']}")
    print(f"canonical_channels={dashboard['source_map']['summary']['canonical_mvp_channels']}")
    print(f"event_count={len(dashboard['event_stream'])}")
    print(
        "external_calls="
        + ",".join(f"{key}:{value}" for key, value in dashboard["external_calls"].items())
    )
    print(f"report_file={DASHBOARD_REPORT_PATH.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
