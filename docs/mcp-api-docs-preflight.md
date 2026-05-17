# MCP/API/docs-preflight для lead-engine

Дата: 2026-05-07

Статус: preflight перед разработкой и запуском. Значения секретов не читались и не выводились. Проверка `.env` сделана только статусами `SET` / `EMPTY`.

## 1. Главное правило

Перед подключением нового источника или сервиса делаем короткую проверку:

```text
что подключаем -> зачем -> кто агент-владелец -> какие API/MCP/docs нужны -> какие токены нужны -> что платное -> какой первый dry-run
```

Нельзя сразу запускать весь сбор или все платформы одновременно.

## 2. `.env` статусы

### Первый CRM/MVP-путь

| Поле | Статус | Зачем |
|---|---|---|
| `APP_ENV` | `SET` | Режим работы |
| `REDIS_URL` | `SET` | Очереди между агентами |
| `DATABASE_URL` | `SET` | PostgreSQL/Supabase через URL |
| `TELEGRAM_MANAGER_CHAT_ID` | `SET` | Куда слать уведомления менеджеру |
| `TELEGRAM_BOT_TOKEN` | `EMPTY` | Telegram-уведомления и approval |
| `BITRIX24_WEBHOOK_URL` | `EMPTY` | Создание лида/сделки в Bitrix24 |
| `ANTHROPIC_API_KEY` | `EMPTY` | Сильная модель для Agent 3/ответов, если не dry-run |
| `OPENROUTER_API_KEY` | `EMPTY` | Бюджетные/альтернативные модели |

### LLM-router настройки в `.env`

| Поле | Статус | Комментарий |
|---|---|---|
| `LLM_PROVIDER` | `EMPTY` | В коде есть default `anthropic`, но в `.env` явно не задан |
| `LLM_MODEL_ANALYSIS` | `EMPTY` | В коде есть default, но в `.env` явно не задан |
| `LLM_MODEL_REPLY` | `EMPTY` | В коде есть default, но в `.env` явно не задан |
| `LLM_MODEL_CONTENT` | `EMPTY` | В коде есть default, но в `.env` явно не задан |

### Telegram user account / Agent 6

| Поле | Статус | Зачем |
|---|---|---|
| `TELEGRAM_API_ID` | `SET` | Telethon user account |
| `TELEGRAM_API_HASH` | `EMPTY` | Telethon user account |
| `TELEGRAM_PHONE` | `SET` | Телефон аккаунта |

### Email IMAP / tender_collector

`GMAIL_*` — исторические имена переменных. Их можно использовать и для Яндекс.Почты, если задан `IMAP_HOST=imap.yandex.ru`.

| Поле | Статус | Зачем |
|---|---|---|
| `IMAP_HOST` | `EMPTY` | IMAP-сервер почты; для Яндекса `imap.yandex.ru` |
| `IMAP_PORT` | `EMPTY` | IMAP-порт; обычно `993` |
| `GMAIL_USER` | `EMPTY` | Почта с тендерами |
| `GMAIL_APP_PASSWORD` | `EMPTY` | Пароль приложения почты |
| `GMAIL_TENDER_FOLDER` | `SET` | Папка с тендерными письмами |

### Agent 4 / отложенные публикации и генерации

| Поле | Статус | Решение |
|---|---|---|
| `MAX_API_BASE_URL` | `SET` | База MAX API, не секрет |
| `MAX_BOT_TOKEN` | `EMPTY` | Позже, для MAX |
| `MAX_CHAT_ID` | `EMPTY` | Позже, для MAX |
| `PUBLISHER_TELEGRAM_BOT_TOKEN` | `EMPTY` | Позже, для публикаций |
| `PUBLISHER_TELEGRAM_CHANNEL_ID` | `EMPTY` | Позже, для публикаций |
| `OPENAI_API_KEY` | `EMPTY` | Позже, изображения |
| `ELEVENLABS_API_KEY` | `EMPTY` | Позже, озвучка |
| `ELEVENLABS_VOICE_ID` | `EMPTY` | Позже, озвучка |
| `REPLICATE_API_TOKEN` | `EMPTY` | Позже, видео |
| `POSTMYPOST_TOKEN` | `EMPTY` | Позже, автопостинг |
| `POSTMYPOST_PROJECT_ID` | `EMPTY` | Позже, автопостинг |
| `POSTMYPOST_INSTAGRAM_ACCOUNT_ID` | `EMPTY` | Позже, автопостинг |
| `AVITO_CLIENT_ID` | `EMPTY` | Позже, Avito |
| `AVITO_CLIENT_SECRET` | `EMPTY` | Позже, Avito |
| `PROXY_URL` | `EMPTY` | Только если понадобится |

## 3. MCP и skills

