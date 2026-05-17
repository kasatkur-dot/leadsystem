# Backlog будущих возможностей

Дата создания: 2026-05-16

Статус: обязательное место для идей `применим позже`.

## Правило

Если в ходе работы появляется идея, инструмент, внешний проект или механизм, который может пригодиться позже, но сейчас не внедряется, его нужно записать сюда.

Формат записи:

```text
Дата:
Название:
Источник:
Что дает:
Когда применять:
Почему не сейчас:
Риск:
Связанные файлы:
Статус:
```

Статусы:

```text
watch
later
partial_now
ready_to_test
rejected
applied
```

## 1. Postiz

Дата: 2026-05-16

Название: `Postiz`

Источник: `https://github.com/gitroomhq/postiz-app`

Проверка источника: 2026-05-16, GitHub repo найден как open-source/self-hosted social media scheduling tool.

Что дает:

- self-host social media scheduler;
- публикации во много каналов;
- analytics;
- API и агентные сценарии;
- полезен как будущий слой автопубликации.

Когда применять:

- после 1 месяца ручного цикла;
- после 10-20 опубликованных постов с нормальным трекингом;
- когда появится потребность планировать несколько каналов из одной панели.

Почему не сейчас:

- у нас еще не закрыт ручной MVP;
- MAX-канал и Bitrix24-цепочка важнее;
- нельзя плодить второй источник правды по публикациям.

Риск:

- сложность внедрения;
- ключи и OAuth;
- можно запустить автопостинг раньше, чем готов approval.

Связанные файлы:

- `content/pipeline/publication-tracker-mvp.csv`
- `content/pipeline/post-funnel-operating-system.md`

Статус: `later`

## 2. BrightBean Studio

Дата: 2026-05-16

Название: `BrightBean Studio`

Источник: `https://github.com/brightbeanxyz/brightbean-studio`

Что дает:

- idea board;
- календарь;
- очереди публикаций;
- approval workflows;
- audit trail;
- media library;
- social inbox.

Когда применять:

- если понадобится полноценная командная панель контента;
- если вручную станет сложно управлять несколькими каналами;
- если нужен клиентский/внутренний approval-интерфейс.

Почему не сейчас:

- проект большой;
- у нас уже есть Agent 4, Agent 5 и Bitrix24;
- сейчас достаточно CSV, Markdown и локального checker.

Риск:

- дублирование нашей архитектуры;
- интеграции с нужными российскими каналами могут потребовать доработок.

Связанные файлы:

- `content/pipeline/content-slot-matrix-mvp.md`
- `docs/content-approval-cycle.md`

Статус: `later`

## 3. TryPost

Дата: 2026-05-16

Название: `TryPost`

Источник: `https://github.com/trypost-it/trypost`

Проверка источника: 2026-05-16, GitHub repo найден как open-source social media scheduling platform.

Что дает:

- visual calendar;
- multi-platform composer;
- AI review;
- brand profile;
- REST API и MCP.

Когда применять:

- если нужен API/MCP слой для публикаций и calendar UI;
- если появится задача управлять публикациями через внешнюю панель.

Почему не сейчас:

- нам важнее лидовая воронка и CRM-связка;
- проект больше про scheduling, чем про монетизацию проектной организации.

Риск:

- AGPL-лицензия и обязательства при сетевом использовании;
- возможное дублирование Agent 4.

Связанные файлы:

- `content/pipeline/publication-tracker-mvp.csv`

Статус: `later`

## 4. LangChain Social Media Agent

Дата: 2026-05-16

Название: `LangChain Social Media Agent`

Источник: `https://github.com/langchain-ai/social-media-agent`

Проверка источника: 2026-05-16, GitHub repo найден как agent для sourcing, curating и scheduling social media posts с human-in-the-loop.

Что дает:

- sourcing;
- curation;
- human-in-the-loop;
- scheduling;
- agent inbox;
- бизнес-контекст для проверки релевантности.

Когда применять:

- если Agent 4 нужно усилить отдельным intake/curation workflow;
- если будем собирать контент из ссылок, видео и внешних источников чаще.

Почему не сейчас:

- требует много внешних сервисов и ключей;
- заточен под X/LinkedIn;
- у нас уже есть локальный контентный контур.

Риск:

- дорогие и внешние зависимости;
- лишняя сложность на MVP.

Связанные файлы:

