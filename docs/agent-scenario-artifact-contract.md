# Agent Scenario Artifact Contract

Дата: 2026-05-17

Статус: локальный контракт сценариев и артефактов. Ничего не отправляет во внешние сервисы. Используется для dashboard, checker и будущей админ-панели.

## 1. Зачем нужен контракт

У лектора важная идея не в количестве агентов, а в цепочке:

```text
задача -> маршрутизация -> агент -> артефакт -> QA -> следующий шаг -> память
```

Для нашего проекта каждый этап должен завершаться проверяемым артефактом. Если артефакта нет, этап считается не закрытым.

## 2. Единый статус задач

| Статус | Значение |
|---|---|
| `locked` | запуск запрещён без отдельного подтверждения или нет обязательных доступов |
| `manual` | этап делается руками, автоматизация ещё не включена |
| `draft` | черновик готов, но ещё не согласован |
| `approval_ready` | можно показать человеку на согласование |
| `approved` | человек одобрил следующий шаг |
| `queued` | задача ждёт обработки |
| `running` | этап выполняется |
| `needs_review` | нужен человек или QA |
| `failed` | этап упал, чинить минимально сломанную часть |
| `done` | этап завершён и есть артефакт |
| `published_manual_unverified_public` | опубликовано вручную, публичные метрики ещё не подтверждены |

## 3. Обязательные поля каждого шага

Каждый шаг сценария должен иметь:

```text
scenario
step_id
owner_agent
owner_subrole
input
output_artifact
artifact_path_or_queue
status
kpi
verification
next_step
external_calls
forbidden_actions
```

Важно: `external_calls` всегда фиксируется как `True/False`, без секретов и токенов.

## 4. Сценарий 1: первый входящий запрос

Цель: доказать путь от первого вопроса клиента до CRM и человека.

```text
сайт / MAX / Telegram / email
-> AI-менеджер / intake
-> Agent 3 Processor
-> Agent 5 CRM
-> Bitrix24 сделка или payload preview
-> человек
```

| Шаг | Владелец | Вход | Артефакт | Где хранить | Статус MVP |
|---|---|---|---|---|---|
| 1. Вход | Agent 5 CRM / CRM Router | сообщение клиента | `intake_card` | `data/reports/*intake*` | local dry-run есть |
| 2. Квалификация | Agent 3 Processor / Scorer | `intake_card` или RawLead | `qualified_lead` | Redis `leads:qualified` или JSON dry-run | частично проверено |
| 3. CRM preview | Agent 5 CRM / CRM Router | `qualified_lead` | `crm_payload_preview` | `data/reports/*crm_payload_preview*` | есть |
| 4. Bitrix24 | Agent 5 CRM / CRM Router | approved payload | `bitrix_lead` или `bitrix_deal` | Bitrix24 + локальный отчёт | тест лида есть, сделка разрешалась отдельно |
| 5. Человек | человек | карточка CRM | `human_next_step` | CRM-комментарий / REPORT | ручной слой |
| 6. Аналитика | Agent 5 CRM / Attribution Agent | источник и статус | `attribution_record` | channel facts/report | planned |

Локальная проверка:

```text
scripts/check_first_inbound_scenario_artifacts.py
scripts/create_first_inbound_scenario_handoff.py
```

Статус на 2026-05-17: `OK_LOCAL_DRY_RUN_READY_FOR_MANUAL_REVIEW`.

В MVP `human_next_step` хранится не отдельным файлом, а внутри `crm_payload_preview.output.human_handoff`. Это допустимо для dry-run, потому что человек видит следующий шаг до реальной отправки в Bitrix24.

Task-handoff в сценарий создан: `data/reports/first_inbound_scenario_handoff_to_human.json`.

KPI сценария:

- каждый этап имеет вход, выход, статус и next_step;
- payload перед реальной отправкой можно посмотреть локально;
- источник, flow, score, object_type, area_m2, first_touch_channel, last_touch_channel не теряются;
- реальные клиенты не используются в тестах.

Запреты:

- не отправлять во внешние сервисы без отдельного approval;
- не показывать webhook и токены;
- не запускать scheduler ради этого сценария.

## 5. Сценарий 2: контент даёт лид

Цель: связать разведку, контент, публикации и аналитику.

```text
Agent 1 SignalCard
-> Agent 4 content brief
-> draft / approval
-> manual publication
-> public metrics
-> inbound question
-> Agent 5 analytics
```

