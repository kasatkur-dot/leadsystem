# Agent Dashboard API

Локальный safe backend для визуальной карты многоагентной системы.

Что делает:
- отдаёт frontend из `frontend/agent-system-visual`;
- читает `data/reports/agent_dashboard.json`;
- генерирует `/data.js`, который понимает текущий frontend;
- отдаёт `/api/dashboard` и `/api/agent-system-data`.
- принимает локальные preview-команды из чат/voice-пульта:
  - `POST /api/agent-control/chat`;
  - `POST /api/agent-control/voice`;
  - `POST /api/agent-control/image`;
  - `POST /api/agent-control/knowledge-search`.

Что не делает:
- не запускает Redis;
- не отправляет данные в Bitrix24;
- не отправляет Telegram;
- не запускает IMAP, scheduler или publisher;
- не вызывает OpenRouter/Whisper/image/embeddings, пока не включён отдельный live-режим.

Режимы:
- `LLM_RUNTIME_MODE=local_codex` — текущая разработка, backend строит только `task-handoff preview`;
- `LLM_RUNTIME_MODE=openrouter_free_test` — локальный тест до сервера, все текстовые LLM идут через одну free OpenRouter-модель;
- `LLM_RUNTIME_MODE=demo_server_free` — временный показ мастеру на сервере, все текстовые LLM идут через одну free OpenRouter-модель;
- `LLM_RUNTIME_MODE=production_server_router` — финальный серверный режим с разными моделями под задачи.

По умолчанию для локальной разработки `AGENT_CONTROL_LIVE_LLM=0`.
Для локального теста реального ответа модели использовать `LLM_RUNTIME_MODE=openrouter_free_test` и `AGENT_CONTROL_LIVE_LLM=1`.

Запуск:

```bash
.venv/bin/python -m backend.agent_dashboard_api.server --host 127.0.0.1 --port 8787
```
