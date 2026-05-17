# Docs Navigation

Эта папка хранит проектные регламенты, планы, аудиты и рабочие спецификации `design-studio-lead-engine`.

Перед изменениями сначала читать:

1. `../REPORT.md` — последняя точка сверки.
2. `../tasks/roadmap.md` — более свежая карта реализации backend/agents.
3. `../tasks/session-notes.md` — подробная история последних запусков.

## Что читать по задачам

- Модульные правила Claude Code по зонам проекта: `../.claude/rules/site.md`, `../.claude/rules/agents-backend.md`, `../.claude/rules/content.md`, `../.claude/rules/data-reports.md`, `../.claude/rules/security.md`.
- Claude/агентные стартовые правила: `claude-project-rules.md`, `claude-agent-architecture.md`, `claude-content-strategy.md`.
- Сайт и публичная упаковка: `new-site-structure.md`, `new-site-design-brief.md`, `site-design-upgrade-plan.md`, `site-selling-geo-audit-2026-05-07.md`, `site-visual-assets-safe-review.md`.
- Многоагентная система: `multi-agent-visual-control-map.md`, `agent-okr-and-checker-map.md`, `agent-system-gap-check.md`, `lesson-05-working-model-lead-chain.md`.
- Лидогенерация и поток лида: `lesson-5-lead-engine-launch-plan.md`, `lead-flow-warframing.md`, `content-approval-cycle.md`, `max-publication-runbook.md`.
- Dashboard и управление: `admin-dashboard-spec.md`, `chief-of-staff-handoff-protocol.md`.
- Безопасность и ключи: `secret-handling-policy.md`, `env-fill-checklist.md`, `mcp-api-docs-preflight.md`.
- GEO/AI visibility: `geo-ai-source-of-truth.md`.

## Статус документов

- `secret-handling-policy.md`, `env-fill-checklist.md`, `mcp-api-docs-preflight.md` — служебные правила. Не вставлять реальные токены в эти файлы.
- Документы с `draft`, `audit`, `plan`, `brief` в названии считать рабочими материалами до явного утверждения в `REPORT.md`.
- Если документ содержит слово `черновик`, не использовать его как финальную инструкцию без сверки с `REPORT.md`.

## Правила

- Ничего не удалять и не переносить без отдельного подтверждения.
- Оригинальные клиентские/коммерческие материалы не хранить здесь, если им место в `/Users/yanika/Documents/Вайбкодинг/База_знаний`.
- При конфликте между документами приоритет такой: `REPORT.md` -> `tasks/roadmap.md` -> профильный документ из `docs/` -> старые `tasks/tasks.md`.
