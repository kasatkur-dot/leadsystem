# Data Navigation

Эта папка хранит локальные данные проекта `design-studio-lead-engine`.

## Что здесь есть

- `channel_costs_mvp.csv` — расходы по каналам для MVP-аналитики.
- `channel_facts_mvp.csv` — факты по лидам, встречам, сделкам и выручке.
- `reports/` — локальные отчёты, тестовые JSON-снимки и read-only dashboard.
- `*.session` — локальные runtime-сессии Telegram/Telethon. Их нельзя коммитить, копировать в отчёты или переносить наружу.

## Правила

- Перед анализом dashboard сначала читать `../REPORT.md`, затем `reports/README.md`.
- Реальные сессии, токены, cookie, webhook, ключи и логи не публиковать и не переносить.
- `reports/agent_dashboard.*` можно пересобирать локально только read-only скриптами из `scripts/build_agent_dashboard*.py`.
- Любой запуск, который может обратиться к Redis, Bitrix24, Telegram, IMAP, LLM, scheduler или publisher, требует отдельного подтверждения.
