# Agent Subroles and KPI Map

Дата: 2026-05-17

Статус: рабочий слой управления по примеру лектора. Новые верхнеуровневые агенты не создавались. Суброли являются внутренними ролями внутри 6 существующих агентских департаментов.

## 1. Главное правило

В проекте остаётся 6 агентов:

```text
Agent 1 Scout
Agent 2 Collector
Agent 3 Processor
Agent 4 Publisher
Agent 5 CRM
Agent 6 Outreach
```

То, что у лектора показано как 35+ узлов, для нас раскладывается не в новые папки `agents/agent7_*`, а в суброли внутри этих 6 департаментов.

Простое правило:

```text
агент = владелец результата;
суброль = рабочая роль внутри агента;
skill = действие или навык;
артефакт = проверяемый результат этапа.
```

Новый агент можно создавать только позже и только если у роли есть отдельная очередь, отдельный владелец результата, отдельный риск, отдельные тесты и отдельный бюджет. Сейчас такого основания нет.

## 2. Суброли по агентам

| Агент | Суброль | Что делает | Главный артефакт |
|---|---|---|---|
| Agent 1 Scout | Market Research Agent | ищет рыночный спрос, темы и сегменты | `SignalCard` |
| Agent 1 Scout | Competitor Analyst | смотрит конкурентов, упаковку и публичные доказательства | `competitor_note` |
| Agent 1 Scout | Source Radar | находит новые каналы лидов и контента | `source_signal_card` |
| Agent 1 Scout | Reviews/Maps Monitor | анализирует карты, отзывы, вопросы клиентов | `review_signal` |
| Agent 1 Scout | Demand Signal Curator | отбирает полезные сигналы и решает, кому передать | `handoff_recommendation` |
| Agent 2 Collector | Tender/Email Collector | берёт лиды из почты и тендерных писем | `raw_lead` |
| Agent 2 Collector | Marketplace Collector | позже проверяет Avito, Profi, Яндекс Услуги по одному источнику | `marketplace_raw_lead` |
| Agent 2 Collector | Directory Collector | позже проверяет карты и каталоги | `directory_signal` |
| Agent 2 Collector | Lead Normalizer | приводит данные к формату `RawLead` | `normalized_raw_lead` |
| Agent 2 Collector | Duplicate Guard | отсеивает явные дубли до передачи дальше | `duplicate_decision` |
| Agent 3 Processor | Cleaner | чистит шум, мусор, оффтопик | `clean_lead` |
| Agent 3 Processor | Enricher | достаёт город, объект, площадь, контакт | `lead_enrichment` |
| Agent 3 Processor | Scorer | ставит `hot/warm/cold/off` и объясняет почему | `score_result` |
| Agent 3 Processor | Offer/Next-Step Architect | формирует оффер и следующий шаг | `qualified_lead` |
| Agent 3 Processor | QA Classifier | проверяет, не завышен ли score | `processor_quality_note` |
| Agent 4 Publisher | Content Strategist | выбирает рубрику, формат и место в воронке | `content_brief` |
| Agent 4 Publisher | Copywriter | пишет черновик без общих рекламных фраз | `content_draft` |
| Agent 4 Publisher | Editor | проверяет стиль, доказательства, запреты и разнообразие форматов | `editor_check` |
| Agent 4 Publisher | Visual/Media Brief Creator | готовит ТЗ на визуал, анимацию или видео позже | `media_brief` |
| Agent 4 Publisher | Approval Coordinator | держит статус согласования и причину правок | `approval_card` |
| Agent 4 Publisher | Content Metrics Analyst | позже связывает посты с метриками и лидами | `content_metric_event` |
| Agent 5 CRM | CRM Router | создаёт payload для Bitrix24 лида/сделки | `crm_payload_preview` |
| Agent 5 CRM | Notifier | уведомляет человека в Telegram после разрешённого теста | `notification_event` |
| Agent 5 CRM | Attribution Agent | сохраняет first_touch, last_touch, канал, UTM | `attribution_record` |
| Agent 5 CRM | ROMI Reporter | считает CPL, CAC, profit, ROMI | `channel_report` |
| Agent 5 CRM | CRM Hygiene Analyst | находит дубли, пустые поля, слабые карточки | `crm_hygiene_report` |
| Agent 5 CRM | Weekly Digest Owner | позже собирает недельный итог системы | `weekly_digest` |
| Agent 6 Outreach | Social Listening Monitor | ищет обсуждения, где можно помочь | `outreach_candidate` |
| Agent 6 Outreach | Candidate Qualifier | проверяет релевантность и риск спама | `outreach_decision` |
| Agent 6 Outreach | Reply Draft Writer | пишет человеческий ответ | `reply_draft` |
| Agent 6 Outreach | Approval Gatekeeper | не даёт отправлять без человека | `approval_required` |
| Agent 6 Outreach | Outreach Sender | отправляет только после отдельного approval | `sent_outreach_event` |
| Agent 6 Outreach | Dialog Converter | превращает заинтересованный ответ в `OutreachLead` | `outreach_lead` |

