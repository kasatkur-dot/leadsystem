# Технологические стыки, MCP и skills для многоагентной системы

Дата: 2026-05-06

Статус: карта реализации. Новые агенты не создавались, skills не устанавливались, платные API не запускались, реальные публикации не выполнялись.

## 1. Главный вывод

Для всей системы нужен не один большой "суперагент", а понятные технологические стыки между уже существующими 6 агентскими отделами.

Главная цепочка:

```text
источник -> raw lead -> Redis -> обработка -> qualified lead -> CRM -> уведомление -> сделка -> аналитика -> следующий цикл
```

Контентная цепочка:

```text
foresight -> research -> monthly plan -> Agent 4 dry-run -> review -> approved -> publish later -> content_published -> Agent 5 analytics
```

## 2. Обязательные технологические стыки

| Стык | Что соединяет | Где в проекте | Статус |
|---|---|---|---|
| `.env` / secrets | Проект с внешними сервисами | `.env.example`, `docs/env-fill-checklist.md` | Нужны реальные значения, секреты не показывать |
| Redis queues | Агентов между собой | `shared/redis_client.py` | Нужен запущенный Redis |
| DB / PostgreSQL | Лиды, дубли, логи, будущая аналитика | `shared/db.py`, `DATABASE_URL` | `DATABASE_URL` уже предусмотрен |
| LLM router | Agent 3, Agent 4, Agent 6 и visual control с выбранной моделью | `shared/llm_client.py`, `config/settings.py`, `backend/agent_dashboard_api/agent_control.py` | 4 режима: `local_codex`, `openrouter_free_test`, `demo_server_free`, `production_server_router` |
| Chat/voice agent control | Управление агентами через интерфейс без закрытия графа | `frontend/agent-system-visual/*`, `backend/agent_dashboard_api/server.py` | Dry-run в `local_codex`; локальный free-тест в `openrouter_free_test`; показ мастеру в `demo_server_free`; production-модели только позже |
| Content event bus | Agent 4 -> Agent 5 | `content_published`, `content:published` | Есть, проверять после Redis |
| CRM bridge | Agent 5 -> Bitrix24 | `agents/agent5_crm/bitrix/` | Нужен `BITRIX24_WEBHOOK_URL` |
| Manager notifications | Agent 5/6 -> Telegram bot | `agents/agent5_crm/notifier/`, `agents/agent6_outreach/approver/` | Нужен `TELEGRAM_BOT_TOKEN` |
| Telegram user sessions | Agent 6 monitor/sender | `scripts/auth_telegram_session.py`, `data/*.session` | Нужны две сессии, не коммитить |
| Content approval | Agent 4 -> человек -> Agent 4 | `docs/content-approval-cycle.md`, `content/pipeline/*` | Документы есть |
| ROMI analytics | Agent 5 -> отчеты | `agents/agent5_crm/analytics_reporter/`, `data/channel_*_mvp.csv` | CSV MVP есть |
| GitHub safety | Код/документы -> GitHub без секретов | `.gitignore`, `AGENTS.md`, `REPORT.md` | Есть правила, перед push проверять |

## 3. Какие MCP-серверы нужны

### Уже доступны в текущей среде

| MCP / plugin | Зачем системе | Когда использовать |
|---|---|---|
| Context7 | Свежая документация по библиотекам, API, SDK | Когда меняем интеграции, Supabase, Redis, OpenRouter, Python-библиотеки |
| GitHub | Репозиторий, PR, CI, безопасная передача проекта | Перед коммитом, push, PR, проверкой чужого репозитория |
| Google Drive | Документы, таблицы, материалы курса, клиентские Google Docs/Sheets | Когда надо читать/создавать Google Docs или Sheets |
| Supabase | Проверка и управление Supabase-проектом | Позже, когда `DATABASE_URL` переводим на Supabase Postgres |
| Browser Use | Безопасная настройка через браузер, QA страниц, личные кабинеты под контролем Яники | Только без платных действий и без публикаций |
| node_repl | Быстрые JS-проверки, обработка JSON, прототипы dashboard | Когда нужен JS без создания проекта |

### MCP/интеграции, которые могут понадобиться позже

| MCP / интеграция | Зачем | Статус решения |
|---|---|---|
| Bitrix24 MCP или устойчивый REST-клиент | CRM-лиды, сделки, задачи, поля UTM | Сейчас достаточно webhook/REST в Agent 5; MCP искать позже |
| Telegram MCP не обязателен | У нас уже есть Telethon и bot API код | Сначала проверить текущий код и сессии |
| Apify MCP / mcpc | Reels Radar, конкурентный анализ, lead scraping по лимитам | Только после бюджета и лимита 5-10 записей |
| PostMyPost интеграция | Автопубликация в соцсети | Отложено до ручного цикла и dry-run |
| Dashboard / BI | Экран как у лектора: канал -> лид -> сделка -> выручка -> ROMI | Сначала CSV/Markdown, потом dashboard |
| Email/Gmail API | Тендерные письма | На MVP можно IMAP/Gmail app password; API позже |

## 4. Что говорит Supabase

По Context7/Supabase: Supabase даёт Postgres database, Auth, Storage, Realtime, Edge Functions и другие сервисы. Для нашего проекта сейчас важнее всего использовать его как PostgreSQL-базу через `DATABASE_URL`. Storage, Realtime, Auth и Edge Functions оставить на потом.

Простое решение:

