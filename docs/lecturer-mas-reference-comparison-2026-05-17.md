# Lecturer MAS Reference Comparison

Дата: 2026-05-17

Статус: анализ промпта лектора как образца многоагентной системы. Дизайн не разрабатывался, код не писался, новые агенты не создавались.

## 1. Что это за пример

Промпт лектора описывает не просто красивую схему. Он описывает операционную модель AI-компании:

```text
человек даёт задачу
-> главный Orchestrator
-> задача дробится
-> департаменты получают свои части
-> агенты делают работу
-> появляются артефакты
-> качество проверяется
-> результат возвращается в память и следующий этап
```

Главная польза для нашего проекта: сделать систему понятной не по папкам, а по управлению задачами, артефактам, статусам и метрикам.

## 2. Что уже есть у нас

| Блок из примера лектора | Есть у нас | Где лежит |
|---|---|---|
| Главный Orchestrator | Да, смысловой оркестратор правил | `CLAUDE.md`, `AGENTS.md` |
| Память системы | Да | `REPORT.md`, `tasks/session-notes.md` |
| Технический запускатель | Да | `orchestrator/scheduler.py` |
| Департаменты | Да, 6 рабочих агентов | `agents/agent1_scout` ... `agents/agent6_outreach` |
| Роли агентов | Да | `agents/*/__init__.py`, `docs/agent-okr-and-checker-map.md` |
| OKR и метрики | Да | `docs/agent-okr-and-checker-map.md`, `data/reports/agent_dashboard.*` |
| Inspector-панель | Частично | `docs/admin-dashboard-spec.md`, `data/reports/agent_dashboard.html` |
| Scenario timeline | Частично | `docs/admin-dashboard-spec.md` |
| Artifact tracker | Частично | `data/reports/*.json`, approval cards, CSV-трекеры |
| Checker / QA | Да | `scripts/check_agent_okr_contract.py`, `scripts/check_content_funnel_contract.py` |
| Weekly digest | Запланирован | `docs/chief-of-staff-handoff-protocol.md` |

Вывод: базовая управленческая логика уже есть. Нам не нужно добавлять десятки новых агентов.

## 3. Как роли лектора ложатся на наши 6 агентов

| У лектора | У нас | Что делать |
|---|---|---|
| Chief Orchestrator, Task Decomposer, Context Router, Quality Arbiter, Memory Manager | `CLAUDE.md / AGENTS.md`, `REPORT.md`, checker | Оставить как слой управления, не создавать Agent 7 |
| Strategy Department | Agent 1 Scout + Agent 3 Processor | Scout ищет рынок и спрос, Processor помогает квалифицировать и формировать next_action |
| Marketing Department | Agent 4 Publisher + Agent 5 CRM | Agent 4 создаёт контент и точки доверия, Agent 5 считает результат |
| Content Department | Agent 4 Publisher | Это skills Agent 4: посты, КП, лендинги, сценарии, письма |
| Design Department | Отдельная ветка сайта / будущий skill Agent 4 | В этой ветке не развиваем дизайн, только фиксируем связь с контентом и артефактами |
| Development Department | Codex + checker + будущий dashboard | Это не лидовый агент, а технический слой реализации |
| Production Department | Agent 4 Publisher + approval Яники | Публикация только после ручного подтверждения |
| Analytics Department | Agent 5 CRM/Analytics | Лиды, сделки, канал, выручка, ROMI |
| Automation & Operations Department | Agent 5 + scheduler + docs | Интеграции, отчёты, очереди, повторяемые процессы |

Простое правило:

```text
У лектора много департаментов.
У нас те же функции должны жить внутри 6 агентов как роли и skills.
Новых агентов сейчас не создаём.
```

## 4. Что полезно добавить в нашу систему

### 4.1. Сценарии должны стать первичным объектом

Сейчас у нас есть агенты и отчёты. Но в примере лектора сильно показано: пользователь должен видеть не только агентов, а путь задачи.

Для нас первыми сценариями должны быть:

| Сценарий | Путь |
|---|---|
| Первый входящий запрос | `сайт / MAX / Telegram / email -> AI-менеджер -> Agent 3 -> Agent 5 -> Bitrix24 -> человек` |
| Контент даёт лид | `Agent 1 signal -> Agent 4 post -> public metrics -> inbound question -> Agent 5 analytics` |
| Тендерный лид | `Gmail tender -> Agent 2 -> Agent 3 -> Agent 5 -> Bitrix24 -> человек` |
| ROMI канала | `source -> cost -> lead -> deal -> revenue -> profit -> ROMI` |

