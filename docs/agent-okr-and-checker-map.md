# Agent OKR and Checker Map

Дата: 2026-05-08

Статус: применён урок 5, часть 2. Новые агенты не создавались. Платные API, массовый сбор, реальные публикации и `orchestrator/scheduler.py` не запускались.

## 1. Главное правило

Многоагентная система считается рабочей не по количеству папок, а по тому, что у каждого агентского департамента есть:

- зона ответственности;
- ожидаемый конечный результат;
- измеримые метрики;
- входы и выходы;
- физический файл с правилами;
- маленький проверяемый тест;
- запись результата в `REPORT.md`.

После сверки с внешним референсом `dz-ai-day-5` добавлено управленческое правило:

```text
агент = роль / ответственность;
skill = действие, которое помогает роли;
Chief of Staff = режим координации через CLAUDE.md/AGENTS.md/REPORT.md, не новый Agent 7.
```

Подробный протокол входа задач, handoff, agent-result, escalation-to-yana и weekly digest лежит в `docs/chief-of-staff-handoff-protocol.md`.

После анализа примера лектора по визуализации AI-компании добавлен второй слой:

```text
6 агентов остаются департаментами;
внутри них есть суброли;
каждая суброль имеет ответственность, артефакт и KPI;
каждый сценарий закрывается только проверяемым артефактом.
```

Физические документы: `docs/agent-subroles-and-kpi-map.md` и `docs/agent-scenario-artifact-contract.md`.

## 2. Таблица агентов и департаментов

| Агент | Департамент | Папка | Главный вход | Главный выход | Текущий статус |
|---|---|---|---|---|---|
| Agent 1 Scout | Разведка источников | `agents/agent1_scout/` | рынок, конкуренты, источники | source cards для Agent 2/4/5 | Папки есть, runtime не подключён |
| Agent 2 Collector | Сбор лидов | `agents/agent2_collector/` | один разрешённый источник | `RawLead` в Redis `leads:raw` | Частично реализован, активный MVP-источник — IMAP/tender |
| Agent 3 Processor | Обработка и скоринг | `agents/agent3_processor/` | `RawLead` из `leads:raw` | `QualifiedLead` в `leads:qualified` | Реализован и проверен локальным Redis-тестом |
| Agent 4 Publisher | Контент и доверие | `agents/agent4_publisher/` | тема, бренд, согласование | контент, dry-run, `content:published` | Частично реализован, реальные публикации не запускать без подтверждения |
| Agent 5 CRM | CRM, уведомления, аналитика | `agents/agent5_crm/` | `QualifiedLead`, `OutreachLead`, content event | Bitrix24 лид, Telegram уведомление, отчёт | Реализован и проверен Bitrix24 + Telegram |
| Agent 6 Outreach | Первое касание | `agents/agent6_outreach/` | чаты, комментарии, найденные кандидаты | одобренный ответ, `OutreachLead` | Частично реализован, полный outreach-тест позже |

## 3. OKR и метрики по агентам

| Агент | Ожидаемый конечный результат | Главная числовая метрика | OKR/KR метрики |
|---|---|---|---|
| Agent 1 Scout | Регулярно выдаёт проверенные source cards / SignalCard: где искать лиды, почему источник перспективен, какому агенту передать следующий шаг. | Покрытие карты источников: 17/17 каналов. | Все каналы 17/17; wave_1 9/9; planned-каналы лектора 8/8; watchlist 15/15; ручной MVP Radar 10/10 SignalCard; личные каналы Яники 0/5. |
| Agent 2 Collector | Берёт один источник за раз, собирает сырые лиды/сигналы и кладёт их в Redis как `RawLead`. | Покрытие источников Agent 2: 1/4 проверенных источника. | Каналы Agent 2 4/4; проверенный сбор 1/4; тестовые RawLead 1/4; месячный пилот 0/20; Redis-передача 1/1. |
| Agent 3 Processor | Превращает сырой лид в квалифицированный: поток A/B, контакт, объект, score, оффер, следующий шаг. | Обработка первой волны: 1/9 тестовых лидов. | Сквозной тест 1/1; покрытие wave_1 1/9; режимы скоринга 2/2; CRM-handoff 1/1; категории score 1/4. |
| Agent 4 Publisher | Готовит контент и точки доверия: идея -> черновик -> согласование -> публикация/событие -> аналитика. | Контентные поверхности: 5/7 учтены в текущем шаблоне. | Поверхности 5/7; черновики первой недели 0/5; ядро месяца 0/20 тем; полный адаптированный план позже 0/52; поля согласования 3/3. |
| Agent 5 CRM | Доставляет лид в Bitrix24, уведомляет менеджера, пишет события и готовит аналитику по лидам/каналам/ROMI. | Каналы в аналитике: 17/17. | Каналы аналитики 17/17; wave_1 9/9; CRM-тест 1/1; цепочка урока 5 5/6; тестовые Bitrix24-создания 4; CR visit->deal 0/1. |
| Agent 6 Outreach | Находит релевантные обсуждения, готовит ответ, отправляет только после одобрения и передаёт заинтересованный ответ в CRM. | Outreach-источники первой волны: 0/2 операционно проверены. | Источники учтены 2/2; кандидаты 0/10; черновики ответов 0/5; outreach->CRM 0/1; реальные отправки до approval 0/0. |

