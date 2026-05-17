# Stabilization Checkpoint - 2026-05-13

Цель: зафиксировать текущее состояние перед следующим сохранением или продолжением работ.

Это не commit, не `git add`, не deploy и не публикация.

## Короткий статус

- Последний локальный commit: `6ac5086 chore: add project safety and navigation docs`.
- Staged-файлов нет.
- Краткий `git status --short`: 127 строк.
- Полный `git status --short --untracked-files=all`: 213 файловых изменений.
- Из них: 32 modified, 8 deleted, 173 untracked.

## Группы изменений

| Блок | Количество | Комментарий |
| --- | ---: | --- |
| `site` и связанные site/content материалы | 52 | Главный кандидат на следующую проверку и сохранение отдельной партией. |
| `agents/backend/scripts/shared/orchestrator` | 73 | Большой блок логики. Нельзя сохранять вместе с сайтом без отдельной проверки. |
| `docs/research/tasks` | 44 | Методология, планы, исследования и checkpoints. Нужна проверка на чувствительные данные перед публичным сохранением. |
| `content` вне site | 10 | Контентные черновики, pipeline и источники. Проверять отдельно. |
| `data/reports` | 26 | Dashboard/test reports. Сохранять только безопасные отчеты, не operational/CRM-артефакты. |
| `config/security` | 7 | `.claude`, `config/settings.py`, `requirements.txt`. Требует аккуратной проверки, особенно по секретам и публичности. |
| прочее | 1 | Проверить вручную при подготовке партии. |

## Удаленные tracked-файлы

В `agent4_publisher` есть 8 удаленных старых `__init__.py`:

- `agents/agent4_publisher/avito_poster/__init__.py`
- `agents/agent4_publisher/boards_poster/__init__.py`
- `agents/agent4_publisher/content_pipeline/__init__.py`
- `agents/agent4_publisher/dzen_poster/__init__.py`
- `agents/agent4_publisher/maps_poster/__init__.py`
- `agents/agent4_publisher/max_poster/__init__.py`
- `agents/agent4_publisher/tg_poster/__init__.py`
- `agents/agent4_publisher/vk_poster/__init__.py`

Риск: это может быть правильный refactor в новую структуру `agents/agent4_publisher/core/` и `posters/`, но нельзя подтверждать удаления без отдельной проверки Agent 4 Publisher.

## Проверка сайта на секреты

Проверен блок:

- `site/`
- `content/site/`
- `content/studio_brand/`

Поиск секретных паттернов не показал реальных токенов. Найденные совпадения относятся к CSS `mask-image` и внутренним строкам React production build (`__SECRET_INTERNALS...`), это не пользовательские секреты.

## Что готовить первым

Лучший следующий блок: `site`.

Почему:

- сайт уже многократно проверялся локально по записям `REPORT.md`;
- блок изолирован от backend/CRM/Bitrix/Telegram;
- нет staged-файлов, значит можно спокойно подготовить отдельную партию;
- перед сохранением нужно сделать только финальный ручной/локальный check.

## Что нельзя трогать без отдельного решения

- удаленные файлы `agent4_publisher`;
- `.env`, credentials, tokens, local Claude settings;
- `data/reports` с operational/CRM тестами;
- backend/agents/scripts одним большим коммитом;
- deploy/GitHub push/Vercel publish.

## Рекомендуемый следующий шаг

Провести отдельный pre-save audit блока `site`:

1. прочитать `site/README.md`, `site/DESIGN.md`, `docs/site-*`;
2. проверить HTML/CSS/JS без внешних API;
3. проверить отсутствие секретов и персональных данных;
4. составить точный список файлов для будущего `git add`;
5. не выполнять `git add`, commit или deploy без подтверждения пользователя.