Что добавить позже: отдельный локальный файл со сценариями, чтобы dashboard строил timeline не вручную из текста, а из структурированных данных.

### 4.2. Артефакты должны быть видны как результат работы

У лектора есть `Artifact node`: Brief, Strategy, Technical Specification, Design System, Frontend Build, Analytics Report.

Для нас артефакты должны быть другими:

| Агент | Артефакт |
|---|---|
| Agent 1 Scout | `SignalCard`, `source_card`, `competitor_signal` |
| Agent 2 Collector | `RawLead` |
| Agent 3 Processor | `QualifiedLead`, `score_reason`, `recommended_action` |
| Agent 4 Publisher | `content_draft`, `approval_card`, `published_content_event`, `public_metrics_attempt` |
| Agent 5 CRM | `crm_payload`, `bitrix_lead/deal`, `channel_report`, `romi_report` |
| Agent 6 Outreach | `approved_reply`, `outreach_lead`, `dialog_summary` |
| Checker | `agent_okr_contract_check.json`, `content_funnel_contract_check.json` |

Это важно: агент считается завершившим шаг только тогда, когда появился понятный артефакт.

### 4.3. Inspector должен показывать не только роль, но и блокер

В примере лектора при клике на агента справа видно: роль, обязанности, входы, выходы, tools, статус, пример задачи.

У нас в будущей панели надо показывать ещё:

- последний созданный артефакт;
- текущий блокер;
- можно ли запускать следующий шаг;
- были ли внешние вызовы;
- что нужно от Яники;
- где лежит результат.

Это сильнее, чем просто карточка агента.

### 4.4. Status model нужно использовать одинаково во всех местах

В примере есть состояния: `idle`, `queued`, `active`, `waiting`, `done`.

У нас уже есть похожие статусы, но они пока разрознены: `approved`, `ready`, `manual`, `locked`, `published_manual_unverified_public`.

Рекомендованный общий слой:

```text
locked
manual
draft
approval_ready
approved
queued
running
needs_review
failed
done
published_manual_unverified_public
```

Важно: не менять все файлы сразу. Сначала просто зафиксировать словарь статусов и применять его в новых карточках.

### 4.5. Scenario playback полезен позже, не сейчас

Анимация маршрута как у лектора полезна для будущей панели, но это не MVP.

Сейчас важнее:

- чтобы сценарий был записан;
- чтобы каждый шаг имел вход, выход и артефакт;
- чтобы checker мог сказать `OK / BLOCKED`;
- чтобы `REPORT.md` показывал один следующий шаг.

Визуальный playback можно делать после того, как 4 главных сценария будут структурированы в данных.

## 5. Что не нужно переносить

Не переносим:

- 9 департаментов как отдельную структуру;
- 35+ узлов ради красивой схемы;
- Design Department как отдельный агент в этой ветке;
- Development Department как лидогенерационный агент;
- Production Department как отдельного агента;
- отдельного Memory Manager, Context Router, Quality Arbiter как папки агентов;
- сложный UI до завершения локального dashboard/data-contract слоя.

Причина: для нашей цели важна не ширина системы, а чтобы первый лид проходил путь до CRM и аналитики.

## 6. Что добавить в ближайшую работу

Точечные улучшения:

1. Создать отдельный документ `agent-scenario-artifact-contract`: какие сценарии есть, какие шаги, какой артефакт закрывает шаг.
2. Добавить в dashboard понятие `last_artifact` и `blocker` для каждого агента.
3. Проверить, чтобы каждый новый post/lead/test создавал не просто запись в `REPORT.md`, а конкретный артефакт в `data/reports`, `content/pipeline` или CRM preview.

Что не делать сейчас:

- не писать React UI;
- не внедрять `@xyflow/react`;
- не делать анимации;
- не создавать новых агентов;
- не запускать внешние сервисы.

## 7. Один маленький следующий шаг

Создать без кода документ:

```text
docs/agent-scenario-artifact-contract.md
```

В нём описать 4 сценария:

1. первый входящий запрос;
2. контент даёт лид;
3. тендерный лид;
4. ROMI канала.

Для каждого сценария указать:

- вход;
- шаги;
- ответственный агент;
- артефакт;
- статус;
- как проверить;
- что запрещено запускать.

Это даст нам основу для будущей красивой панели, но без преждевременной разработки дизайна.
