# Safe Save Batch 2 — Dashboard Demo

Дата: 2026-05-17

Назначение: подготовить следующий безопасный набор файлов для локального commit без push.

Важно: этот файл не выполняет commit и не отправляет изменения на GitHub. Это только список для проверки перед сохранением.

## Что можно добавить в batch 2

### Frontend визуализации

```text
frontend/agent-system-visual/README.md
frontend/agent-system-visual/app.jsx
frontend/agent-system-visual/data.js
frontend/agent-system-visual/graph.jsx
frontend/agent-system-visual/index.html
frontend/agent-system-visual/panels.jsx
frontend/agent-system-visual/preview.png
frontend/agent-system-visual/preview2.png
frontend/agent-system-visual/preview3.png
frontend/agent-system-visual/styles.css
```

Почему можно: это рабочая копия визуального интерфейса, уже подключённая к backend/dashboard.

### Dashboard reports

```text
data/.gitkeep
data/reports/.gitkeep
data/reports/agent_dashboard.json
data/reports/agent_dashboard.md
data/reports/agent_dashboard.html
data/reports/agent_dashboard_product_test_2026-05-17.json
data/reports/agent_dashboard_product_test_2026-05-17.md
data/reports/agent_okr_contract_check.json
data/reports/content_funnel_contract_check.json
```

Почему можно: это read-only dashboard/test artifacts без запуска внешних сервисов.

### Текущие продолжения Codex/Claude

```text
scripts/start-server.sh
tasks/claude-code-continuation-2026-05-17.md
tasks/safe-save-batch-2-dashboard-demo-2026-05-17.md
```

Почему можно: это безопасный старт демо и карта продолжения работы.

## Что пока не добавлять

```text
Многоагентная система-визуал/
```

Почему: это исходный локальный оригинал, его не удалять, но в Git лучше не добавлять. Рабочая версия уже лежит в `frontend/agent-system-visual`.

```text
data/reports/agent3_*.json
data/reports/agent4_*.md
data/reports/agent5_*.json
data/reports/first_inbound_*.json
data/reports/lead-post-*.json
data/reports/max_b2b_*.md
data/reports/openrouter_provider_config.json
data/reports/vpp_ai_manager_dry_run/
```

Почему: это полезные локальные результаты, но перед публичным commit их нужно отдельно проверить на чувствительные данные и смысл для репозитория.

## Проверка перед commit

1. Показать пользователю список файлов batch 2.
2. Проверить, что `.env`, session-файлы, logs, credentials и реальные CRM/Telegram artifacts не попадают в `git add`.
3. Сделать commit только после отдельного подтверждения.
4. Push в `main` делать только после отдельного подтверждения.

## Следующий маленький шаг

Показать пользователю batch 2 и получить подтверждение на локальный commit без push.