Важно: `1 лид` - это не норма работы, а только минимальная проверка трубы. Для покрытия первой волны нужен минимум `9 тестовых сигналов` - по одному на каждый канал первой волны. Для Agent 2 отдельно нужен минимум `4 тестовых RawLead` - по одному на каждый его источник.

План публикаций считаем не как случайные посты, а как управляемый контентный контур:

- `7` поверхностей для учёта: MAX, Telegram, VK, Дзен, Яндекс Карты, 2GIS, сайт/блог.
- `5` черновиков - первый безопасный недельный тест без публикации.
- `20` базовых тем - месячное ядро, примерно одна тема на рабочий день.
- `52` адаптированных материала - полный будущий месячный план после MVP, если ведём все поверхности.

## 4. Где OKR должны быть записаны физически

| Что фиксируем | Основное место | Дополнительное место | Статус |
|---|---|---|---|
| Главные правила проекта | `CLAUDE.md`, `AGENTS.md` | `REPORT.md` как журнал изменений | Есть |
| Chief of Staff / handoff protocol | `docs/chief-of-staff-handoff-protocol.md` | `docs/multi-agent-visual-control-map.md`, `docs/admin-dashboard-spec.md` | Есть |
| Суброли и KPI | `docs/agent-subroles-and-kpi-map.md` | `agents/agent*/__init__.py`, dashboard | Есть |
| Сценарии и артефакты | `docs/agent-scenario-artifact-contract.md` | `data/reports/agent_dashboard.json`, Markdown/HTML dashboard | Есть |
| OKR Agent 1 | `agents/agent1_scout/__init__.py` | этот документ | Записано |
| OKR Agent 2 | `agents/agent2_collector/__init__.py` | этот документ | Записано |
| OKR Agent 3 | `agents/agent3_processor/__init__.py` | этот документ | Записано |
| OKR Agent 4 | `agents/agent4_publisher/__init__.py` | `agents/agent4_publisher/README.md`, этот документ | Записано |
| OKR Agent 5 | `agents/agent5_crm/__init__.py` | этот документ | Записано |
| OKR Agent 6 | `agents/agent6_outreach/__init__.py` | этот документ | Записано |
| История проверок | `REPORT.md` | `tasks/session-notes.md` | Есть |
| Тесты MVP | `scripts/test_*.py` | `data/reports/*.json` | Есть |
| Админ-сверка / checker | `scripts/check_agent_okr_contract.py` | `docs/multi-agent-visual-control-map.md`, `docs/admin-dashboard-spec.md`, `scripts/build_agent_dashboard.py`, `scripts/build_agent_dashboard_viewer.py`, `scripts/build_agent_dashboard_markdown.py`, `data/reports/agent_dashboard.json`, `data/reports/agent_dashboard.html`, `data/reports/agent_dashboard.md`, `data/reports/agent_okr_contract_check.json` | Создано и проверено |

## 4.1. Контракт Agent 1 Scout: SignalCard

После ручного MVP `Universal Demand & Content Radar` Agent 1 Scout должен отдавать не просто список ссылок, а карточки `SignalCard`.

Минимальные поля:

```text
source
platform
url
topic
audience
pain_or_demand
hook
format
visible_metrics
why_it_worked
risk_notes
project_fit
recommended_action
handoff_to
status
```

Простыми словами: Agent 1 не говорит `вот ссылка, посмотри`. Он говорит:

```text
вот сигнал рынка -> вот почему он важен -> вот риск -> вот что делать дальше -> вот кому передать
```

Дальше информация используется так:

| `handoff_to` | Что делать с карточкой |
|---|---|
| `Site` | Превратить в блок сайта, FAQ, страницу услуги, кейс или доверительный аргумент |
| `Agent 4 Publisher` | Превратить в тему поста, рубрику, сценарий, контент-план или approval-задачу |
| `Agent 2 Collector` | Превратить в гипотезу нового источника лидов, но не запускать сбор без отдельной проверки |
| `Agent 5 CRM` | Добавить источник/сегмент в CRM-разметку, аналитику каналов, CPL/CAC/ROMI или отчет |
| `Agent 6 Outreach` | Использовать как основу для первого касания только после approval и без автоматических отправок |

Статусы карточек:

```text
new -> reviewed -> approved -> used
new -> reviewed -> rejected
```