## 3. KPI по субролям

### Agent 1 Scout

| Суброль | KPI |
|---|---|
| Market Research Agent | не меньше 5 полезных рыночных сигналов в ручном радаре перед запуском нового источника |
| Competitor Analyst | у каждого важного конкурента есть ссылка, сегмент, сильная сторона и risk_notes |
| Source Radar | каждый новый источник имеет owner_agent, first_touch_channel и next_action |
| Reviews/Maps Monitor | отзывы и карты не копируются, а превращаются в боли, FAQ и темы |
| Demand Signal Curator | 100% готовых SignalCard имеют `recommended_action`, `handoff_to`, `risk_notes` |

### Agent 2 Collector

| Суброль | KPI |
|---|---|
| Tender/Email Collector | тестовый RawLead создаётся без потери source и raw_text |
| Marketplace Collector | каждый источник проверяется отдельно, не все платформы сразу |
| Directory Collector | собираются только разрешённые публичные сигналы, без серого парсинга |
| Lead Normalizer | 100% RawLead имеют `source`, `flow`, `raw_text`, `created_at` |
| Duplicate Guard | явные дубли не уходят в Agent 3 |

### Agent 3 Processor

| Суброль | KPI |
|---|---|
| Cleaner | оффтопик не попадает в CRM |
| Enricher | город, тип объекта, площадь и контакт заполняются, если они есть в тексте |
| Scorer | каждый score имеет объяснение `score_reason` |
| Offer/Next-Step Architect | каждый QualifiedLead имеет `recommended_action` |
| QA Classifier | после появления выборки ошибочные hot-лиды не выше 10% |

### Agent 4 Publisher

| Суброль | KPI |
|---|---|
| Content Strategist | у каждого материала есть формат, этап воронки и канал |
| Copywriter | посты не повторяют одну и ту же структуру; формат должен быть узнаваемо другим |
| Editor | 0 неподтверждённых обещаний, 0 общих фраз без фактов |
| Visual/Media Brief Creator | визуал/видео идут только как ТЗ или dry-run до approval |
| Approval Coordinator | 100% материалов имеют статус согласования, стоимость генерации и причину перегенерации при правках |
| Content Metrics Analyst | позже каждый опубликованный материал получает content_metric_event |

### Agent 5 CRM

| Суброль | KPI |
|---|---|
| CRM Router | payload создаётся локально до реальной отправки |
| Notifier | уведомления не содержат секретов и лишних персональных данных |
| Attribution Agent | 100% тестовых лидов имеют first_touch_channel и last_touch_channel |
| ROMI Reporter | каналы считаются по схеме spend -> leads -> deals -> revenue -> profit -> ROMI |
| CRM Hygiene Analyst | дубли и пустые поля попадают в очередь ручной чистки |
| Weekly Digest Owner | позже раз в неделю выдаёт лиды, CRM, контент, ROMI, блокеры |

### Agent 6 Outreach

| Суброль | KPI |
|---|---|
| Social Listening Monitor | кандидат не создаётся без URL/контекста и причины релевантности |
| Candidate Qualifier | 0 отправок по спорным кандидатам без escalation-to-yana |
| Reply Draft Writer | ответ полезный, не спамный, без давления |
| Approval Gatekeeper | 0 реальных отправок без approval |
| Outreach Sender | после разрешения пилотный лимит не больше 5 отправок в день |
| Dialog Converter | заинтересованный ответ превращается в OutreachLead и уходит в Agent 5 |

## 4. Когда суброль можно превратить в отдельный агент

Суброль можно повышать до отдельного агента только если одновременно выполнены условия:

- у неё свой стабильный вход;
- у неё свой проверяемый выход;
- у неё отдельная очередь или отдельный storage;
- она может ломаться независимо от родительского агента;
- у неё есть собственные KPI и тест;
- без отдельной папки система становится хуже, а не просто “красивее”.

До этого суброль остаётся внутри текущего агента.

## 5. Что делать сейчас

Сейчас внедряем только управленческий слой:

- зафиксировать суброли в документации;
- добавить их в локальный dashboard;
- добавить проверку checker;
- не запускать новые сервисы;
- не создавать Agent 7;
- не делать массовый сбор;
- не публиковать и не отправлять сообщения без отдельного подтверждения.

Следующий маленький шаг после этого документа: проверить, что `data/reports/agent_dashboard.md` и `data/reports/agent_dashboard.html` показывают суброли у каждого агента.
