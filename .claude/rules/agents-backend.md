---
paths:
  - "agents/**"
  - "orchestrator/**"
  - "shared/**"
  - "config/**"
  - "scripts/**"
  - "requirements.txt"
---

# Agents And Backend Rules

Перед работой с агентами и backend читать:

- `REPORT.md`;
- `tasks/roadmap.md`;
- `docs/claude-agent-architecture.md`;
- `docs/agent-okr-and-checker-map.md`;
- `docs/agent-system-gap-check.md`;

Правила:

- не переписывать всю систему, если меняется один агент;
- сначала определить конкретного агента, входы, выходы, зависимости и критерий проверки;
- внешние интеграции запускать только в dry-run или mock-режиме, если пользователь не подтвердил боевой запуск;
- не читать и не выводить реальные секреты из `.env`;
- после изменения агента обновить его README/правила, если изменилась роль или интерфейс.