| Инструмент | Статус | Для чего нужен |
|---|---|---|
| Context7 MCP | Доступен | Проверять актуальную документацию библиотек/API перед кодом |
| GitHub plugin | Доступен | Репозиторий, PR, безопасная передача проекта |
| Supabase plugin | Доступен | Будущая проверка Supabase-проекта и таблиц, если используем Supabase глубже `DATABASE_URL` |
| Browser Use | Доступен | Безопасная настройка кабинетов и QA, без самостоятельного извлечения паролей |
| Google Drive plugin | Доступен | Документы/таблицы, если понадобится отчёт или база знаний |
| find-skills / skill-installer | Доступны локально | Искать и устанавливать skills только после отдельного решения |

Что пока не подключаем:

- новый MCP для Apify;
- PostMyPost;
- HiggsField;
- ElevenLabs;
- CapCut/video stack;
- массовые web scraping инструменты.

## 4. API-preflight по агентам

| Агент | API/сервис | Документация перед кодом | Токен | Платность | Первый безопасный тест |
|---|---|---|---|---|---|
| Agent 1 Scout | публичные источники, карты, конкуренты | правила источника и robots/terms вручную | не всегда нужен | зависит от источника | 3-5 ручных записей в watchlist |
| Agent 2 Collector | Email IMAP, сейчас Яндекс.Почта | пароль приложения / IMAP справка почтового провайдера | нужен | обычно нет | 1 тестовое письмо в папке |
| Agent 2 Collector | Avito API | официальная Avito developer docs | нужен | может быть | dry-run без заявок |
| Agent 3 Processor | LLM-router | Anthropic/OpenRouter docs | нужен, если не dry-run | да/может быть | один тестовый лид в dry_run |
| Agent 5 CRM | Bitrix24 REST | официальная Bitrix24 REST/webhook docs конкретного портала | нужен | зависит от тарифа | создать тестовый лид в sandbox/тестовой воронке |
| Agent 5 Notifier | Telegram Bot API / python-telegram-bot | Context7 проверен | нужен | нет | отправить тестовое уведомление себе |
| Agent 5 Analytics | PostgreSQL/Supabase, CSV | Context7 Supabase проверен | `DATABASE_URL` уже `SET` | зависит от Supabase | записать 1 тестовую строку отчёта |
| Agent 6 Outreach | Telethon / Telegram API | Telethon + Telegram API docs | нужен | нет | авторизация session, без отправки сообщений |
| Agent 4 Publisher | MAX Bot API | официальная MAX Bot API docs | нужен | неизвестно | dry-run публикации |
| Agent 4 Publisher | OpenAI/ElevenLabs/Replicate/PostMyPost | официальные docs каждого сервиса | нужен | да | не запускать до решения бюджета |

## 5. Docs-preflight: что уже сверено через Context7

| Тема | Context7 library | Что проверено |
|---|---|---|
| Telegram bot notifications | `/python-telegram-bot/python-telegram-bot` | token через BotFather, `ApplicationBuilder`, polling/webhook, handlers, отправка сообщений |
| Redis queues | `/redis/docs` | подключение redis-py, connection pooling, retries/backoff, Redis Streams, consumer groups, acknowledge |
| Supabase/PostgreSQL | `/supabase/supabase` | connection strings, pooler/direct URL, переменные `DATABASE_URL`, local/hosted подход |

## 6. Docs-preflight: что проверить перед реальной разработкой

| Сервис | Что проверить |
|---|---|
| Bitrix24 | REST webhook, создание лида/сделки, поля CRM, тестовая воронка, лимиты |
| Telegram API / Telethon | авторизация user account, session-файлы, ограничения отправки, безопасность аккаунта |
| Email IMAP, сейчас Яндекс.Почта | пароль приложения, IMAP включен, папка тендеров, лимиты чтения |
| MAX Bot API | отправка сообщений/постов, chat/channel id, лимиты, права бота |
| Avito | OAuth/client credentials, доступные endpoints, лимиты, правила площадки |
| OpenRouter/Anthropic | модели, стоимость, rate limits, fallback `dry_run` |
| Sentry/logging | события по агентам, маскирование секретов, не отправлять полный `.env` или сырые персональные данные |

## 7. Безопасность

Проверено:

```text
.env -> игнорируется git
secrets/ -> игнорируется git
credentials/ -> игнорируется git
*.session -> игнорируется git
logs/ -> игнорируется git
*.jsonl -> игнорируется git
```

Правило:

```text
В REPORT.md, README, CLAUDE.md и docs пишем только SET/EMPTY, не значения.
```

## 8. Первый маленький тест после preflight

Пока не запускать весь `orchestrator/scheduler.py`.

Когда обязательные поля будут `SET`, порядок такой:

1. Проверить Redis отдельно.
2. Создать один тестовый сырой лид.
3. Прогнать только Agent 3.
4. Прогнать только Agent 5 в тестовую CRM/уведомление.
5. Проверить, что источник попал в аналитику.
6. Обновить `REPORT.md`.

Статус: не закрыто, потому что `TELEGRAM_BOT_TOKEN`, `BITRIX24_WEBHOOK_URL` и ключ LLM для не-dry-run пока `EMPTY`.