```text
сейчас: Redis + локальные CSV + DATABASE_URL
позже: Supabase Postgres как основная база
ещё позже: Storage для файлов, Realtime для dashboard, Auth для веб-интерфейса
```

Источник: Context7 по `/supabase/supabase`.

## 5. Уже установленные skills

### Локальные и системные

| Skill | Польза |
|---|---|
| `find-skills` | Искать новые skills под конкретных агентов |
| `context7-mcp` | Проверять свежую документацию |
| `skill-creator` | Создавать свои skills, если внешних не хватит |
| `skill-installer` | Устанавливать skills после согласования |
| `openai-docs` | Работа с OpenAI-документацией |
| `imagegen` | Генерация визуалов |
| `pdf` | Чтение и подготовка PDF |
| `playwright` | Браузерная автоматизация и QA |
| `web-design-guidelines` | Проверка интерфейсов |
| `vercel-react-best-practices` | React/Next.js позже для dashboard |
| `vercel-composition-patterns` | Архитектура компонентов позже |

### Skills из активных plugins

| Skill group | Польза |
|---|---|
| `github:*` | GitHub workflow, PR, CI, публикация изменений |
| `google-drive:*` | Google Docs, Sheets, Slides, Drive |
| `supabase:*` | Supabase и Postgres best practices |
| `browser-use:browser` | QA и безопасная настройка через браузер |
| `spreadsheets` | CSV/XLSX-отчеты, таблицы, метрики |
| `documents` | DOCX-документы |
| `presentations` | Презентации |
| `hyperframes:*` | Видео/анимации позже, не для MVP |

## 6. Кандидаты skills для будущего

Проверено через `find-skills` workflow и поиск по skills.sh. `npx skills find` в текущей shell-сессии не вернул результат вовремя, поэтому кандидаты зафиксированы как внешние, не установленные.

| Направление | Skill-кандидат | Зачем | Решение сейчас |
|---|---|---|---|
| Telegram bot | `sickn33/antigravity-awesome-skills/telegram-bot-builder` | Архитектура Telegram-бота, команды, кнопки, webhook | Не ставить сейчас; сначала проверить текущие bot/Telethon-модули |
| Web scraping | `mindrally/skills/web-scraping` | Этичный scraping, rate limit, Playwright, BeautifulSoup | Не ставить до выбора одного источника |
| Apify scraping | `apify/agent-skills/apify-ultimate-scraper` | 55+ платформ, конкуренты, Reels, Maps | Только после бюджета и лимитов |
| Apify lead gen | `apify/agent-skills/apify-lead-generation` | Lead scraping через Actors | Отложить, риск платных запусков |
| Dashboard | `anthropics/knowledge-work-plugins/interactive-dashboard-builder` | HTML/JS dashboard как у лектора | Полезно после первого CSV-отчета |
| Firecrawl | `firecrawl/cli/firecrawl` | Markdown-выгрузка страниц, search/scrape/crawl | Только для research, не массово |
| Scraper builder | `jwynia/agent-skills/scraper-builder` | Site-specific scraper на Playwright/TS | Позже, когда выбран конкретный сайт |

Источники:

- `https://skills.sh/sickn33/antigravity-awesome-skills/telegram-bot-builder`
- `https://skills.sh/mindrally/skills/web-scraping`
- `https://skills.sh/apify/agent-skills/apify-ultimate-scraper`
- `https://skills.sh/apify/agent-skills/apify-lead-generation`
- `https://skills.sh/anthropics/knowledge-work-plugins/interactive-dashboard-builder`
- `https://skills.sh/firecrawl/cli/firecrawl`
- `https://skills.sh/jwynia/agent-skills/scraper-builder`

## 7. Что нужно каждому агенту

| Агент | Технологический минимум | MCP/skills позже |
|---|---|---|
| Agent 1 Scout | Research-файлы, источники, ручные таблицы | Browser Use, Context7, web-scraping, Firecrawl, Apify позже |
| Agent 2 Collector | Один источник, Redis `leads:raw`, `RawLead` | Gmail/API, Apify только после лимита, Playwright для QA |
| Agent 3 Processor | `shared/models.py`, `shared/llm_client.py`, Redis | Context7 для LLM SDK, тестовые fixtures |
| Agent 4 Publisher | Monthly plan, dry-run, review statuses, content files | imagegen, spreadsheets, dashboard skill позже, PostMyPost отложен |
| Agent 5 CRM | Bitrix webhook, Telegram bot, analytics CSV, `content_id` | Supabase, Google Sheets, dashboard builder |
| Agent 6 Outreach | Telethon sessions, approver, sender, relevance | Telegram bot skill позже, Browser Use только для настройки |

## 8. Что не ставить и не подключать сейчас

- Не ставить Apify skills до бюджета и лимитов.
- Не подключать PostMyPost.
- Не подключать все collectors одновременно.
- Не делать отдельный Telegram MCP, пока текущий Telethon-код не проверен.
- Не делать dashboard до первого нормального отчёта `channel_report_mvp.csv`.
- Не создавать Agent 7.

## 9. Ближайший маленький шаг

Сначала закрыть текущий dry-run контента:

```text
content-2026-05-001 -> полноценный текст вручную или через выбранный LLM -> review -> needs_changes/approved
```

Только потом возвращаться к техническим интеграциям:

```text
.env -> Redis -> один тестовый лид -> Agent 3 -> Agent 5 -> отчет
```
