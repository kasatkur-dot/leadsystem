# Agent 4 — Publisher

**СТАТУС: полезный контент-движок перенесён из `projects/sales_ai` в lead-engine.**

Дата начала переноса: 2026-05-06. Решение и план — `ТЗ_СЛИЯНИЕ_КОНТЕНТ_ДВИЖКА.md` в корне проекта.

Важно: старый `sales_ai` больше не является активным проектом после архивирования. В Agent 4 перенесены студийные функции, а курс/Jarvis/прогрев/лекции не переносились.

---

## Что делает

Постепенный конвейер генерации и публикации контента студии проектирования.

Уже есть:

- генерация текстового поста через OpenRouter;
- dry-run без API для проверки CLI;
- публикация готового Markdown-файла в Telegram-канал;
- Redis-bus: после успешной публикации — `PUBLISH content_published` и очередь `content:published` для Агента 5 (CRM);
- иллюстрации через DALL-E 3 (архитектурный визуальный язык, не курсовой/Jarvis);
- голосовая озвучка через ElevenLabs;
- видео-задание через Replicate;
- карусели 1080×1350, сторис 9:16 и стикеры через PIL;
- Instagram-адаптер через Postmypost с безопасным `dry-run`;
- MAX-публикация через официальный Bot API с безопасным `dry-run`;
- безопасные dry-run адаптеры VK и Дзен до подключения официальных API.

## Где какая логика

```
agents/agent4_publisher/
├── core/        внутренние сервисы: config, llm, image, voice, video, carousel, stories, stickers, event_bus
├── posters/     адаптеры каналов: telegram, instagram, max, vk, dzen
├── assets/      шрифты и фотоисточники
├── output/      сгенерированный контент по типам
└── cli.py       единая точка вызова: publish / generate
```

## Изначальная роль Agent 4

Agent 4 Publisher изначально назначался как **публикационные поверхности и точки доверия**, а не просто как технический постер.

Его зона:

- Avito-объявления;
- Яндекс Карты и 2GIS;
- Telegram-канал;
- VK-группа;
- Яндекс Дзен;
- MAX-канал и бот ПРОВЕРКА;
- региональные доски объявлений;
- сайт, лендинги, контент и доверительные материалы.

Важно: Agent 4 не является основным сборщиком сырых лидов. Он создаёт и обновляет поверхности, откуда лиды могут прийти. Сбор лидов и мониторинг делают Agent 2, Agent 6, Agent 1 и `source-radar`.

## Старые папки-плейсхолдеры

```text
avito_poster/
boards_poster/
content_pipeline/
dzen_poster/
maps_poster/
max_poster/
tg_poster/
vk_poster/
```

Эти пакеты оставлены на месте как roadmap-слоты будущих направлений. Их нельзя считать мусором: они фиксируют будущие публикационные поверхности Agent 4.

Как развивать без хаоса:

- текущая рабочая переиспользуемая логика живёт в `core/` и `posters/`;
- старые named-пакеты сохраняют понятную продуктовую карту каналов;
- если канал внедряется, добавляем конкретный код, dry-run, approval и правила безопасности;
- реальные публикации, обновления карточек и объявления не запускать без отдельного подтверждения Яники.

Контент-данные:

```
content/studio_brand/        база знаний бренда: системный промпт, страхи, профили клиентов
content/library/             готовые посты, шаблоны визуалов, реестры источников
content/by_channel/          адаптации под площадки
```

## Что не делать

- ❌ Не использовать курсовые/Jarvis/cyberpunk промпты — у студии другой визуальный язык.
- ❌ Не дублировать содержимое студийных `.md` в `posters/` или `core/`. Точка истины — `content/studio_brand/`.
- ❌ Не плодить FSM, формы, квизы — пишем как живой человек, лиды только добровольные (юридическое требование).
- ❌ Не публиковать одинаковый текст во все каналы — каждый канал получает свою адаптацию.

## Контракт с CRM

После успешной публикации `posters/*.publish()` вызывает `core.event_bus.publish_content_event(...)`,
который пишет JSON-сообщение в Redis Pub/Sub канал `content_published` и в очередь
`content:published`. Агент 5 читает очередь и логирует связку контент↔лид.

## Запуск

```bash
.venv/bin/python -m agents.agent4_publisher.cli generate post --topic "перепланировка с несущей стеной"
.venv/bin/python -m agents.agent4_publisher.cli generate post --topic "перепланировка с несущей стеной" --dry-run
.venv/bin/python -m agents.agent4_publisher.cli generate carousel --topic "5 ошибок при проектировании дома" --dry-run
.venv/bin/python -m agents.agent4_publisher.cli generate stories --topic "Что проверить перед реконструкцией" --dry-run
.venv/bin/python -m agents.agent4_publisher.cli publish telegram --file agents/agent4_publisher/output/posts/2026-05-06.md
.venv/bin/python -m agents.agent4_publisher.cli publish max --file agents/agent4_publisher/output/posts/2026-05-06.md --dry-run
.venv/bin/python -m agents.agent4_publisher.cli publish instagram --file agents/agent4_publisher/output/carousel/demo --dry-run
```

Для реальной публикации в MAX нужно заполнить в `.env`:

```bash
MAX_BOT_TOKEN=...
MAX_CHAT_ID=...
```

`MAX_BOT_TOKEN` берётся при создании бота в MAX. `MAX_CHAT_ID` — ID чата/канала, где бот имеет право отправлять сообщения.
