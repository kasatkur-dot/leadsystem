---
paths:
  - "data/**"
  - "data/reports/**"
  - "docs/admin-dashboard-spec.md"
  - "docs/chief-of-staff-handoff-protocol.md"
---

# Data And Reports Rules

Перед работой с данными и отчетами читать:

- `REPORT.md`;
- `data/README.md`;
- `data/reports/README.md`;
- `docs/admin-dashboard-spec.md`;

Правила:

- не коммитить operational CRM test artifacts, Bitrix lead IDs, токены, session-файлы и runtime-логи;
- `data/reports/bitrix_close_test_lead_*.json` оставлять только локально;
- отчеты должны показывать: источник, статус, следующий шаг, риск, метрики и дату обновления;
- перед внешней публикацией проверять чувствительные данные;
- после изменения dashboard/report обновить `REPORT.md`.

