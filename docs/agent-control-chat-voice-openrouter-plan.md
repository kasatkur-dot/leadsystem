# Agent Control: чат, голос и маршрутизация моделей

Документ фиксирует серверный слой управления агентами через визуальный интерфейс.

## Четыре режима работы

### Режим 1 — сейчас, разработка через Codex

Это самый безопасный режим разработки:

- управление разработкой идёт через текущий Codex-чат и подписку;
- backend продукта не вызывает OpenRouter;
- `LLM_PROVIDER=dry_run`;
- `AGENT_CONTROL_LIVE_LLM=0`;
- чат/voice-пульт в интерфейсе строит только preview: какой агент, какая задача, какой handoff, какой следующий шаг.

Он нужен, чтобы можно было менять код и структуру без внешних LLM-вызовов.

### Режим 2 — локальный OpenRouter free test

Это текущий тестовый режим, если нужно, чтобы локальный интерфейс уже отвечал моделью, но без серверного деплоя.

- `LLM_RUNTIME_MODE=openrouter_free_test`;
- `LLM_PROVIDER=openrouter`;
- `AGENT_CONTROL_LIVE_LLM=1`;
- `LLM_MODEL_DEMO_FREE=deepseek/deepseek-v4-flash:free`;
- все текстовые LLM-задачи принудительно идут через одну бесплатную модель;
- Redis, Bitrix24, Telegram, scheduler, publisher, голос, картинки и embeddings отдельно не включаются.

Этот режим подходит для проверки чата `привет -> ответ модели` внутри локального dashboard.

### Режим 3 — демо-сервер для мастера через бесплатную OpenRouter-модель

Это временный режим, чтобы показать работающую систему мастеру на сервере.

- `LLM_RUNTIME_MODE=demo_server_free`;
- `LLM_PROVIDER=openrouter`;
- `AGENT_CONTROL_LIVE_LLM=1`;
- `LLM_MODEL_DEMO_FREE=deepseek/deepseek-v4-flash:free`;
- все текстовые LLM-задачи принудительно идут через одну бесплатную модель;
- дорогие модели разработки/маркетинга/production не используются;
- голос, картинки и embeddings лучше оставить в `dry_run`, если не нужно показывать именно их реальную работу.

Для этого режима создан шаблон `.env.demo-server-free.example`.

### Режим 4 — позже, финальный серверный продукт через OpenRouter

Когда продукт будет развёрнут на сервере, включается отложенный механизм:

- `LLM_RUNTIME_MODE=production_server_router`;
- `LLM_PROVIDER=openrouter`;
- `AGENT_CONTROL_LIVE_LLM=1`;
- модели выбираются по задачам через `.env`;
- секреты хранятся только в серверных переменных окружения;
- перед включением проверяются model IDs, лимиты и стоимость.

Именно для этого режима ниже сохранена маршрутизация DeepSeek / MiniMax / Opus / Google Flash / Whisper / embeddings / image.

## Что добавлено сейчас

- В интерфейсе агентской карты есть нижняя панель `Chat / voice command center`.
- Панель не перекрывает визуализацию агентов: граф остаётся в отдельной основной области, чат находится в нижнем dock-блоке.
- Сервер визуализации получил безопасные локальные endpoints:
  - `POST /api/agent-control/chat`
  - `POST /api/agent-control/voice`
  - `POST /api/agent-control/image`
  - `POST /api/agent-control/knowledge-search`
- По умолчанию endpoints работают как `dry-run`: строят preview, но не вызывают OpenRouter, Whisper, image-модели, embeddings, Redis, Bitrix24, Telegram, scheduler или publisher.

## Серверная маршрутизация моделей

Основной принцип серверного режима: агент не должен быть привязан к подписке. Модель выбирается через `.env`, а код агентов обращается к общему роутеру.

В режимах `openrouter_free_test` и `demo_server_free` все текстовые строки ниже фактически подменяются на `LLM_MODEL_DEMO_FREE`, чтобы тест или показ мастеру не включили дорогие модели.

| Задача | Переменная | Текущий маршрут |
|---|---|---|
| Обычные дешевые задачи | `LLM_MODEL_DEFAULT_FREE` | `deepseek/deepseek-v4-flash:free` |
| Управление агентами | `LLM_MODEL_AGENT_CONTROL` | `minimax/minimax-2.7` |
| Разработка | `LLM_MODEL_DEVELOPMENT` | `anthropic/claude-opus-4.7` |
| Маркетинговые тексты | `LLM_MODEL_MARKETING` | `google/gemini-2.5-flash` |
| База знаний | `LLM_MODEL_KNOWLEDGE` | `deepseek/deepseek-v4-flash:free` |
| Голос | `WHISPER_PROVIDER`, `WHISPER_MODEL` | local Whisper / `whisper-1` |
| Картинки в чат | `IMAGE_MODEL_PROVIDER`, `IMAGE_MODEL` | route for Kling/Nano Banana-compatible model |
| Поиск по базе знаний | `EMBEDDING_PROVIDER`, `EMBEDDING_MODEL` | Gemini/OpenAI-compatible embedding route |

Model ID нужно проверять в каталоге OpenRouter перед реальным серверным запуском. Если OpenRouter меняет название модели, меняется только `.env`, а не код агентов.

## Как работает команда

1. Пользователь пишет или диктует задачу.
2. Интерфейс отправляет команду в локальный endpoint.
3. Backend определяет режим: управление, разработка, маркетинг, база знаний или картинка.
4. Backend выбирает модельный маршрут.
5. Backend формирует `task-handoff preview`.
6. Реальная отправка во внешний LLM не выполняется, пока `AGENT_CONTROL_LIVE_LLM=0`.
7. После реального выполнения результат должен фиксироваться в `REPORT.md`.

## Что включать позже

- Реальное OpenRouter-управление локально: только в режиме `openrouter_free_test` и только на бесплатной модели.
- Реальное OpenRouter-управление для демо: только в режиме `demo_server_free` и только на бесплатной модели.
- Реальное OpenRouter-управление для production: только после перехода к `production_server_router`, проверки `OPENROUTER_API_KEY`, model IDs и стоимости.
- Голос: подключить локальный Whisper или внешний transcription endpoint.
- Картинки: выбрать фактическую модель генерации, проверить стоимость и ограничения.
- База знаний: подключить Supabase/Postgres pgvector или локальный индекс, затем embeddings.
- Серверный deploy: вынести секреты в серверные переменные окружения, не в frontend.

## Что нельзя делать автоматически

- Не отправлять реальные клиентские данные в LLM без отдельного решения.
- Не публиковать контент из чата без подтверждения человека.
- Не запускать Redis/scheduler/Bitrix24/Telegram из визуального пульта без явного действия.
- Не показывать API-ключи в интерфейсе, логах или отчётах.
