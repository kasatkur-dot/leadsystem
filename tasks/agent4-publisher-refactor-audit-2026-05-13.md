# Agent 4 Publisher Refactor Audit - 2026-05-13

Цель: проверить, можно ли принять удаление старых пустых пакетов Agent 4 Publisher, и затем уточнить решение после проверки изначальной роли агента.

Это не commit, не `git add`, не push и не deploy.

## Проверено

- 8 удалённых старых `__init__.py` в `agent4_publisher/*_poster/` и `content_pipeline/`;
- новая структура `agents/agent4_publisher/core/`;
- новая структура `agents/agent4_publisher/posters/`;
- импорты на старые пути;
- syntax/import-check.

## Результат

Старые файлы:

- `avito_poster/__init__.py`;
- `boards_poster/__init__.py`;
- `content_pipeline/__init__.py`;
- `dzen_poster/__init__.py`;
- `maps_poster/__init__.py`;
- `max_poster/__init__.py`;
- `tg_poster/__init__.py`;
- `vk_poster/__init__.py`.

Все они были `0 bytes`, то есть не содержали рабочей логики.

Новая структура:

- `core/` - генерация, конфиг, LLM, визуалы, карусели, stories, voice, video, stickers, event_bus;
- `posters/` - адаптеры публикации: `telegram.py`, `max.py`, `vk.py`, `dzen.py`, `instagram.py`;
- `cli.py` - единая точка запуска `generate` / `publish`.

Проверки:

- Python files: `18`;
- syntax errors: `0`;
- `import agents.agent4_publisher` - OK;
- `import agents.agent4_publisher.cli` - OK;
- `python -m agents.agent4_publisher.cli --help` - OK;
- missing internal imports: `0`.

## Важное уточнение

Пустые старые папки можно не восстанавливать, но смысл задач из них нельзя терять.

Эти каналы нужны для будущей работы:

- Avito;
- региональные доски;
- Яндекс Карты / 2GIS;
- Telegram;
- VK;
- MAX;
- Дзен;
- контентный пайплайн.

Новая договорённость:

- публикации и обновления площадок развивать через `agents/agent4_publisher/posters/*.py`;
- контентный пайплайн развивать через `agents/agent4_publisher/core/*.py` и `content/library/`;
- сбор лидов/мониторинг источников развивать не внутри Publisher, а через `agent2_collector`, `agent6_outreach` и `source-radar`.

## Первичный вердикт

Удаление пустых placeholder-пакетов можно принять как refactor.

Но перед backend/Agent 4 Batch нужно отдельно проверить, что roadmap использует новые целевые пути, а будущие адаптеры `avito`, `boards`, `maps` не потеряны.

## Уточнение после проверки изначальной роли

Пользователь справедливо указал: эти пакеты могли быть нужны для дальнейшей работы по источникам и публикационным поверхностям.

После сверки исходного `tasks/roadmap.md` и `docs/claude-agent-architecture.md` уточнено:

- Agent 4 Publisher изначально отвечал за публикационные поверхности и точки доверия;
- старые пакеты были пустыми, но их названия фиксировали важные будущие направления;
- удаление пустых пакетов не ломало код, но могло стереть продуктовую карту каналов.

Итоговое решение:

- восстановить пакеты `avito_poster`, `boards_poster`, `content_pipeline`, `dzen_poster`, `maps_poster`, `max_poster`, `tg_poster`, `vk_poster` как roadmap-slots;
- сохранить новую рабочую структуру `core/` и `posters/`;
- в документации явно разделить: Agent 4 создаёт и обновляет поверхности, Agent 2/6/source-radar собирают и обрабатывают лиды.

## Что обновлено

- `tasks/roadmap.md` - старые Agent 4 slots возвращены как продуктовая карта каналов;
- `agents/agent4_publisher/README.md` - добавлено объяснение изначальной роли Agent 4 и правил развития каналов;
- восстановлены placeholder-пакеты Agent 4 с поясняющими docstring.

## Следующий маленький шаг

Когда дойдём до Agent 4 Batch, сохранять этот refactor отдельной backend-партией, не смешивая с `site Batch`.