- `agents/agent4_publisher/README.md`
- `content/pipeline/post-funnel-operating-system.md`

Статус: `partial_now`

## 5. Scenario Playback / Agent Graph UI из промпта лектора

Дата: 2026-05-17

Название: `Scenario Playback / Agent Graph UI`

Источник: учебный промпт лектора про визуализацию AI-компании с `AI Orchestrator`, департаментами, specialist nodes, artifact nodes и scenario playback.

Что дает:

- понятную визуальную карту системы;
- кликабельный inspector по агенту;
- timeline сценариев;
- видимые артефакты каждого шага;
- единый статус задачи: queued, active, waiting, done.

Когда применять:

- после того как 4 главных сценария будут описаны в `docs/agent-scenario-artifact-contract.md`;
- после стабильного read-only dashboard;
- до live-кнопок запуска, но после понятного data-contract.

Почему не сейчас:

- сейчас важнее первый лид, CRM, контентные метрики и безопасные dry-run;
- преждевременный React/UI может отвлечь от MVP;
- нельзя добавлять новые агенты ради красивой карты.

Риск:

- можно перепутать визуальную красоту с реальной работоспособностью;
- можно создать 35 узлов, которые не соответствуют файлам проекта;
- можно начать UI раньше, чем есть стабильные артефакты и статусы.

Связанные файлы:

- `docs/admin-dashboard-spec.md`
- `docs/multi-agent-visual-control-map.md`
- `docs/lecturer-mas-reference-comparison-2026-05-17.md`
- `data/reports/agent_dashboard.json`

Статус: `later`

Применено сейчас:

- human-in-the-loop approval;
- бизнес-контекст;
- sourcing -> curation -> draft -> approval как принцип.

## 5. Dittofeed

Дата: 2026-05-16

Название: `Dittofeed`

Источник: `https://github.com/dittofeed/dittofeed`

Проверка источника: 2026-05-16, GitHub repo и сайт Dittofeed описывают систему как open-source customer engagement platform.

Что дает:

- customer journeys;
- сегменты;
- рассылки и сообщения после событий;
- аналитика сообщений;
- self-host customer engagement.

Когда применять:

- когда появится база подписчиков/клиентов;
- когда нужно будет делать повторные касания после заявки;
- когда Bitrix24 alone станет недостаточно для nurturing.

Почему не сейчас:

- нет базы подписчиков и стабильного intake;
- сначала нужен Bitrix24 lead/deal поток.

Риск:

- сложность;
- PII и безопасность;
- дублирование CRM-коммуникаций.

Связанные файлы:

- `agents/agent5_crm/`
- `docs/site-bitrix24-channel-routing-table.md`

Статус: `later`

## 6. OpenPanel / PostHog-like analytics

Дата: 2026-05-16

Название: `OpenPanel`

Источник: `https://github.com/Openpanel-dev/openpanel`

Проверка источника: 2026-05-16, сайт OpenPanel описывает продукт как open-source analytics alternative to Mixpanel.

Что дает:

- funnel analytics;
- cohorts;
- dashboards;
- session replay;
- event alerts.

Когда применять:

- после публикации сайта и появления реального трафика;
- когда нужно смотреть путь `site visit -> click -> message -> lead -> deal`.

Почему не сейчас:

- сайт и CRM еще проходят MVP-связку;
- первый канал заявок пока MAX/Telegram/ручной контакт.

Риск:

- лишний аналитический слой до появления данных;
- нужно аккуратно работать с приватностью.

Связанные файлы:

- `site/`
- `agents/agent5_crm/analytics_reporter/`
- `data/channel_facts_mvp.csv`

Статус: `later`

## 7. Keeper.sh / календарная синхронизация

Дата: 2026-05-16

Название: `Keeper.sh`

Источник: `https://github.com/ridafkih/keeper.sh`

Что дает:

- синхронизация календарей;
- MCP для календаря;
- source -> destination mapping;
- чистка устаревших событий.

Когда применять:

- если появится реальный календарь публикаций и созвонов;
- если нужно синхронизировать publication slots, консультации и напоминания.

Почему не сейчас:

- публикации пока ручные;
- календарь можно держать в CSV/Markdown.

Риск:

- лишняя инфраструктура;
- календарные права и приватные события.

Связанные файлы:

- `content/pipeline/content-slot-matrix-mvp.md`
- `content/pipeline/publication-tracker-mvp.csv`

Статус: `later`
