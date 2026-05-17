# ENV Fill Checklist

Дата: 2026-05-06

Назначение: безопасно закрыть недостающие `.env` поля для первого MVP-запуска.

Главное правило: секреты не повторяются в ответах и не попадают в отчеты, README, правила, логи, скриншоты или GitHub.

Если Яника намеренно передает токен/API-ключ для локальной настройки, агент принимает его спокойно и сохраняет только локально: `.env`, `.env.local`, gitignored `secrets/`, `~/.config/yanika-secrets/` или macOS Keychain.

## Как записывать ключи

### Вариант А — Яника вводит сама в терминале

Открыть обычный терминал Mac в папке проекта:

```bash
cd "/Users/yanika/Documents/Вайбкодинг/Codex/2026-04-20-cloude-code/projects/design-studio-lead-engine"
```

Для каждого секрета запускать:

```bash
.venv/bin/python scripts/set_env_secret.py ИМЯ_КЛЮЧА
```

Скрипт попросит значение, не покажет его на экране и запишет в `.env`.

### Вариант Б — Яника передает ключ агенту для локальной настройки

Агент:

- не повторяет значение;
- не пишет значение в `REPORT.md`, `README.md`, `CLAUDE.md`, `AGENTS.md`, `tasks/session-notes.md` или логи;
- сохраняет только локально;
- после записи показывает только `SET` / `EMPTY`.

## Что блокирует MVP сейчас

| Ключ | Статус | Где взять | Куда записать |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | `EMPTY` | Anthropic Console, раздел API keys | `.venv/bin/python scripts/set_env_secret.py ANTHROPIC_API_KEY` |
| `TELEGRAM_BOT_TOKEN` | `EMPTY` | Telegram `@BotFather`; если токен уже был в чате, перевыпустить | `.venv/bin/python scripts/set_env_secret.py TELEGRAM_BOT_TOKEN` |
| `TELEGRAM_API_HASH` | `EMPTY` | `https://my.telegram.org/apps` | `.venv/bin/python scripts/set_env_secret.py TELEGRAM_API_HASH` |
| `BITRIX24_WEBHOOK_URL` | `EMPTY` | Bitrix24, раздел для разработчиков, входящий webhook | `.venv/bin/python scripts/set_env_secret.py BITRIX24_WEBHOOK_URL` |
| `IMAP_HOST` | `EMPTY` | для Яндекс.Почты: `imap.yandex.ru` | `.venv/bin/python scripts/set_env_secret.py IMAP_HOST` |
| `IMAP_PORT` | `EMPTY` | для Яндекс.Почты: `993` | `.venv/bin/python scripts/set_env_secret.py IMAP_PORT` |
| `GMAIL_USER` | `EMPTY` | рабочий email, где лежат тендерные письма; для Яндекса это полный адрес `...@yandex.ru` | `.venv/bin/python scripts/set_env_secret.py GMAIL_USER` |
| `GMAIL_APP_PASSWORD` | `EMPTY` | пароль приложения от почты; для Яндекса создаётся в Яндекс ID | `.venv/bin/python scripts/set_env_secret.py GMAIL_APP_PASSWORD` |
| `DATABASE_URL` | `EMPTY` | локальный PostgreSQL или Supabase Postgres connection string | `.venv/bin/python scripts/set_env_secret.py DATABASE_URL` |

## Что уже есть для MVP

| Ключ | Статус |
|---|---|
| `TELEGRAM_MANAGER_CHAT_ID` | `SET` |
| `TELEGRAM_API_ID` | `SET` |
| `TELEGRAM_PHONE` | `SET` |
| `GMAIL_TENDER_FOLDER` | `SET` |
| `REDIS_URL` | `SET` |
| `APP_ENV` | `SET` |

## Agent 4 / публикации

Это не должно блокировать первый сбор лидов, но понадобится для публикаций.

| Ключ | Статус | Комментарий |
|---|---|---|
| `MAX_API_BASE_URL` | `SET` | публичный адрес API уже добавлен |
| `MAX_BOT_TOKEN` | `EMPTY` | нужен токен MAX-бота |
| `MAX_CHAT_ID` | `EMPTY` | нужен ID чата/канала MAX |
| `OPENROUTER_API_KEY` | `EMPTY` | нужен для реальной генерации текстов Agent 4 |
| `PUBLISHER_TELEGRAM_BOT_TOKEN` | `EMPTY` | нужен для публикации в Telegram-канал |
| `PUBLISHER_TELEGRAM_CHANNEL_ID` | `EMPTY` | нужен ID Telegram-канала |

## Платные или отложенные ключи

Пока не заполнять без отдельного решения по бюджету:

- `OPENAI_API_KEY`
- `ELEVENLABS_API_KEY`
- `ELEVENLABS_VOICE_ID`
- `REPLICATE_API_TOKEN`
- `POSTMYPOST_TOKEN`
- `POSTMYPOST_PROJECT_ID`
- `POSTMYPOST_INSTAGRAM_ACCOUNT_ID`

## Что может сделать ассистент

- проверить `.env` только по `SET / EMPTY / MISSING`;
- добавить пустые поля без секретов;
- проверить Redis после заполнения базовых ключей;
- запустить авторизацию Telegram-сессий, когда `TELEGRAM_API_HASH` будет `SET`;
- проверить Bitrix24 только безопасным read/status, если webhook заполнен.

## Что должен сделать человек

- войти в личные кабинеты;
- создать или перевыпустить ключи;
- вставить секреты локально в `.env` или намеренно передать агенту для локального сохранения;
- не отправлять ключи в публичные документы, GitHub, скриншоты или чужие чаты.

## Официальные точки входа

- Telegram API ID/hash: `https://core.telegram.org/api/obtaining_api_id`
- Telegram Bot API / BotFather: `https://core.telegram.org/bots/api`
- Bitrix24 webhooks: `https://helpdesk.bitrix24.com/open/21133100/`
- Яндекс.Почта IMAP: `https://m.yandex.ru/support/yandex-360/customers/mail/ru/mobile-mail`
- Яндекс ID, пароли приложений: `https://yandex.ru/support/id/ru/authorization/app-passwords`
- Gmail app passwords, если позже будет Gmail: `https://support.google.com/mail/answer/185833`
- Anthropic Console: `https://console.anthropic.com/`
- OpenRouter API keys: `https://openrouter.ai/docs/api-keys`
- Supabase Postgres connection strings: `https://supabase.com/docs/reference/postgres/connection-strings`
