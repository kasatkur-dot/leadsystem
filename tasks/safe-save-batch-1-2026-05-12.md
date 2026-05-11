# Safe Save Batch 1 - 2026-05-12

Назначение: первая публично-безопасная партия файлов для сохранения в репозитории `kasatkur-dot/leadsystem`.

Важно: репозиторий GitHub публичный. Поэтому внутренние рабочие отчёты, локальные настройки, runtime-файлы и operational artifacts не включать.

## Статус проверки

Проверено:

- remote: `https://github.com/kasatkur-dot/leadsystem.git`;
- visibility: `PUBLIC`;
- секреты/API-ключи/private key/webhook values в этой партии не найдены;
- явные email/телефоны в этой партии не найдены;
- `git add --dry-run` проходит по выбранному списку.
- Batch 1 поставлена в Git stage командой `git add`; commit/push/deploy не выполнялись.
- После staging проверено: `git diff --cached --check` без ошибок, секретов и явных email/телефонов в staged-файлах не найдено.

## Включить в Batch 1

```bash
git add \
  .gitignore \
  AGENTS.md \
  CLAUDE.md \
  README.md \
  .env.example \
  docs/README.md \
  docs/secret-handling-policy.md \
  docs/claude-project-rules.md \
  docs/claude-content-strategy.md \
  docs/claude-agent-architecture.md \
  research/README.md \
  content/README.md \
  data/README.md \
  data/reports/README.md \
  tasks/roadmap.md \
  tasks/stabilization-checkpoint-2026-05-12.md \
  tasks/final-stabilization-checkpoint-2026-05-12.md \
  tasks/save-plan-2026-05-12.md \
  tasks/safe-save-batch-1-2026-05-12.md \
  OPEN_SITE.command \
  'ТЗ_СЛИЯНИЕ_КОНТЕНТ_ДВИЖКА.md'
```

## Не включать в Batch 1

```text
REPORT.md
tasks/session-notes.md
MCP_SETUP_RESULT.md
data/reports/bitrix_close_test_lead_*.json
.env
.env.*
CLAUDE.local.md
.claude/settings.local.json
logs/
output/
.playwright-cli/
.playwright-mcp/
*.session
*.jsonl
```

## Почему `REPORT.md` не включаем

`REPORT.md` остаётся локальной памятью Codex/Claude и первой точкой входа в проект, но в публичный GitHub его не добавляем, потому что он содержит внутренние рабочие заметки, историю решений и отдельные публичные контакты/ссылки компании.

Для защиты добавлено правило `.gitignore`:

```gitignore
REPORT.md
```

## Следующий шаг

Batch 1 уже находится в stage. Следующий шаг — только после отдельного подтверждения пользователя:

```bash
git commit -m "chore: add project safety and navigation docs"
```

`git push` выполнять только отдельным подтверждением после commit.