| Шаг | Владелец | Вход | Артефакт | Где хранить | Статус MVP |
|---|---|---|---|---|---|
| 1. Сигнал | Agent 1 Scout / Source Radar | публичный источник | `SignalCard` | `research/*radar*` | есть ручной MVP |
| 2. Контент-brief | Agent 4 Publisher / Content Strategist | SignalCard | `content_brief` | `content/pipeline/*` | частично |
| 3. Черновик | Agent 4 Publisher / Copywriter | brief | `content_draft` | dry-run output | есть |
| 4. Редактура | Agent 4 Publisher / Editor | draft | `editor_check` | local report | частично |
| 5. Согласование | Agent 4 Publisher / Approval Coordinator | draft + check | `approval_card` | content pipeline | частично |
| 6. Метрики | Agent 4 Publisher / Content Metrics Analyst | опубликованный пост | `content_metric_event` | Redis `content:published` позже | planned |
| 7. CRM/ROMI | Agent 5 CRM / Attribution Agent | content event + лид | `content_attribution_record` | channel report | planned |

KPI сценария:

- формат поста не повторяет один шаблон подряд;
- у материала есть этап воронки;
- у материала есть стоимость генерации, статус согласования, причина перегенерации при правках;
- метрики берутся только из открытых или подтверждённых источников.

Запреты:

- не публиковать автоматически;
- не скачивать чужой контент;
- не использовать чужие формулировки без переработки и проверки риска.

## 6. Сценарий 3: тендерный лид

Цель: проверить один понятный источник сбора без массового парсинга.

```text
Gmail / IMAP tender
-> Agent 2 Collector
-> RawLead
-> Agent 3 Processor
-> QualifiedLead
-> Agent 5 CRM
-> Bitrix24 / Telegram / человек
```

| Шаг | Владелец | Вход | Артефакт | Где хранить | Статус MVP |
|---|---|---|---|---|---|
| 1. Письмо | Agent 2 Collector / Tender Email Collector | email/tender text | `raw_lead` | Redis `leads:raw` | частично |
| 2. Нормализация | Agent 2 Collector / Lead Normalizer | сырой текст | `normalized_raw_lead` | Redis `leads:raw` | planned |
| 3. Дубль | Agent 2 Collector / Duplicate Guard | raw lead | `duplicate_decision` | local log/report | planned |
| 4. Скоринг | Agent 3 Processor / Scorer | RawLead | `qualified_lead` | Redis `leads:qualified` | проверено |
| 5. CRM | Agent 5 CRM / CRM Router | QualifiedLead | `crm_payload_preview` или `bitrix_lead` | local report / Bitrix24 | проверено на тесте |
| 6. Человек | человек | CRM-карточка | `human_next_step` | CRM / REPORT | ручной слой |

KPI сценария:

- `RawLead` имеет source, raw_text, flow, created_at;
- `QualifiedLead` имеет score, score_reason, recommended_action;
- Agent 5 создаёт CRM payload без потери source attribution;
- очередь очищается после теста.

Запреты:

- не включать массовый сбор писем;
- не использовать реальные клиентские данные в тестовом отчёте;
- не отправлять Telegram/Bitrix без явного разрешения.

## 7. Сценарий 4: ROMI канала

Цель: видеть окупаемость и рентабельность каждого канала.

```text
source
-> cost
-> lead
-> deal
-> revenue
-> profit
-> ROMI
-> решение оставить / усилить / выключить канал
```

| Шаг | Владелец | Вход | Артефакт | Где хранить | Статус MVP |
|---|---|---|---|---|---|
| 1. Канал | Agent 5 CRM / Attribution Agent | channel registry | `channel_registry_row` | `content/library/sources/channel-registry-mvp.csv` | есть |
| 2. Расход | Agent 5 CRM / ROMI Reporter | spend/cost | `channel_cost_row` | `data/channel_costs_mvp.csv` | есть |
| 3. Факт | Agent 5 CRM / Attribution Agent | visits/leads/deals/revenue | `channel_fact_row` | `data/channel_facts_mvp.csv` | есть |
| 4. Расчёт | Agent 5 CRM / ROMI Reporter | registry + costs + facts | `channel_report` | `data/reports/channel_report_mvp.csv` | есть MVP |
| 5. Решение | человек + Agent 5 | report | `channel_decision` | REPORT / future dashboard | manual |

KPI сценария:

- CPL, CAC, profit, ROMI считаются локально;
- каналы без расходов не ломают отчёт;
- каналы с плохой окупаемостью попадают в список на пересмотр;
- решение по каналу принимает человек.

Запреты:

- не запускать рекламу ради теста;
- не подставлять выручку без подтверждения;
- не удалять канал только по одному слабому тесту.

## 8. Что показывает dashboard

Dashboard должен показывать:

- 6 агентов как департаменты;
- суброли внутри каждого агента;
- сценарии;
- последний артефакт каждого сценария;
- статус каждого сценария;
- блокеры;
- next_step;
- external_calls как `True/False`;
- ссылку на локальный отчёт или файл.

## 9. Следующий маленький шаг

После фиксации этого контракта нужно перестроить:

```text
data/reports/agent_dashboard.json
data/reports/agent_dashboard.md
data/reports/agent_dashboard.html
data/reports/agent_okr_contract_check.json
```

Проверка должна быть локальной. Redis, Bitrix24, Telegram, IMAP, LLM, scheduler и publisher не запускать.
