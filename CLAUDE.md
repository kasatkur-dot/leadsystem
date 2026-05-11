# Lead Intelligence Pipeline — ООО «Вектор Плюс-Про»

`CLAUDE.md` — короткий стартовый оркестратор проекта. Большие правила вынесены в отдельные файлы, чтобы не превращать этот файл в простыню и не тратить контекст без необходимости.

## Первый вход

Перед любой задачей сначала читать:

1. `REPORT.md` — актуальное состояние, последние решения и следующий шаг.
2. `tasks/save-plan-2026-05-12.md` — если задача про сохранение, commit, deploy или разбор накопленных изменений.
3. `tasks/stabilization-checkpoint-2026-05-12.md` — если задача про checkpoint/готовность блоков.
4. `tasks/roadmap.md` — если задача про backend, агентов, MVP или дальнейшую разработку.

Не начинать работу по старым `tasks/tasks.md`, если есть более свежие `REPORT.md` и `tasks/roadmap.md`.

## Подключаемые правила

@docs/claude-project-rules.md

## Запуск и проверки

```bash
.venv/bin/python -m orchestrator.scheduler
.venv/bin/python -m pytest tests/
redis-cli ping
```

Без отдельного подтверждения не запускать:

- боевые публикации;
- Bitrix24-обновления;
- Telegram/MAX/VK/Instagram отправку;
- деплой;
- commit/push;
- платные API.

## Что читать по типу задачи

- Сайт: `site/README.md`, `docs/new-site-structure.md`, `docs/new-site-design-brief.md`, `docs/geo-ai-source-of-truth.md`, `docs/site-design-upgrade-plan.md`.
- Контент и публикации: `docs/claude-content-strategy.md`, `content/README.md`, `content/pipeline/published-log.md`.
- Агенты и backend: `docs/claude-agent-architecture.md`, `docs/agent-okr-and-checker-map.md`, `docs/agent-system-gap-check.md`, `tasks/roadmap.md`.
- Dashboard/reports: `data/README.md`, `data/reports/README.md`.
- Секреты и ключи: `docs/secret-handling-policy.md`, `.env.example`.
- Agent 4 Publisher: `ТЗ_СЛИЯНИЕ_КОНТЕНТ_ДВИЖКА.md`, `agents/agent4_publisher/README.md`.

## Короткая карта проекта

- `agents/` — агентные отделы лидогенерации, контента, CRM и аутрича.
- `orchestrator/` — технический запускатель MVP-цепочки.
- `shared/` — общие модели, Redis, DB и логгер.
- `site/` — публичный сайт/лендинг.
- `content/` — контентная база и pipeline публикаций.
- `docs/` — регламенты, аудиты, спецификации.
- `research/` — исследования источников лидов, GEO/AI, рынка и архитектуры.
- `data/reports/` — read-only dashboard и отчёты.

## Главные запреты

- Не удалять и не переносить оригиналы без явного разрешения.
- Не коммитить и не публиковать `.env`, session-файлы, токены, credentials, логи, screenshots/output и operational CRM test artifacts.
- Не использовать одинаковый контент во всех каналах.
- Не подключать формы/CRM/Bitrix24/публикации без отдельного подтверждения.
- Не переписывать всю систему, если сломан один агент.

## Правило завершения работы

После заметного изменения:

1. Проверить результат минимальной безопасной командой.
2. Обновить `REPORT.md`.
3. Если изменены правила или структура, обновить профильный README/документ.
4. Сказать, что закрыто, что осталось и какой один следующий маленький шаг.
