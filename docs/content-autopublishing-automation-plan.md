# План полной автоматизации выпуска и публикации постов

Дата: 2026-05-16

Статус: план внедрения. Автопубликация не включена.

## Цель

Сделать так, чтобы контент работал как система:

```text
идея -> план -> черновик -> проверка -> утверждение -> расписание -> публикация -> аналитика -> следующий пост
```

Главное правило: автоматизация не должна публиковать случайный текст. Публиковать можно только материал со статусом `approved` или `scheduled`.

## Что уже есть

| Блок | Где | Статус |
|---|---|---|
| План постов | `content/pipeline/content-plan-10-posts-lead-mvp-2026-05.md` | есть |
| Трекер публикаций | `content/pipeline/publication-tracker-mvp.csv` | есть |
| Трекер откликов | `content/pipeline/topic-response-tracker-mvp.csv` | есть |
| Воронки и офферы | `content/pipeline/post-funnel-*.csv`, `offer-readiness-map-mvp.csv` | есть |
| Проверка контракта | `scripts/check_content_funnel_contract.py` | есть |
| Agent 4 контент-движок | `agents/agent4_publisher/` | есть |
| MAX publisher | `agents/agent4_publisher/posters/max.py` | есть, запускать только через dry-run до отдельного разрешения |
| Telegram publisher | `agents/agent4_publisher/posters/telegram.py` | есть |
| Событие публикации | Redis `content_published` и `content:published` | есть |
| Agent 5 аналитика | `agents/agent5_crm/analytics_reporter/` | есть MVP |

## Этап 1. Безопасная полуавтоматизация

Что делаем первым:

1. Agent 4 берет ближайший пост со статусом `planned`.
2. Делает черновик в `content/pipeline/drafts/`.
3. Проверяет стоп-правила: повторы, CTA, оффер, длинное тире, кавычки, обещания результата.
4. Ставит статус `review`.
5. Яника вручную утверждает или просит переделать.
6. После утверждения статус становится `approved`.

Что нельзя:

- не публиковать автоматически;
- не использовать платные API без разрешения;
- не отправлять одинаковый текст во все каналы.

## Этап 2. Approved-only публикация

После проверки этапа 1 можно включать первый технический publisher.

Порядок:

1. Сначала MAX.
2. Потом Telegram.
3. Потом VK.
4. Потом Дзен.

Правило запуска:

```text
status = approved
channel = MAX
publisher = dry-run OK
env keys = SET
manual confirmation = yes
```

Только после этого можно делать реальную публикацию.

## Этап 3. Расписание публикаций

Когда manual approval стабильно работает, добавляем статус `scheduled`.

Поля, которые нужны в `publication-tracker-mvp.csv`:

```text
planned_date
scheduled_at
published_date
published_url
publisher_status
publisher_error
```

Если публикация не прошла, статус не должен теряться. Нужна запись ошибки и повтор только после проверки.

## Этап 4. Связь с лидами и ROMI

После публикации Agent 4 отправляет событие:

```text
content_id
channel
published_url
funnel_arc
funnel_stage
offer_id
main_cta
published_at
```

Agent 5 должен связать:

```text
пост -> канал -> вопрос -> лид -> сделка -> выручка -> ROMI
```

Минимальные метрики:

- просмотры;
- реакции;
- вопросы;
- присланные планы;
- лиды;
- квалифицированные лиды;
- сделки;
- выручка;
- решение `scale`, `keep`, `rewrite`, `pause`.

## Этап 5. Полная автоматизация месяца

Полный цикл можно включать только после 10-20 ручных публикаций с нормальным учетом.

Тогда система должна сама:

1. Собирать идеи из Agent 1, вопросов клиентов, комментариев и конкурентов.
2. Ставить темы в месячный план.
3. Делать черновики.
4. Отправлять на approval.
5. После approval ставить в расписание.
6. Публиковать в нужный канал.
7. Собирать метрики.
8. Предлагать следующий месяц по фактическим данным.

## Что нужно сделать ближайшим шагом

Не включать полную автоматизацию сразу.

Ближайший правильный шаг:

```text
сделать approved-only dry-run публикации lead-post-001 в MAX
```

То есть система должна показать, что она умеет взять утвержденный файл, проверить статус `approved`, подготовить публикацию и остановиться перед реальной отправкой.

Безопасная команда MVP:

```bash
.venv/bin/python scripts/dry_run_agent4_max_approved_publication.py --content-id lead-post-001
```

Что делает команда:

1. Читает `content/pipeline/publication-tracker-mvp.csv`.
2. Проверяет, что `lead-post-001` имеет `status=approved`.
3. Проверяет, что канал `MAX`.
4. Проверяет, что `source_file` существует.
5. Извлекает только блок `Пост для ручной публикации`.
6. Запускает MAX publisher только с `dry_run=True`.
7. Пишет отчет в `data/reports/lead-post-001_max_approved_dry_run.json`.

MAX API при этом не вызывается.

## Что понадобится в `.env`

Значения секретов не показывать. Проверять только `SET` или `EMPTY`.

Для MAX:

```text
MAX_BOT_TOKEN
MAX_CHAT_ID
```

Для Telegram:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHANNEL_ID
```

Для аналитики и CRM:

```text
BITRIX24_WEBHOOK_URL
OPENROUTER_API_KEY
REDIS_URL
```

## Стоп-правила полной автоматизации

Автоматизация должна остановиться, если:

- статус поста не `approved` или `scheduled`;
- не заполнен `content_id`;
- нет `funnel_arc`, `offer_id`, `main_cta`;
- checker вернул ошибку;
- канал не настроен;
- `.env` ключи `EMPTY`;
- текст повторяет недавнюю тему;
- есть персональные данные;
- есть обещание гарантированного согласования;
- публикация уже есть в `published-log.md`.

## Future opportunities

Если ручной цикл станет тяжелым, смотреть:

- `content/pipeline/future-opportunities-backlog.md`;
- Postiz для self-host scheduling;
- TryPost для calendar/API/MCP;
- BrightBean Studio для approval-интерфейса;
- OpenPanel для аналитики сайта;
- Dittofeed для цепочек повторных касаний.

Пока это не внедрять. Сначала закрыть approved-only dry-run для MAX.
