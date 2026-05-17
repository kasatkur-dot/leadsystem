# Lead Intelligence Pipeline — ООО «Вектор Плюс-Про»

`CLAUDE.md` — короткий стартовый оркестратор проекта. Большие правила вынесены в отдельные файлы, чтобы не превращать этот файл в простыню и не тратить контекст без необходимости.

## Первый вход

Перед любой задачей сначала читать:

1. `REPORT.md` — актуальное состояние, последние решения и следующий шаг.
2. `tasks/save-plan-2026-05-12.md` — если задача про сохранение, commit, deploy или разбор накопленных изменений.
3. `tasks/stabilization-checkpoint-2026-05-12.md` — если задача про checkpoint/готовность блоков.
4. `tasks/roadmap.md` — если задача про backend, агентов, MVP или дальнейшую разработку.
5. `agents/Агент безопастности/AGENT_SECURITY.md` — если задача затрагивает секреты, внешние сервисы, CRM, публикации, deploy, MCP/API, LLM-вызовы, платежи, массовый сбор или реальные пользовательские данные.

Не начинать работу по старым `tasks/tasks.md`, если есть более свежие `REPORT.md` и `tasks/roadmap.md`.

## Подключаемые правила

@docs/claude-project-rules.md

Дополнительно в проекте есть `.claude/rules/` с короткими правилами по зонам. Они нужны, чтобы не раздувать этот файл и подгружать правила только там, где они нужны:

- `.claude/rules/site.md`;
- `.claude/rules/agents-backend.md`;
- `.claude/rules/content.md`;
- `.claude/rules/data-reports.md`;
- `.claude/rules/security.md`.

Security Agent Control Layer: `agents/Агент безопастности/AGENT_SECURITY.md`. Это не седьмой продуктовый агент, а файл управления безопасностью для всех 6 агентских отделов, checker/dashboard и будущих интеграций.

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
- Контент и публикации: `docs/claude-content-strategy.md`, `content/README.md`, `content/pipeline/published-log.md`, `content/pipeline/post-funnel-operating-system.md`, `content/pipeline/publication-tracker-mvp.csv`.
- Агенты и backend: `docs/claude-agent-architecture.md`, `docs/agent-okr-and-checker-map.md`, `docs/agent-system-gap-check.md`, `tasks/roadmap.md`.
- Dashboard/reports: `data/README.md`, `data/reports/README.md`.
- Секреты и ключи: `docs/secret-handling-policy.md`, `.env.example`.
- Безопасность агентов и интеграций: `agents/Агент безопастности/AGENT_SECURITY.md`, `.claude/rules/security.md`, `docs/security-agent-control-layer.md`.
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

## Карта 6 агентских отделов

- `agents/agent1_scout/` — разведка источников, конкурентов и рыночных сигналов.
- `agents/agent2_collector/` — безопасный сбор RawLead из разрешённых источников.
- `agents/agent3_processor/` — очистка, квалификация, скоринг и следующий шаг по лиду.
- `agents/agent4_publisher/` — контент, доверие, сайт, dry-run публикации и future content events.
- `agents/agent5_crm/` — Bitrix24, Telegram-уведомления, CRM и сквозная аналитика.
- `agents/agent6_outreach/` — первое касание и outreach только через approval человека.
- `agents/Агент безопастности/AGENT_SECURITY.md` — контрольный слой безопасности для всех агентов; не считается Agent 7 и не запускается как продуктовый агент.

## Саб-агенты проекта

Саб-агентов Claude Code использовать только для экономии контекста, read-only расследований и точечной проверки. Не создавать новых продуктовых агентов без отдельного решения: в проекте уже есть 6 агентских отделов.

- `Explore` / read-only: поиск по `site/`, `docs/`, `agents/`, `tasks/`, сверка файлов, карт и текущих изменений.
- `code-reviewer`: проверка кода после правок, особенно `site/`, `agents/`, `shared/`, `orchestrator/`.
- `architecture-validator`: проверка границ модулей, агентских отделов, Redis/CRM handoff и новых правил.
- `checker/QA`: сверка `docs/agent-okr-and-checker-map.md`, `data/reports/`, `scripts/check_agent_okr_contract.py`, без создания Agent 7.

Правило write-zones: если несколько агентов работают параллельно, заранее разделить зоны (`site/`, `agents/backend/`, `docs/research/`, `content/`, `data/reports/`). Один файл не должен редактироваться несколькими агентами одновременно.

Итоги заметных проверок и саб-агентов фиксировать в `REPORT.md` или `tasks/session-notes.md`.

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
3. Если деталей много, короткий итог оставить в `REPORT.md`, а подробности вынести в `tasks/session-notes.md`.
4. Если изменены правила или структура, обновить профильный README/документ.
5. Сказать, что закрыто, что осталось и какой один следующий маленький шаг.

## Правило будущих возможностей

Если в работе появляется идея, инструмент или внешний проект, который `можно применить позже`, записать его в:

```text
content/pipeline/future-opportunities-backlog.md
```

Не оставлять такие идеи только в чате. Для каждой записи указать: источник, что дает, когда применять, почему не сейчас, риск и статус.
