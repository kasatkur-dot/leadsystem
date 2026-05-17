# OpenRouter Free Local Test Mode

Цель: проверить, что локальный visual dashboard уже может отвечать настоящей моделью OpenRouter без серверного деплоя.

## Когда использовать

Использовать, когда нужно быстро проверить чат управления агентами:

```text
пользователь -> Chat / voice command center -> backend -> OpenRouter free model -> ответ в интерфейсе
```

Этот режим не включает Redis, Bitrix24, Telegram, scheduler, publisher, публикации, массовый сбор, голос, картинки или embeddings.

## Настройки

```text
LLM_RUNTIME_MODE=openrouter_free_test
LLM_PROVIDER=openrouter
AGENT_CONTROL_LIVE_LLM=1
LLM_MODEL_DEMO_FREE=deepseek/deepseek-v4-flash:free
OPENROUTER_API_KEY=заполнить_локально
```

Все текстовые маршруты в этом режиме принудительно используют `LLM_MODEL_DEMO_FREE`.
Это защищает от случайного включения дорогих моделей `Opus`, `MiniMax` или `Google Flash` во время локального теста.

## Что проверить

- `OPENROUTER_API_KEY` имеет статус `SET`.
- Каталог OpenRouter содержит `LLM_MODEL_DEMO_FREE`.
- `/data.js` показывает `runtime_mode=openrouter_free_test`.
- `/api/agent-control/chat` возвращает `provider=openrouter`.
- Ответ содержит `llm_status=OK`.

## Что нельзя

- Не отправлять реальные клиентские данные.
- Не публиковать контент из чата.
- Не запускать CRM/Telegram/Redis/scheduler из этого теста.
- Не записывать ключ OpenRouter в документы, отчёты, README или git.

## Связь с другими режимами

| Режим | Для чего |
|---|---|
| `local_codex` | разработка через Codex, backend `dry_run` |
| `openrouter_free_test` | локальный тест ответа модели до сервера |
| `demo_server_free` | показ мастеру на сервере через free model |
| `production_server_router` | финальный сервер с task-specific моделями |
