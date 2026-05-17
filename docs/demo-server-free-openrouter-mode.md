# Demo Server Free OpenRouter Mode

Цель: временно выложить систему на сервер, чтобы мастер мог посмотреть работающий интерфейс и управление агентами.

## Когда использовать

Использовать только для показа и проверки системы мастером.

Не использовать для финальной production-версии и не использовать для основной разработки. Для локального теста до сервера есть отдельный режим `openrouter_free_test`.

## Суть режима

В демо режиме все текстовые LLM-задачи идут через одну бесплатную модель OpenRouter.

```text
LLM_RUNTIME_MODE=demo_server_free
LLM_PROVIDER=openrouter
AGENT_CONTROL_LIVE_LLM=1
LLM_MODEL_DEMO_FREE=deepseek/deepseek-v4-flash:free
```

Это значит:

- Agent Control Chat может отвечать через OpenRouter;
- дорогие модели Opus / MiniMax / Google Flash не используются;
- все маршруты `development`, `marketing`, `agent_control`, `knowledge`, `analysis`, `reply`, `content` принудительно получают одну free-модель;
- после показа мастеру можно вернуться к Codex-разработке.

## Что нужно на сервере

1. Скопировать `.env.demo-server-free.example` в серверный `.env`.
2. Заполнить `OPENROUTER_API_KEY` только на сервере.
3. Проверить актуальность `LLM_MODEL_DEMO_FREE` в каталоге OpenRouter.
4. Оставить `WHISPER_PROVIDER=dry_run`, `IMAGE_MODEL_PROVIDER=dry_run`, `EMBEDDING_PROVIDER=dry_run`, если не нужно показывать их реальную работу.
5. Не включать Bitrix24, Telegram, Redis-сбор, publisher и реальные публикации для просмотра мастером без отдельного решения.

## Чем отличается от других режимов

| Режим | Для чего | LLM |
|---|---|---|
| `local_codex` | текущая разработка | Codex/подписка, backend `dry_run` |
| `openrouter_free_test` | локальный тест чата до сервера | OpenRouter free model для всех текстовых задач |
| `demo_server_free` | показать мастеру на сервере | OpenRouter free model для всех текстовых задач |
| `production_server_router` | финальный продукт | OpenRouter с разными моделями под задачи |

## Что проверить перед показом мастеру

- `/api/health` возвращает `status=OK`.
- `/data.js` показывает `runtime_mode=demo_server_free`.
- `/api/agent-control/chat` возвращает `provider=openrouter`.
- Все выбранные route-модели равны `LLM_MODEL_DEMO_FREE`.
- Внешние CRM/публикации выключены, если мастер смотрит только систему управления.

## Что не делать

- Не использовать реальные клиентские данные.
- Не включать дорогие модели.
- Не включать публикации.
- Не отправлять лиды в Bitrix24, если это только демонстрация.
- Не хранить `OPENROUTER_API_KEY` в репозитории.