Защитное правило: карточка без `risk_notes`, `recommended_action` и `handoff_to` не считается готовым выходом Agent 1.

## 5. Минимальный checker-agent без создания Agent 7

Новый агент не нужен. Правильнее сделать маленький checker как внутренний контрольный режим проекта:

```text
scripts/check_agent_okr_contract.py
```

Что он должен проверять:

- существует ли каждая папка из списка 6 агентских департаментов;
- есть ли в верхнем `__init__.py` слова `Ожидаемый конечный результат` и `Метрики`;
- есть ли у Agent 4 `README.md`;
- совпадают ли названия агентских папок с `CLAUDE.md`;
- есть ли ключевые очереди Redis в `shared/redis_client.py`;
- есть ли канонический сквозной тест в `scripts/test_agent3_to_agent5_handoff_local.py`;
- есть ли визуальная карта `docs/multi-agent-visual-control-map.md`;
- содержит ли визуальная карта 6 агентов, пути к файлам, Mermaid-схему, таблицу агентов, админ-панель и checker-блок;
- есть ли спецификация админ-панели `docs/admin-dashboard-spec.md`;
- содержит ли спецификация блоки урока: верхняя панель, карта агентов, детали агента, event stream, dashboard метрик и checker;
- есть ли read-only сборщик `scripts/build_agent_dashboard.py`;
- есть ли локальный dashboard JSON `data/reports/agent_dashboard.json`;
- есть ли HTML-просмотрщик `data/reports/agent_dashboard.html`;
- есть ли Markdown-снимок `data/reports/agent_dashboard.md`;
- пишет ли результат в `data/reports/agent_okr_contract_check.json`.

Ожидаемый вывод checker:

```text
agent_contract_status=OK/FAILED
missing_agent_files=...
missing_okr_blocks=...
missing_metric_blocks=...
canonical_test_status=FOUND/MISSING
visual_map_status=OK/FAILED
missing_visual_map_items=...
admin_dashboard_spec_status=OK/FAILED
missing_admin_dashboard_items=...
dashboard_builder_status=FOUND/MISSING
dashboard_report_status=OK/FAILED
missing_dashboard_report_items=...
dashboard_viewer_status=OK/FAILED
dashboard_markdown_status=OK/FAILED
missing_dashboard_viewer_items=...
missing_dashboard_markdown_items=...
report_file=data/reports/agent_okr_contract_check.json
```

Статус на 2026-05-10: checker-скрипт создан и прошёл проверку с `agent_contract_status=OK`, `visual_map_status=OK`, `admin_dashboard_spec_status=OK`, `dashboard_report_status=OK`, `dashboard_viewer_status=OK` и `dashboard_markdown_status=OK`.

Дополнительно checker должен подтверждать, что в HTML-viewer есть блок `Перемещаемая карта агентов`, центральный узел `Главный агент-оркестратор`, контейнер `workflowCanvas`, draggable-карточки `workflow-node`, локальный ключ `leadEngineAgentWorkflowPositionsV1`, кнопка `Сбросить расположение`, блок `Что доделать` и проценты готовности.

## 6. Один сквозной тест, который доказывает работу системы

Канонический тест для доказательства MVP:

```bash
.venv/bin/python scripts/test_agent3_to_agent5_handoff_local.py
```

Что он доказывает:

```text
RawLead -> Redis leads:raw -> Agent 3 local score/offer -> Redis leads:qualified -> Agent 5 -> Bitrix24 + Telegram
```

Почему это лучший тест сейчас:

- он проверяет сердце системы, а не отдельную функцию;
- не запускает `orchestrator/scheduler.py`;
- не запускает IMAP;
- не запускает массовый сбор;
- не запускает LLM/API;
- не публикует реальные посты;
- использует ровно один тестовый лид;
- проверяет очереди до и после, чтобы не оставить хвосты.

Ожидаемые статусы:

```text
redis_ping_status=OK
queue_guard_status=OK
redis_push_raw_status=OK
agent3_run_status=OK
agent5_run_status=OK
qualified_output_status=OK
bitrix_send_status=OK
telegram_send_status=OK
cleanup_status=OK
```

Статус на 2026-05-08: тест уже пройден, тестовый лид `832` создан и затем закрыт как `JUNK`. Это значит, что базовый контролируемый MVP-путь доказан.

## 7. Что не делаем сейчас

- Не создаём Agent 7.
- Не запускаем массовый сбор.
- Не запускаем `orchestrator/scheduler.py`.
- Не публикуем реальные посты.
- Не подключаем новые платные сервисы.
- Не запускаем outreach-отправку без отдельного подтверждения.

## 8. Один маленький следующий шаг

Перед следующими runtime-проверками повторить локальный checker:

```text
scripts/check_agent_okr_contract.py
```

Он ничего не отправляет наружу. Только читает файлы проекта, проверяет наличие OKR/метрик и пишет локальный JSON-отчёт.
