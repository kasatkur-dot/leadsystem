# Session Notes

## 2026-05-17 — Полный тест dashboard/backend/frontend

### Что проверяли
- `backend/agent_dashboard_api`.
- `frontend/agent-system-visual`.
- Локальный dashboard `http://127.0.0.1:8788/`.
- Agent-control chat в режиме `openrouter_free_test`.

### Кто проверял
- Backend/API tester subagent.
- Frontend/UI tester subagent.
- Main Codex test pass.
- Playwright UI pass.

### Главный результат
- Продукт готов как internal MVP / technical demo.
- Он показывает карту 6 агентов, inspector, сценарии и принимает команды в chat dock.
- Text chat реально отвечает через OpenRouter free model.
- Реальные бизнес-интеграции ещё не выполняются.

### До какого этапа доходит
```text
local dashboard
-> real agent map
-> inspector
-> scenario playback
-> local chat command
-> OpenRouter free text response
-> safe handoff preview
```

### Что пока dry-run / не готово
- Redis queue execution.
- Bitrix24/Telegram action.
- Scheduler/publisher action.
- Voice transcription.
- Image generation.
- Knowledge embeddings.
- Real analytics update from event.

### Что исправлено в ходе теста
- Agent-control prompt теперь получает `known_project_agents` из dashboard.
- Повторный тест подтвердил реальные 6 агентов вместо generic-ролей.

### Отчёты
- `data/reports/agent_dashboard_product_test_2026-05-17.md`.
- `data/reports/agent_dashboard_product_test_2026-05-17.json`.

### Следующий маленький шаг
- Усилить agent-control до строгого управляющего протокола.
- Исправить mobile layout.
- Позже заменить CDN/Babel frontend на Vite/React build.

## 2026-05-17 — UI: увеличено окно agent-control chat

### Что изменено
- Нижняя панель чата увеличена и стала адаптивной.
- Чат занимает отдельную нижнюю grid-зону, поэтому не перекрывает граф агентов.
- История диалога стала шире и читабельнее: больше padding, крупнее текст, перенос длинных строк, собственная прокрутка.
- Поле ввода стало выше.

### Что проверено
- `http://127.0.0.1:8788/` открыт через Playwright.
- Консоль без ошибок.
- Тестовое сообщение отправлено, ответ виден в увеличенной истории.

### Наблюдение
- Следующий UX/logic шаг: усилить prompt agent-control, чтобы ответы шли строго по нашим 6 агентам и данным dashboard.

## 2026-05-17 — Исправлена ошибка HTML вместо JSON в agent-control chat

### Симптом
- В интерфейсе было сообщение: `Unexpected token '<', "<!DOCTYPE "... is not valid JSON`.
- Это значит, что frontend получил HTML-страницу вместо JSON-ответа API.

### Причина
- Интерфейс был открыт не через основной backend `http://127.0.0.1:8788/` или с устаревшим статическим `data.js`.
- В таком режиме `/api/agent-control/chat` мог уходить в статический сервер, а не в `backend/agent_dashboard_api`.

### Что исправлено
- Frontend теперь автоматически отправляет локальные API-запросы на `http://127.0.0.1:8788`, если открыт как файл или с другого локального порта.
- Добавлена понятная ошибка, если API снова вернёт HTML вместо JSON.
- Исправлен CORS preflight в backend: больше нет двойного `Access-Control-Allow-Origin`.
- Статический `frontend/agent-system-visual/data.js` обновлён до режима `openrouter_free_test`.

### Что проверено
- Основной backend `8788` отдаёт JSON.
- Статический тестовый порт `8790` тоже успешно отправляет `привет` на backend `8788`.
- Ответ приходит через `Agent control / OpenRouter free`.

### Следующий маленький шаг
- Открывать `http://127.0.0.1:8788/`.
- Если страница уже открыта, сделать hard refresh: `Cmd + Shift + R`.

## 2026-05-17 — Локальный OpenRouter free test включён

### Что изменено
- Добавлен режим `LLM_RUNTIME_MODE=openrouter_free_test`.
- Локальный `.env` переключён на `LLM_PROVIDER=openrouter` и `AGENT_CONTROL_LIVE_LLM=1`.
- Все текстовые маршруты в этом режиме используют одну бесплатную модель `deepseek/deepseek-v4-flash:free`.
- Созданы `.env.openrouter-free-test.example` и `docs/openrouter-free-local-test-mode.md`.

### Что проверено
- `OPENROUTER_API_KEY=SET`, значение ключа не выводилось.
- Модель `deepseek/deepseek-v4-flash:free` найдена в каталоге OpenRouter.
- `POST /api/agent-control/chat` на `привет` вернул `llm_status=OK`, `provider=openrouter`, `openrouter_llm=True`.
- В интерфейсе Playwright-проверкой подтверждено: `Enter` отправляет сообщение, появляется ответ ассистента, консоль без ошибок.
- Подписи маршрутов в интерфейсе приведены к фактическому режиму: `Agent control / OpenRouter free`, `Development / OpenRouter free`, `Marketing / OpenRouter free`.
- Локальный dashboard запущен на `http://127.0.0.1:8788/`.

### Что не запускалось
- Redis.
- Bitrix24.
- Telegram.
- IMAP.
- Scheduler.
- Publisher.
- Whisper, image generation, embeddings.
- Массовый сбор, публикации и outreach.

### Следующий маленький шаг
Открыть `http://127.0.0.1:8788/`, обновить страницу и проверить сообщение в нижнем chat/voice command center.

## 2026-05-17 — Точка продолжения: многоагентная система

### Где остановились
- Фокус этого чата возвращён к разработке многоагентной системы, не к сайту.
- Состав остаётся 6 агентов. Новые верхнеуровневые агенты и Agent 7 не создаются.
- Пример лектора с 35+ узлами перенесён как слой субролей, сценариев, артефактов, KPI и checker-контроля.

### Что сделано
- Создан `docs/agent-subroles-and-kpi-map.md`.
- Создан `docs/agent-scenario-artifact-contract.md`.
- Суброли добавлены в `agents/agent*/__init__.py`.
- Dashboard JSON/Markdown/HTML теперь показывает суброли и `Scenario Artifact Contract`.
- Checker обновлён и проверяет этот слой.
- Создан `scripts/check_first_inbound_scenario_artifacts.py`.
- Сценарий `Первый входящий запрос` проверен локально: `OK_LOCAL_DRY_RUN_READY_FOR_MANUAL_REVIEW`.
- Создан `scripts/create_first_inbound_scenario_handoff.py`.
- Сценарий `Первый входящий запрос` передан в локальный handoff человеку: `READY_FOR_MANUAL_REVIEW`.

### Что проверено
- `py_compile` dashboard/checker-скриптов — OK.
- `scripts/check_agent_okr_contract.py` — `agent_contract_status=OK`.
- В `data/reports/agent_dashboard.json` есть `scenario_artifact_contract`.
- В dashboard осталось 6 агентов и добавлено 33 суброли.
- `intake_card`, `qualified_lead`, `crm_payload_preview`, `human_next_step` — OK по локальному dry-run.
- `first_inbound_scenario_handoff_to_human.json` создан и не вызывает внешние сервисы.

### Что не запускалось
- Redis.
- Bitrix24.
- Telegram.
- IMAP.
- LLM.
- Scheduler.
- Publisher.
- Массовый сбор.
- Реальные публикации и outreach.

### Следующий маленький шаг
Янике выбрать одно решение по handoff: `confirm_bitrix_fields`, `keep_dry_run` или `revise_payload`.

## 2026-05-15 — Точка продолжения: сайт

### Где остановились
- Сейчас фокус только на сайте.
- CRM, Bitrix24, AI-менеджер и база данных отложены до завершения сайта.
- Сайт локально подготовлен, но не опубликован.

### Что сделано по сайту
- Актуальное ТЗ: `docs/current-site-improvement-tz.md`.
- Финальный чек-лист: `tasks/site-finalization-checklist-2026-05-15.md`.
- Главная страница доработана ниже hero; первый экран не перестраивался по сетке, кнопкам, цветам и шрифтам.
- Доработаны услуги, процесс, FAQ, CTA, кейсы, доверие, медиа, команда и контакты.
- Добавлен блок исходных данных после услуг.
- Пересозданы 6 статических страниц услуг и `site/sitemap.xml`.
- Зафиксирована схема связи сайта с Bitrix24 без формы, но на сайт она не подключалась.

### Что проверено
- `node site/tools/build-bundle.mjs` — OK.
- `.venv/bin/python site/tools/generate-service-pages.py` — `generated 6 service pages`.
- `node --check site/assets/app.bundle.js` — OK.
- Проверено: `10` HTML-файлов, `11` JSON-LD блоков, JSON-LD ошибок `0`, `sitemap.xml` валидный.
- Запрещённые публичные фразы в `site` не найдены.

### Что не запускалось
- Vercel/GitHub deploy.
- Публикация сайта.
- Формы.
- CRM/Bitrix24.
- AI-менеджер.
- Внешние API и платные сервисы.

### Следующий маленький шаг
1. Подтвердить финальный домен: `https://wektorplus-pro.ru/` или другой.
2. После этого отдельно подтвердить, можно ли запускать preview.
3. На preview сделать финальный визуальный проход по главной, услугам, кейсам, доверию, медиа, контактам и одной странице услуги на телефоне/десктопе.

## 2026-05-13 — MAX messaging + Agent 5 Bitrix24 тест (claude-code bridge session)

### Что сделано
- Bitrix24 MCP webhook проверен: `bitrix24_validate_webhook` → `{"valid": true}` ✅
- `test_agent5_bitrix_lead.py` → создан лид #848 в Bitrix24 ✅
- `close_bitrix_test_lead.py --lead-id 848` → лид закрыт как JUNK ✅
- Создан скрипт `scripts/send_max_message.py` для отправки сообщений через MAX (открытые линии Bitrix24)
- Добавлен раздел «MAX-команды» в CLAUDE.md Telegram bridge
- Подтверждение от Яники: она хочет именно этот механизм ("Именно так")

### Как работает send_max_message.py
- `--contact "ИМЯ"` — найти лид по имени (поиск по HAS_IMOL=Y)
- `--lead-id ID` — отправить напрямую по ID лида
- `--list-max-leads` — показать все MAX-лиды в Bitrix24
- `--message "ТЕКСТ"` — текст сообщения
- Использует imopenlines.crm.chat.get + im.message.add
- Читает BITRIX24_WEBHOOK_URL из .env, токен не выводится в логи

### Файлы изменены
- `scripts/send_max_message.py` — создан
- `../telegram-claude-code-bridge/CLAUDE.md` — добавлен раздел MAX-команды

### Следующий шаг
1. Протестировать send_max_message.py на реальном MAX-лиде: `--list-max-leads`, затем `--lead-id X --message "тест"`
2. Запустить сквозной тест: Agent 3 LLM → Redis leads:qualified → Agent 5 → Bitrix24
3. Зафиксировать 3 batch-коммита когда Яника подтвердит

## 2026-05-13 — Bitrix24 MCP сервер (claude-code bridge session)

### Что сделано
- Установлен `gunnit/bitrix24-mcp-server` в `tools/bitrix24-mcp-server/`
- Собран: `npm install` + `npm run build` → `build/index.js`
- Исправлена уязвимость form-data (`npm audit fix`); SDK 0.4.0 оставлен (1.29.0 ломает build)
- Добавлен в `~/.claude.json` глобально (webhook из `.env` этого проекта)
- Проверен: 56 инструментов активны, сервер стартует без ошибок

### Файлы изменены
- `/Users/yanika/.claude.json` — добавлен `"bitrix24"` блок в `mcpServers`
- `/Users/yanika/Documents/Вайбкодинг/Codex/2026-04-20-cloude-code/tools/bitrix24-mcp-server/` — создан

### Следующий шаг
1. Перезапустить Claude Code
2. Проверить через `/mcp` что `bitrix24` в списке
3. Запустить `bitrix24_validate_webhook` и `bitrix24_list_leads` для проверки реального подключения
4. При необходимости создать задачу в design-studio на интеграцию Bitrix24 в агентный pipeline

## 2026-05-08 — Agent 3 Redis + настоящий LLM прошёл

### Итог

Пользователь запустил:

```bash
.venv/bin/python scripts/test_agent3_redis_processing_llm.py
```

Результат:

```text
redis_ping_status=OK
queue_guard_status=OK
redis_push_raw_status=OK
agent3_run_status=OK
qualified_output_status=OK
cleanup_status=OK
processed_count=1
qualified_score=hot
qualified_flow=B
qualified_recommended_action=позвонить сегодня
external_calls=redis_ping:True,redis_push_raw:True,agent3_run:True,llm_score:True,llm_offer:True,redis_pop_qualified_cleanup:True,bitrix24:False,telegram_send:False,imap:False,scheduler:False
```

Отчёт:

```text
data/reports/agent3_redis_processing_llm_test.json
```

### Очереди

До теста:

```text
raw=0
qualified=0
outreach=0
content_events=0
```

После Agent 3:

```text
raw=0
qualified=1
outreach=0
content_events=0
```

После cleanup:

```text
raw=0
qualified=0
outreach=0
content_events=0
```

Хвоста для Agent 5 не осталось.

### Что не запускалось

- Agent 5;
- Bitrix24;
- Telegram;
- IMAP;
- scheduler;
- массовый сбор.

### Следующий маленький шаг

Подготовить полный контролируемый handoff с настоящим LLM:

```text
RawLead -> Redis leads:raw -> Agent 3 real LLM -> Redis leads:qualified -> Agent 5 -> Bitrix24 + Telegram
```

Без IMAP, без scheduler и без массового сбора. После теста закрыть созданный Bitrix24 тестовый лид.

## 2026-05-08 — Подготовлен Agent 3 Redis-тест с настоящим LLM

### Что подготовлено

Создан скрипт:

```bash
.venv/bin/python scripts/test_agent3_redis_processing_llm.py
```

Он проверяет один контролируемый путь:

```text
RawLead -> Redis leads:raw -> agents.agent3_processor.run() -> Redis leads:qualified -> cleanup
```

### Что важно

- `score/generate` не подменяются локальными функциями.
- Используется настоящий LLM через текущий `LLM_PROVIDER=openrouter`.
- `is_duplicate` временно подменяется, чтобы не писать тестовый fingerprint в Redis.
- После теста скрипт забирает тестовый `QualifiedLead` из `leads:qualified`, чтобы не оставить хвост для Agent 5.

### Что не запускается

- Agent 5;
- Bitrix24;
- Telegram;
- IMAP;
- scheduler;
- массовый сбор.

### Проверено

```text
compileall=OK
dry_run=OK
llm_provider=openrouter
llm_config_status=OK
openrouter_api_key_status=SET
external_calls=redis_ping:False,redis_push_raw:False,agent3_run:False,llm_score:False,llm_offer:False,bitrix24:False,telegram_send:False,imap:False,scheduler:False
```

Отчёт dry-run:

```text
data/reports/agent3_redis_processing_llm_test_dry_run.json
```

### Следующий маленький шаг

В обычном терминале проекта запустить:

```bash
.venv/bin/python scripts/test_agent3_redis_processing_llm.py
```

Нужный результат:

```text
redis_ping_status=OK
queue_guard_status=OK
agent3_run_status=OK
qualified_output_status=OK
cleanup_status=OK
qualified_score=hot
```

## 2026-05-08 — Agent 3 LLM score/offer через OpenRouter прошёл

### Итог

Пользователь повторил:

```bash
.venv/bin/python scripts/test_agent3_llm_score_offer.py --execute
```

Результат успешный:

```text
llm_config_status=OK
anthropic_api_key_status=SET
openrouter_api_key_status=SET
offtopic_status=OK_NOT_OFFTOPIC
enrich_status=OK
llm_score_status=OK
llm_offer_status=OK
score=hot
recommended_action=позвонить сегодня
offer_chars=148
external_calls=llm_score:True,llm_offer:True,redis:False,bitrix24:False,telegram_send:False,imap:False,scheduler:False
```

Отчёт:

```text
data/reports/agent3_llm_score_offer_test.json
```

### Вывод

Отдельный настоящий LLM-блок Agent 3 закрыт:

```text
RawLead synthetic -> scorer.score() -> offer_gen.generate()
```

Через OpenRouter скоринг и оффер работают.

### Следующий маленький шаг

Подготовить один контролируемый Redis-тест Agent 3 с настоящим LLM:

```text
RawLead -> Redis leads:raw -> agents.agent3_processor.run() -> Redis leads:qualified -> cleanup
```

Без Agent 5, Bitrix24, Telegram, IMAP и scheduler.

## 2026-05-08 — OpenRouter content=None исправлен для Agent 3 LLM-теста

### Что произошло

После добавления `OPENROUTER_API_KEY` пользователь повторил:

```bash
.venv/bin/python scripts/test_agent3_llm_score_offer.py --execute
```

Результат:

```text
llm_provider=openrouter
openrouter_api_key_status=SET
llm_config_status=OK
llm_score_status=FAILED
llm_offer_status=NOT_RUN
external_calls=llm_score:True,llm_offer:False,redis:False,bitrix24:False,telegram_send:False,imap:False,scheduler:False
```

Точная ошибка в `logs/lead_engine.log`:

```text
scorer ошибка: 'NoneType' object has no attribute 'strip'
```

### Что исправлено

- `shared/llm_client.py` теперь аккуратно разбирает OpenRouter `message.content`.
- Если OpenRouter вернёт пустой content, тест покажет понятную ошибку с `model`, `finish_reason` и `message_keys`.
- `scorer.score()` и `offer_gen.generate()` получили тестовый режим `raise_errors=True`.
- `scripts/test_agent3_llm_score_offer.py` теперь в execute-режиме показывает реальную ошибку провайдера, а не только fallback.
- OpenRouter-модели переключены на стабильный пример из документации:

```text
LLM_MODEL_ANALYSIS=openai/gpt-4o
LLM_MODEL_REPLY=openai/gpt-4o
LLM_MODEL_CONTENT=openai/gpt-4o
```

### Проверено

```text
compileall=OK
dry_run=OK
llm_provider=openrouter
llm_config_status=OK
openrouter_api_key_status=SET
external_calls=llm_score:False,llm_offer:False,redis:False,bitrix24:False,telegram_send:False,imap:False,scheduler:False
```

### Следующий маленький шаг

В обычном терминале повторить:

```bash
.venv/bin/python scripts/test_agent3_llm_score_offer.py --execute
```

Нужный результат:

```text
llm_score_status=OK
llm_offer_status=OK
```

Если снова будет отказ OpenRouter, теперь в отчёте должна быть точная причина.

## 2026-05-08 — OpenRouter настроен как альтернативный LLM-провайдер

### Итог

Альтернативный провайдер настроен локально:

```text
LLM_PROVIDER=openrouter
LLM_MODEL_ANALYSIS=SET
LLM_MODEL_REPLY=SET
LLM_MODEL_CONTENT=SET
OPENROUTER_APP_TITLE=SET
OPENROUTER_SITE_URL=EMPTY
OPENROUTER_API_KEY=EMPTY
```

Ключ OpenRouter пока не задан. Значение ключа не выводилось.

### Что изменено

- `shared/llm_client.py` — добавлены optional OpenRouter headers `HTTP-Referer` и `X-OpenRouter-Title`.
- `config/settings.py` — добавлены `OPENROUTER_SITE_URL` и `OPENROUTER_APP_TITLE`.
- `scripts/set_env_secret.py` — разрешены локальные LLM/OpenRouter настройки.
- `scripts/configure_openrouter_provider.py` — создан безопасный конфигуратор non-secret OpenRouter-настроек.
- `.env.example` — обновлены подсказки по OpenRouter model ID формата `provider/model`.

### Проверено

```text
compileall=OK
openrouter_provider_config=OK
secret_values_printed=False
```

Dry-run Agent 3:

```text
llm_provider=openrouter
llm_config_status=FAILED_OPENROUTER_API_KEY_EMPTY
openrouter_api_key_status=EMPTY
external_calls=llm_score:False,llm_offer:False,redis:False,bitrix24:False,telegram_send:False,imap:False,scheduler:False
```

### Следующий маленький шаг

В обычном терминале проекта задать ключ:

```bash
.venv/bin/python scripts/set_env_secret.py OPENROUTER_API_KEY
```

Потом повторить LLM-тест:

```bash
.venv/bin/python scripts/test_agent3_llm_score_offer.py --execute
```

## 2026-05-08 — Agent 3 LLM-тест остановлен по балансу Anthropic

### Итог

Пользователь запустил:

```bash
.venv/bin/python scripts/test_agent3_llm_score_offer.py --execute
```

Тест дошёл до реального Anthropic API, но провайдер отказал:

```text
Your credit balance is too low to access the Anthropic API
```

Результат:

```text
llm_config_status=OK
anthropic_api_key_status=SET
openrouter_api_key_status=EMPTY
offtopic_status=OK_NOT_OFFTOPIC
enrich_status=OK
llm_score_status=FAILED
llm_offer_status=NOT_RUN
external_calls=llm_score:True,llm_offer:False,redis:False,bitrix24:False,telegram_send:False,imap:False,scheduler:False
```

Отчёт:

```text
data/reports/agent3_llm_score_offer_test.json
```

### Вывод

Это не поломка Agent 3 и не проблема Redis/CRM/Telegram.

Блокер внешний:

```text
Anthropic billing / credit balance
```

### Следующий маленький шаг

Не повторять LLM-тест до устранения billing-блокера.

Сначала сделать одно из двух:

- пополнить баланс Anthropic;
- или настроить альтернативный LLM-провайдер в `.env`.

Потом повторить:

```bash
.venv/bin/python scripts/test_agent3_llm_score_offer.py --execute
```

## 2026-05-08 — OKR-checker создан и пройден

### Итог

По продуктовой структуре закрыт следующий маленький шаг после фиксации OKR:

```text
scripts/check_agent_okr_contract.py
```

Результат:

```text
agent_contract_status=OK
agent4_readme_status=FOUND
claude_folder_map_status=OK
redis_queue_status=OK
canonical_test_status=FOUND
missing_agent_files=[]
missing_okr_blocks=[]
missing_metric_blocks=[]
```

Отчёт:

```text
data/reports/agent_okr_contract_check.json
```

### Что не запускалось

- Redis;
- Bitrix24;
- Telegram;
- IMAP;
- LLM/API;
- scheduler;
- publisher;
- массовый сбор.

### Дополнительно подготовлено

Подготовлен следующий безопасный runtime-тест:

```bash
.venv/bin/python scripts/test_agent3_llm_score_offer.py --execute
```

Без `--execute` этот скрипт работает как dry-run и не делает LLM-вызов.

### Следующий маленький шаг

Если продолжаем проверку runtime-цепочки, запустить в обычном терминале:

```bash
.venv/bin/python scripts/test_agent3_llm_score_offer.py --execute
```

Нужный результат:

```text
llm_score_status=OK
llm_offer_status=OK
external_calls=llm_score:True,llm_offer:True,redis:False,bitrix24:False,telegram_send:False,imap:False,scheduler:False
```

## 2026-05-08 — Лид 832 закрыт, полный handoff MVP закрыт

### Итог

Тестовый лид `832` закрыт:

```text
bitrix_close_status=OK
bitrix_status_id=JUNK
bitrix_lead_deleted=False
```

Bitrix24-действия:

- `crm.status.list`;
- `crm.timeline.comment.add`;
- `crm.lead.update`.

### Что не запускалось

- Telegram;
- Redis;
- IMAP;
- LLM/API;
- scheduler;
- массовый сбор.

### Статус этапа

Полный контролируемый MVP-участок закрыт:

```text
RawLead -> Redis leads:raw -> Agent 3 local score/offer -> Redis leads:qualified -> Agent 5 -> Bitrix24 + Telegram
```

Все известные тестовые лиды закрыты:

```text
828
830
832
```

### Следующий маленький шаг

Перед следующей внешней проверкой сначала проверить пустоту Redis-очередей.

Потом выбрать один следующий безопасный тест:

- IMAP-вход на одном письме;
- или настоящий LLM-score/offer на одном синтетическом лиде.

## 2026-05-08 — Полный handoff RawLead -> Agent 3 -> Agent 5 прошёл

### Итог

Тест прошёл успешно:

```text
agent3_run_status=OK
agent5_run_status=OK
bitrix_send_status=OK
telegram_send_status=OK
agent3_processed_count=1
agent5_processed_count=1
bitrix_id=832
```

### Что проверено

Один полный контролируемый путь:

```text
RawLead -> Redis leads:raw -> Agent 3 local score/offer -> Redis leads:qualified -> Agent 5 -> Bitrix24 + Telegram
```

### Очереди

До теста очереди были пустые.

После Agent 5 снова пустые:

```text
raw=0
qualified=0
outreach=0
content_events=0
```

### Что не запускалось

- LLM/API;
- IMAP;
- scheduler;
- массовый сбор;
- реальные публикации.

### Что осталось

Тестовый лид `832` нужно закрыть в Bitrix24.

### Следующий маленький шаг

В обычном терминале запустить:

```bash
.venv/bin/python scripts/close_bitrix_test_lead.py --lead-id 832
```

Нужный результат:

```text
bitrix_close_status=OK
bitrix_status_id=JUNK
```

До закрытия `832` новые тесты не запускать.

## 2026-05-08 — Подготовлен полный handoff RawLead -> Agent 3 -> Agent 5

### Что подготовлено

Создан скрипт:

```bash
.venv/bin/python scripts/test_agent3_to_agent5_handoff_local.py
```

Он проверяет один полный контролируемый путь:

```text
RawLead -> Redis leads:raw -> Agent 3 local score/offer -> Redis leads:qualified -> Agent 5 -> Bitrix24 + Telegram
```

### Что не запускается

- scheduler;
- IMAP;
- LLM/API;
- массовый сбор;
- реальные публикации.

### Что будет внешним действием в обычном запуске

- один тестовый лид в Bitrix24;
- одно Telegram-уведомление менеджеру.

### Защита

Перед добавлением тестового лида скрипт проверяет очереди:

- `raw`;
- `qualified`;
- `outreach`;
- `content_events`.

Если там есть данные, скрипт остановится до добавления тестового лида.

### Проверено в Codex

```text
compileall=OK
dry_run=OK
```

Реальный запуск из Codex остановился до изменения очередей:

```text
redis_ping_status=FAILED
redis_push_raw_status=NOT_RUN
agent3_run_status=NOT_RUN
agent5_run_status=NOT_RUN
bitrix_send_status=NOT_RUN
telegram_send_status=NOT_RUN
```

Причина: Codex-среда не имеет доступа к локальному Redis.

### Следующий маленький шаг

В обычном терминале проекта запустить:

```bash
.venv/bin/python scripts/test_agent3_to_agent5_handoff_local.py
```

Нужный результат:

```text
agent3_run_status=OK
agent5_run_status=OK
bitrix_send_status=OK
telegram_send_status=OK
agent3_processed_count=1
agent5_processed_count=1
```

После успешного запуска закрыть новый тестовый лид:

```bash
.venv/bin/python scripts/close_bitrix_test_lead.py --lead-id НОВЫЙ_BITRIX_ID
```

## 2026-05-08 — Agent 3 Redis-тест без LLM закрыт

### Итог

Тест прошёл успешно:

```text
redis_ping_status=OK
queue_guard_status=OK
agent3_run_status=OK
qualified_output_status=OK
cleanup_status=OK
processed_count=1
qualified_score=hot
qualified_flow=B
```

### Что проверено

Один синтетический лид прошёл участок:

```text
RawLead -> Redis leads:raw -> agents.agent3_processor.run() -> Redis leads:qualified
```

### Очереди

До теста:

```text
raw=0
qualified=0
```

После обработки:

```text
raw=0
qualified=1
```

После cleanup:

```text
raw=0
qualified=0
```

То есть хвоста для Agent 5 не осталось.

### Что не запускалось

- LLM/API;
- Bitrix24;
- Telegram;
- IMAP;
- scheduler;
- массовый сбор.

### Следующий маленький шаг

Подготовить один контролируемый тест:

```text
RawLead -> Agent 3 local score/offer -> Agent 5 -> Bitrix24 + Telegram
```

Без scheduler, без IMAP, без LLM и без массового сбора. Перед запуском снова проверить пустоту Redis-очередей.

## 2026-05-07 — Подготовлен Agent 3 Redis-тест без LLM

### Что выбрано следующим

После закрытия Agent 5 следующий безопасный участок MVP:

```text
RawLead -> Redis leads:raw -> agents.agent3_processor.run() -> Redis leads:qualified
```

Agent 5 при этом не запускается.

### Почему отдельный скрипт

Обычный Agent 3 вызывает Claude API для:

- скоринга;
- генерации оффера.

Чтобы не трогать платные API, создан безопасный локальный тест:

```bash
.venv/bin/python scripts/test_agent3_redis_processing_local.py
```

Он временно подменяет `score` и `generate` локальными функциями только на время теста.

### Защита

Скрипт сначала проверяет очереди:

- `raw`;
- `qualified`;
- `outreach`;
- `content_events`.

Если там есть данные, он остановится до добавления тестового лида.

После успешной обработки он забирает тестовый `QualifiedLead` из `leads:qualified`, чтобы не оставить хвост для Agent 5.

### Проверено в Codex

```text
compileall=OK
dry_run=OK
```

Реальный запуск из Codex остановлен до изменения очередей:

```text
redis_ping_status=FAILED
redis_push_raw_status=NOT_RUN
agent3_run_status=NOT_RUN
cleanup_status=NOT_NEEDED
```

Причина: Codex-среда не имеет доступа к локальному Redis.

### Следующий маленький шаг

В обычном терминале проекта запустить:

```bash
.venv/bin/python scripts/test_agent3_redis_processing_local.py
```

Нужный результат:

```text
redis_ping_status=OK
queue_guard_status=OK
agent3_run_status=OK
qualified_output_status=OK
cleanup_status=OK
processed_count=1
```

## 2026-05-07 — Лид 830 закрыт, этап Agent 5 закрыт полностью

### Итог

Тестовый лид `830` закрыт:

```text
bitrix_close_status=OK
bitrix_status_id=JUNK
bitrix_lead_deleted=False
```

Bitrix24-действия:

- `crm.status.list`;
- `crm.timeline.comment.add`;
- `crm.lead.update`.

### Что не запускалось

- Telegram;
- Redis;
- IMAP;
- LLM/API;
- scheduler;
- массовый сбор.

### Статус Agent 5

Этап Agent 5 закрыт:

- отдельный Bitrix24 тест: OK;
- отдельный Telegram тест: OK;
- полный `QualifiedLead -> Bitrix24 -> Telegram`: OK;
- Redis-queue handoff `leads:qualified -> agents.agent5_crm.run() -> Bitrix24 -> Telegram`: OK;
- тестовые лиды `828` и `830` закрыты.

### Следующий маленький шаг

Перед следующим внешним тестом проверить пустоту Redis-очередей, потом выбрать следующий безопасный участок MVP: один контролируемый вход до Agent 5, без scheduler и без массового сбора.

## 2026-05-07 — Redis-queue handoff Agent 5 закрыт

### Итог

Telegram retry прошёл успешно:

```text
telegram_payload_status=OK
telegram_send_status=OK
bitrix_id=830
```

### Что закрыто

Один полный безопасный Redis-queue handoff Agent 5:

```text
Redis leads:qualified -> agents.agent5_crm.run() -> Bitrix24 -> Telegram
```

Фактический итог:

- Redis принял один тестовый `QualifiedLead`;
- `agents.agent5_crm.run()` обработал ровно один элемент;
- Bitrix24 создал тестовый лид `830`;
- Telegram-уведомление менеджеру отправлено;
- scheduler, IMAP, LLM/API и массовый сбор не запускались.

### Что осталось

Тестовый лид `830` ещё нужно закрыть в Bitrix24.

### Следующий маленький шаг

В обычном терминале запустить:

```bash
.venv/bin/python scripts/close_bitrix_test_lead.py --lead-id 830
```

Нужный результат:

```text
bitrix_close_status=OK
bitrix_status_id=JUNK
```

До закрытия `830` новые Redis/Bitrix/Telegram тесты не запускать.

## 2026-05-07 — Redis-queue тест: Bitrix24 OK, Telegram Markdown исправлен

### Что произошло

Redis-queue тест Agent 5 обработал один тестовый лид:

```text
processed_count=1
bitrix_send_status=OK
bitrix_id=830
telegram_send_status=FAILED
```

Очередь была чистая, один тестовый `QualifiedLead` был положен в `leads:qualified`, затем запущен только:

```text
agents.agent5_crm.run()
```

Scheduler, IMAP, LLM/API и массовый сбор не запускались.

### Причина ошибки Telegram

Telegram упал на Markdown-разметке:

```text
Can't parse entities
```

Причина простая: в динамическом тексте были символы вроде `_` в `agent5_crm.run()`. Старый `ParseMode.MARKDOWN` воспринимал `_` как начало форматирования.

### Что исправлено

`agents/agent5_crm/notifier/__init__.py`:

- уведомления переведены на `ParseMode.HTML`;
- все динамические поля экранируются через `html.escape`;
- контакт и ID выводятся через `<code>`;
- жирные подписи выводятся через `<b>`.

`scripts/test_agent5_redis_queue_handoff.py`:

- dry-run теперь пишет отдельный отчёт и не затирает реальный результат.

Создан безопасный retry:

```bash
.venv/bin/python scripts/retry_agent5_redis_telegram_notification.py
```

Он отправляет только Telegram-уведомление по уже созданному Bitrix24-лиду `830`.

### Проверено без внешних действий

```text
compileall=OK
retry dry_run=OK
telegram_payload_status=OK
```

### Следующий маленький шаг

В обычном терминале запустить:

```bash
.venv/bin/python scripts/retry_agent5_redis_telegram_notification.py
```

Нужный результат:

```text
telegram_send_status=OK
```

После этого закрыть тестовый лид:

```bash
.venv/bin/python scripts/close_bitrix_test_lead.py --lead-id 830
```

## 2026-05-07 — Лид 828 закрыт, Redis-queue тест Agent 5 подготовлен

### Итог по лиду 828

Повторный запуск в обычном терминале прошёл успешно:

```text
bitrix_close_status=OK
bitrix_status_id=JUNK
bitrix_statuses_found=5
```

Bitrix24-действия:

- `crm.status.list`;
- `crm.timeline.comment.add`;
- `crm.lead.update`.

Удаления не было:

```text
bitrix_lead_deleted=False
```

### Что закрыто

Тестовый лид `828` закрыт статусом `JUNK` / `Некачественный лид`.

### Что подготовлено дальше

Создан скрипт следующего безопасного теста:

```bash
.venv/bin/python scripts/test_agent5_redis_queue_handoff.py
```

Он делает ровно это:

```text
один QualifiedLead -> Redis leads:qualified -> agents.agent5_crm.run() -> Bitrix24 + Telegram
```

Он не запускает:

- scheduler;
- IMAP;
- LLM/API;
- массовый сбор;
- реальные публикации.

### Защита

Если очереди Agent 5 уже не пустые, скрипт остановится до добавления тестового лида.

Проверяются очереди:

- `qualified`;
- `outreach`;
- `content_events`.

### Проверено без внешних действий

```text
compileall=OK
dry_run=OK
bitrix_payload_status=OK
telegram_payload_status=OK
```

### Следующий маленький шаг

В обычном терминале проекта запустить:

```bash
.venv/bin/python scripts/test_agent5_redis_queue_handoff.py
```

Нужный результат:

```text
processed_count=1
bitrix_send_status=OK
telegram_send_status=OK
```

После этого новый тестовый лид тоже нужно будет закрыть через:

```bash
.venv/bin/python scripts/close_bitrix_test_lead.py --lead-id НОВЫЙ_ID
```

## 2026-05-07 — Статусы Bitrix24 теперь читаются raw-вызовом

### Что было

Повторный запуск дал:

```text
error_type=RuntimeError
report_file=data/reports/bitrix_close_test_lead_828.json
```

В отчёте:

```text
bitrix_statuses_found=0
bitrix_available_statuses=[]
```

То есть Bitrix24 ответил, но обычная обработка `fast-bitrix24.call()` дала пустой список статусов.

### Что исправлено

В `scripts/close_bitrix_test_lead.py` метод `crm.status.list` теперь вызывается через `raw=True`.

Это значит: скрипт берёт настоящий сырой ответ Bitrix24 и сам достаёт из него `result`.

### Проверено

- `compileall=OK`
- локальный разбор raw-ответа Bitrix24: `normalized_count=1`

### Следующий маленький шаг

Снова запустить:

```bash
.venv/bin/python scripts/close_bitrix_test_lead.py --lead-id 828
```

Теперь должно быть одно из двух:

- `bitrix_close_status=OK` — лид закрыт;
- или появится непустая строка `available_statuses=...` — тогда выберем нужный `status_id`.

## 2026-05-07 — Ошибка RuntimeError при закрытии лида 828 уточнена

### Что значит ошибка

`RuntimeError` здесь не означает, что агент сломался целиком.

По отчёту:

```text
bitrix_statuses_read=true
error=No failure/JUNK lead status found in Bitrix24
```

То есть Bitrix24 ответил, но скрипт не нашёл стандартный статус закрытия `JUNK`/failure.

### Что изменено

`scripts/close_bitrix_test_lead.py` обновлён:

- теперь печатает безопасную строку `available_statuses=...`;
- умеет принимать ручной статус через `--status-id`;
- лучше ищет закрывающий статус по названиям вроде `отказ`, `закрыт`, `некачественный`, `junk`, `fail`;
- dry-run больше не затирает отчёт реального запуска.

### Проверено

- `compileall=OK`
- `--help=OK`
- локальный выбор кастомного статуса по названию `Отказ клиента=OK`

### Следующий маленький шаг

В обычном терминале повторить:

```bash
.venv/bin/python scripts/close_bitrix_test_lead.py --lead-id 828
```

Если снова будет ошибка, прислать строку:

```text
available_statuses=...
```

После этого можно будет запустить так:

```bash
.venv/bin/python scripts/close_bitrix_test_lead.py --lead-id 828 --status-id НУЖНЫЙ_STATUS_ID
```

## 2026-05-07 — Закрытие тестового лида 828 подготовлено

### Итог

Создан безопасный скрипт закрытия тестового лида:

```bash
.venv/bin/python scripts/close_bitrix_test_lead.py --lead-id 828
```

Скрипт не удаляет лид. Он ищет статус `JUNK`/failure в Bitrix24, добавляет комментарий в таймлайн и переводит лид в этот статус.

### Проверено

- `BITRIX24_WEBHOOK_URL=SET`
- `compileall=OK`
- dry-run: `bitrix_close_status=DRY_RUN`
- отчёт: `data/reports/bitrix_close_test_lead_828.json`

### Что произошло в Codex-среде

Реальное закрытие из Codex не прошло из-за сетевого ограничения:

```text
bitrix_close_status=FAILED
error=All attempts to get data from server exhausted
```

Лид `828` не был закрыт и не был удалён. До Bitrix24 не дошли `crm.timeline.comment.add`, `crm.lead.update` и `crm.lead.delete`.

### Что не запускалось

- Redis-queue тест Agent 5;
- Telegram-отправка;
- IMAP;
- LLM/API;
- scheduler;
- массовый сбор.

### Следующий маленький шаг

В обычном терминале проекта запустить:

```bash
.venv/bin/python scripts/close_bitrix_test_lead.py --lead-id 828
```

Нужный результат:

```text
bitrix_close_status=OK
```

После этого можно переходить к одному Redis-queue тесту Agent 5.

## 2026-05-07 — Полный handoff Agent 5 закрыт

### Итог

Повторный запуск из обычного терминала прошёл успешно:

```text
bitrix_payload_status=OK
bitrix_send_status=OK
telegram_payload_status=OK
telegram_send_status=OK
```

### Проверено

- `bitrix24_attempted=true`
- `bitrix24_created=true`
- `telegram_attempted=true`
- `telegram_send=true`
- `bitrix_method=crm.lead.add`
- `bitrix_id=828`
- отчёт: `data/reports/agent5_full_handoff_test.json`

### Что было внешним действием

- один тестовый лид в Bitrix24;
- одно тестовое Telegram-уведомление менеджеру.

### Что не запускалось

- IMAP;
- Redis-очереди;
- LLM/API;
- платные API;
- массовый сбор;
- реальные публикации;
- `orchestrator/scheduler.py`.

### Статус шага

Связка `QualifiedLead -> Bitrix24 -> Telegram` закрыта.

### Следующий маленький шаг

Удалить или закрыть тестовый лид `828`, затем сделать безопасный Redis-queue тест Agent 5: положить один тестовый `QualifiedLead` в очередь и запустить только `agents.agent5_crm.run()`, без scheduler и без IMAP.

## 2026-05-07 — Подготовлен полный тест Agent 5: Bitrix24 + Telegram

### Итог

Создан скрипт полного handoff-теста:

```bash
.venv/bin/python scripts/test_agent5_full_handoff.py
```

Он проверяет один тестовый лид по связке:

```text
QualifiedLead -> Bitrix24 crm.lead.add -> Telegram-уведомление менеджеру
```

### Что улучшено

В Bitrix24 payload теперь заполняется `NAME`, чтобы тестовые и будущие реальные карточки не выглядели как `Без имени`, если есть `company_name` или другой понятный признак.

### Проверено без внешних вызовов

- `BITRIX_NAME_STATUS=OK`
- `BITRIX_TITLE_STATUS=OK`
- `TELEGRAM_MESSAGE_STATUS=OK`
- синтаксис скрипта: OK

### Что произошло в Codex-среде

Запуск из Codex-среды не прошёл из-за сетевого ограничения:

```text
bitrix_send_status=FAILED
telegram_send_status=FAILED
```

Это не ошибка проекта. Ранее такие же внешние тесты успешно проходили из обычного терминала пользователя.

### Что не запускалось

- IMAP;
- Redis-очереди;
- LLM/API;
- платные API;
- массовый сбор;
- реальные публикации;
- `orchestrator/scheduler.py`.

### Следующий маленький шаг

В обычном терминале проекта запустить:

```bash
.venv/bin/python scripts/test_agent5_full_handoff.py
```

Нужный результат:

```text
bitrix_send_status=OK
telegram_send_status=OK
```

## 2026-05-07 — Bitrix24 лид визуально проверен

### Итог

Пользователь показал карточку лида в Bitrix24. Лид реально появился в CRM.

### Что видно на карточке

- заголовок: `[B] TENDER_EMAIL — HOT | Краснодар`;
- источник: `Электронная почта`;
- комментарий: скор `hot` и тестовая пометка Agent 5;
- сумма: `0 ₽`, потому что тестовый лид без бюджета;
- имя: `Без имени`, потому что синтетический тестовый лид не содержит имени клиента.

### Статус шага

Визуальная проверка Bitrix24 закрыта.

### Что улучшить позже

Перед реальными лидами улучшить заполнение карточки:

- имя или компания;
- контакт;
- бюджет/стоимость, если он известен;
- более короткий и удобный комментарий.

### Следующий маленький шаг

Удалить или закрыть тестовый лид `826`, затем сделать следующий безопасный тест: один тестовый лид должен одновременно создать карточку в Bitrix24 и отправить Telegram-уведомление менеджеру.

## 2026-05-07 — Agent 5 Bitrix24 test закрыт

### Итог

Тест создания лида в Bitrix24 успешно прошёл:

```text
bitrix_payload_status=OK
bitrix_send_status=OK
```

### Проверено

- `bitrix24_attempted=true`
- `bitrix24_created=true`
- `bitrix_method=crm.lead.add`
- `bitrix_id=826`
- отчёт: `data/reports/agent5_bitrix_lead_test.json`

### Что было внешним действием

Только один тестовый вызов Bitrix24 `crm.lead.add`.

### Что не запускалось

- Telegram-отправка;
- IMAP;
- Redis-очереди;
- LLM/API;
- платные API;
- массовый сбор;
- реальные публикации;
- `orchestrator/scheduler.py`.

### Следующий маленький шаг

В Bitrix24 открыть лид `826`, проверить, что поля читаются нормально, затем удалить/закрыть этот тестовый лид, чтобы он не мешал реальной CRM.

## 2026-05-07 — Bitrix24 test lead: причина `insufficient_scope`

### Итог

Повторный запуск тестового Bitrix24-лида из обычного терминала тоже не создал лид:

```text
bitrix_send_status=FAILED
bitrix_id=None
```

### Проверено

- `BITRIX24_WEBHOOK_URL=SET`
- `STARTS_HTTPS=SET`
- `HAS_REST=SET`
- `ENDS_SLASH=SET`
- `bitrix_payload_status=OK`
- `bitrix24_attempted=true`
- `bitrix24_created=false`
- отчёт: `data/reports/agent5_bitrix_lead_test.json`

### Что произошло

В логах Bitrix24 вернул:

```text
insufficient_scope
```

Это значит: адрес webhook записан и payload Agent 5 собрался правильно, но у входящего webhook нет права `crm`, которое нужно для метода `crm.lead.add`.

### Что не запускалось

- Telegram-отправка;
- IMAP;
- Redis-очереди;
- LLM/API;
- платные API;
- массовый сбор;
- реальные публикации;
- `orchestrator/scheduler.py`.

### Следующий маленький шаг

В Bitrix24 создать новый входящий webhook с правом `CRM` и пользователем, который может создавать лиды, затем заменить `BITRIX24_WEBHOOK_URL` в `.env` и повторить:

```bash
.venv/bin/python scripts/test_agent5_bitrix_lead.py
```

Нужный результат:

```text
bitrix_send_status=OK
bitrix_id=<номер>
```

## 2026-05-07 — Bitrix24 test lead: создание из Codex не прошло

### Итог

Создан скрипт:

```bash
.venv/bin/python scripts/test_agent5_bitrix_lead.py
```

Он создаёт один тестовый лид Bitrix24 с пометкой:

```text
ТЕСТ Agent 5 — удалить после проверки
```

### Проверено

- `BITRIX24_WEBHOOK_URL=SET`
- `bitrix_payload_status=OK`
- `bitrix_send_status=FAILED`
- `bitrix_id=None`
- отчёт: `data/reports/agent5_bitrix_lead_test.json`

### Что произошло

Из Codex-среды клиент Bitrix24 не получил ответ:

```text
All attempts to get data from server exhausted
```

Вероятная причина: сетевое ограничение Codex-среды или недоступность webhook именно из неё.

### Что не запускалось

- Telegram-отправка;
- IMAP;
- Redis-очереди;
- LLM/API;
- платные API;
- массовый сбор;
- реальные публикации;
- `orchestrator/scheduler.py`.

### Следующий маленький шаг

Повторить тот же скрипт в обычном терминале проекта:

```bash
.venv/bin/python scripts/test_agent5_bitrix_lead.py
```

Нужный результат:

```text
bitrix_send_status=OK
bitrix_id=<номер>
```

## 2026-05-07 — Agent 5 Telegram test закрыт

### Итог

Повторный запуск тестового Telegram-уведомления успешен:

```text
telegram_send_status=OK
```

### Проверено

- `TELEGRAM_BOT_TOKEN=SET`
- `TELEGRAM_MANAGER_CHAT_ID=SET`
- `telegram_payload_status=OK`
- `telegram_send_status=OK`
- отчёт: `data/reports/agent5_telegram_notify_test.json`

### Что было внешним действием

Только одно тестовое Telegram-сообщение менеджеру.

### Что не запускалось

- Bitrix24 API;
- IMAP;
- Redis-очереди;
- LLM/API;
- платные API;
- массовый сбор;
- реальные публикации;
- `orchestrator/scheduler.py`.

### Следующий маленький шаг

Перед следующим внешним действием согласовать тестовый лид в Bitrix24.

Если запускаем, он должен быть явно помечен как `ТЕСТ`, чтобы его можно было безопасно удалить/закрыть в CRM.

## 2026-05-07 — Agent 5 Telegram test: нужен настоящий chat id

### Итог

Первый реальный тест Telegram-уведомления пока не закрыт.

Payload собрался, но отправка не выполнена, потому что:

- `TELEGRAM_BOT_TOKEN=SET`
- `TELEGRAM_MANAGER_CHAT_ID=INVALID_OR_EMPTY`

Проверка показала: `TELEGRAM_MANAGER_CHAT_ID` сейчас равен `0`.

### Что добавлено

- `scripts/test_agent5_telegram_notification.py` — отправляет одно тестовое уведомление Agent 5.
- `scripts/set_telegram_manager_chat_id_from_updates.py` — берёт chat id из последних сообщений бота и записывает в `.env`, не показывая значение.
- `scripts/set_env_secret.py` теперь не принимает `TELEGRAM_MANAGER_CHAT_ID=0`.

### Ограничение

Codex-сеанс не смог обратиться к Telegram API из-за сетевого ограничения среды: `NETWORK_ERROR`.

### Следующий маленький шаг

1. В Telegram открой уведомительного бота, чей токен записан в `TELEGRAM_BOT_TOKEN`.
2. Отправь ему любое сообщение, например `тест`.
3. В обычном терминале проекта запусти:

```bash
.venv/bin/python scripts/set_telegram_manager_chat_id_from_updates.py
```

Ожидаемый результат:

```text
TELEGRAM_MANAGER_CHAT_ID=SET
```

4. Потом повторить тест:

```bash
.venv/bin/python scripts/test_agent5_telegram_notification.py
```

Ожидаемый результат:

```text
telegram_send_status=OK
```

## 2026-05-07 — Agent 5 dry-run payload выполнен

### Итог

Создан и выполнен локальный dry-run Agent 5:

```bash
.venv/bin/python scripts/dry_run_agent5_payload.py
```

### Что проверено

- `QualifiedLead` берётся из синтетического dry-run;
- поля для Bitrix24 собираются локально;
- Telegram-уведомление менеджеру собирается локально;
- ничего не отправляется наружу.

### Результат

- `qualified_lead_status=OK`
- `bitrix_payload_status=OK`
- `telegram_payload_status=OK`
- `bitrix_method=crm.lead.add`
- `bitrix_field_count=10`
- `telegram_message_chars=492`
- отчёт: `data/reports/agent5_payload_dry_run.json`

### Безопасность

Внешние вызовы не выполнялись:

- Redis-очереди;
- LLM/API;
- Bitrix24 API;
- Telegram-отправка;
- IMAP;
- `orchestrator/scheduler.py`;
- массовый сбор;
- реальные публикации.

Тестовый контакт в отчёте замаскирован как `REDACTED`.

### Следующий маленький шаг

Перед первым реальным внешним тестом выбрать один вариант:

- тестовое Telegram-уведомление менеджеру;
- тестовый лид в Bitrix24.

## 2026-05-07 — Первый безопасный dry-run лида выполнен

### Итог

Создан и выполнен локальный dry-run:

```bash
.venv/bin/python scripts/dry_run_synthetic_lead.py
```

### Что проверено

- `RawLead` создаётся;
- фильтр нецелевого не отсекает целевой лид;
- локальное обогащение достаёт поля;
- `QualifiedLead` собирается;
- результат сохраняется в локальный JSON-отчёт.

### Результат

- `raw_lead_status=OK`
- `offtopic_status=OK_NOT_OFFTOPIC`
- `qualified_lead_status=OK`
- `score=hot`
- `recommended_action=позвонить сегодня`
- `flow=B`
- отчёт: `data/reports/synthetic_lead_dry_run.json`

### Внешние вызовы

Не запускались:

- Redis-очереди;
- LLM/API;
- Bitrix24;
- Telegram-отправка;
- IMAP;
- `orchestrator/scheduler.py`;
- массовый сбор;
- реальные публикации.

### Следующий маленький шаг

Проверить Agent 5 в сухом режиме: сформировать локальный Bitrix/TG payload по `QualifiedLead`, но ничего не отправлять.

## 2026-05-07 — Telegram sender-сессия создана

### Итог

Создана отдельная Telethon-сессия отправки:

- `TG_MONITOR_SESSION=SET`
- `TG_SENDER_SESSION=SET`

Авторизация прошла как:

```text
sender авторизован: @wektorpluspro
```

### Что теперь закрыто для первого технического MVP

- `.env` обязательные поля: `SET`
- Redis: установлен и запущен, пользовательский терминал дал `PONG`
- Telegram `monitor`: `SET`
- Telegram `sender`: `SET`

### Не запускалось

Bitrix24 API, IMAP-подключение, отправка Telegram-сообщений, платные API, массовый сбор, реальные публикации и `orchestrator/scheduler.py`.

### Следующий маленький шаг

Сделать безопасный dry-run на одном синтетическом лиде:

- без IMAP;
- без Bitrix24 API;
- без отправки Telegram-сообщений;
- без `orchestrator/scheduler.py`;
- только проверить, что локальные модели и пайплайн готовы принять один тестовый лид.

## 2026-05-07 — Telegram monitor-сессия создана

### Итог

Создана Telethon-сессия мониторинга:

- `TG_MONITOR_SESSION=SET`
- `TG_SENDER_SESSION=MISSING`

Авторизация прошла как:

```text
monitor авторизован: @wektorpluspro
```

### Что закрыто

Сессия `monitor` для Agent 6 `tg_monitor` закрыта.

### Что ещё блокирует запуск

Нужна отдельная `sender`-сессия, чтобы отправка сообщений не использовала тот же SQLite session-файл, что мониторинг.

### Следующий маленький шаг

```bash
.venv/bin/python scripts/auth_telegram_session.py sender
```

После успешного сообщения `sender авторизован: ...` проверить появление `data/tg_sender_session.session`.

## 2026-05-07 — Telethon: TELEGRAM_PHONE слишком короткий

### Итог

Ошибка:

```text
PhoneNumberInvalidError
```

означает, что Telegram не принял номер телефона.

### Безопасная проверка

- `TELEGRAM_API_ID=SET`
- `TELEGRAM_API_HASH=SET`
- `TELEGRAM_PHONE=INVALID_TOO_SHORT`

Значение номера не показывалось.

### Что нужно сделать

Записать полный номер Telegram в формате без пробелов:

```text
+7XXXXXXXXXX
```

Команда:

```bash
.venv/bin/python scripts/set_env_secret.py TELEGRAM_PHONE
```

Потом повторить:

```bash
.venv/bin/python scripts/auth_telegram_session.py monitor
```

### Улучшение

`scripts/auth_telegram_session.py` теперь сам убирает пробелы, скобки и дефисы из номера и заранее показывает безопасный статус, если номер слишком короткий или без `+`.

## 2026-05-07 — Telethon monitor не стартовал из-за TELEGRAM_API_ID

### Итог

Команда:

```bash
.venv/bin/python scripts/auth_telegram_session.py monitor
```

не смогла стартовать, потому что `TELEGRAM_API_ID` оказался невалидным для Telethon.

### Безопасная проверка

- `TELEGRAM_API_ID=INVALID_OR_EMPTY`
- `TELEGRAM_API_HASH=SET`
- `TELEGRAM_PHONE=SET`

Значения не показывались.

### Что нужно сделать

Найти настоящий числовой `api_id` в Telegram:

```text
https://my.telegram.org/apps
```

Потом записать его локально:

```bash
.venv/bin/python scripts/set_env_secret.py TELEGRAM_API_ID
```

После этого повторить:

```bash
.venv/bin/python scripts/auth_telegram_session.py monitor
```

### Важно

`TELEGRAM_API_ID` — это не bot token, не телефон и не `api_hash`. Это короткое число из Telegram API Development Tools.

## 2026-05-07 — Redis закрыт, следующий шаг Telegram-сессии

### Итог

Redis установлен и запущен.

Пользовательский терминал показал:

```bash
PONG
```

### Проверено дополнительно

- `REDIS_CLI=SET`
- `REDIS_SERVER=SET`
- `brew services`: `redis started`
- `redis-server` слушает `127.0.0.1:6379`

### Ограничение Codex-сеанса

Прямой `redis-cli ping` внутри Codex заблокирован песочницей с ошибкой `Operation not permitted`.

Это не считаем ошибкой Redis, потому что обычный терминал получил `PONG`, а процесс Redis слушает порт.

### Ещё блокирует запуск

- `TELEGRAM_SESSION_FILES_COUNT=0`

### Следующий маленький шаг

Создать первую Telethon-сессию:

```bash
.venv/bin/python scripts/auth_telegram_session.py monitor
```

После успешной авторизации проверить появление session-файла. Потом отдельно создать:

```bash
.venv/bin/python scripts/auth_telegram_session.py sender
```

## 2026-05-07 — `.env` для MVP закрыт, Redis ещё не установлен

### Итог

Обязательные поля `.env` для первого технического MVP теперь заполнены.

Значения секретов не показывались.

### Закрыто по `.env`

- `ANTHROPIC_API_KEY=SET`
- `TELEGRAM_BOT_TOKEN=SET`
- `TELEGRAM_MANAGER_CHAT_ID=SET`
- `TELEGRAM_API_ID=SET`
- `TELEGRAM_API_HASH=SET`
- `TELEGRAM_PHONE=SET`
- `BITRIX24_WEBHOOK_URL=SET`
- `IMAP_HOST=SET`
- `IMAP_PORT=SET`
- `GMAIL_USER=SET`
- `GMAIL_APP_PASSWORD=SET`
- `GMAIL_TENDER_FOLDER=SET`
- `REDIS_URL=SET`
- `DATABASE_URL=SET`

### Ещё блокирует запуск

- `REDIS_CLI=MISSING`
- `REDIS_SERVER=MISSING`
- `REDIS_RUNNING=EMPTY`
- `TELEGRAM_SESSION_FILES_COUNT=0`

### Agent 4 / MAX publisher

Поля реальной публикации пока пустые. Это не блокирует первый MVP по лидам, но блокирует реальные публикации.

### Не запускалось

Redis, Telegram-сессии, Bitrix24 API, IMAP-подключение, платные API, массовый сбор, реальные публикации и `orchestrator/scheduler.py`.

### Следующий маленький шаг

Установить и запустить Redis, затем проверить:

```bash
redis-cli ping
```

Цель: получить `PONG`.

## 2026-05-07 — Почта для tender_collector: Яндекс.Почта через IMAP

### Итог

Уточнено: почта для тендерных писем — Яндекс.Почта, не Gmail.

Агент 2 `tender_collector` больше не привязан жёстко к Gmail: добавлены `IMAP_HOST` и `IMAP_PORT`.

### Текущий статус почтового блока

- `IMAP_HOST=SET`
- `IMAP_PORT=SET`
- `GMAIL_TENDER_FOLDER=SET`
- `GMAIL_USER=EMPTY`
- `GMAIL_APP_PASSWORD=EMPTY`

### Важно про названия

`GMAIL_USER` и `GMAIL_APP_PASSWORD` — старые технические имена переменных.

Для Яндекс.Почты туда записываем:

- `GMAIL_USER` — полный email Яндекса;
- `GMAIL_APP_PASSWORD` — пароль приложения Яндекс.Почты.

### Команды для следующего шага

```bash
.venv/bin/python scripts/set_env_secret.py GMAIL_USER
.venv/bin/python scripts/set_env_secret.py GMAIL_APP_PASSWORD
```

### Не запускалось

Redis, Telegram-сессии, Bitrix24 API, IMAP-подключение, платные API, массовый сбор, реальные публикации и `orchestrator/scheduler.py`.

### Следующий маленький шаг

Создать пароль приложения в Яндекс ID для почты, записать `GMAIL_USER` и `GMAIL_APP_PASSWORD`, затем повторить безопасную проверку `SET/EMPTY/MISSING`.

## 2026-05-07 — Bitrix24 webhook записан

### Итог

`BITRIX24_WEBHOOK_URL=SET`.

Значение webhook не показывалось и не записывалось в отчёты.

### Текущий статус MVP `.env`

- `ANTHROPIC_API_KEY=SET`
- `TELEGRAM_BOT_TOKEN=SET`
- `TELEGRAM_MANAGER_CHAT_ID=SET`
- `TELEGRAM_API_ID=SET`
- `TELEGRAM_API_HASH=SET`
- `TELEGRAM_PHONE=SET`
- `BITRIX24_WEBHOOK_URL=SET`
- `GMAIL_TENDER_FOLDER=SET`
- `REDIS_URL=SET`
- `DATABASE_URL=SET`

### Всё ещё блокирует запуск

- `GMAIL_USER=EMPTY`
- `GMAIL_APP_PASSWORD=EMPTY`
- Telegram session-файлы в `data/` пока не найдены.

### Не запускалось

Redis, Telegram-сессии, Bitrix24 API, Gmail, платные API, массовый сбор, реальные публикации и `orchestrator/scheduler.py`.

### Следующий маленький шаг

Записать:

```bash
.venv/bin/python scripts/set_env_secret.py GMAIL_USER
.venv/bin/python scripts/set_env_secret.py GMAIL_APP_PASSWORD
```

После этого повторить безопасную проверку и перейти к Telegram-сессиям.

## 2026-05-07 — Часть `.env` заполнена, остались Bitrix24 и Gmail

### Итог

Проверка выполнена безопасно: значения секретов не показывались.

### Теперь заполнено

- `ANTHROPIC_API_KEY=SET`
- `TELEGRAM_BOT_TOKEN=SET`
- `TELEGRAM_MANAGER_CHAT_ID=SET`
- `TELEGRAM_API_ID=SET`
- `TELEGRAM_API_HASH=SET`
- `TELEGRAM_PHONE=SET`
- `REDIS_URL=SET`
- `DATABASE_URL=SET`

### Всё ещё пусто и блокирует MVP

- `BITRIX24_WEBHOOK_URL=EMPTY`
- `GMAIL_USER=EMPTY`
- `GMAIL_APP_PASSWORD=EMPTY`

### Не запускалось

- Redis;
- Telegram-сессии;
- Bitrix24 API;
- Gmail;
- платные API;
- массовый сбор;
- реальные публикации;
- `orchestrator/scheduler.py`.

### Следующий маленький шаг

Создать входящий webhook в Bitrix24 с правами CRM и записать его в `.env` через:

```bash
.venv/bin/python scripts/set_env_secret.py BITRIX24_WEBHOOK_URL
```

Потом заполнить `GMAIL_USER` и `GMAIL_APP_PASSWORD`.

## 2026-05-07 — `.env` проверен перед MVP-прогоном

### Итог

Первый сквозной MVP-тест пока не запускаем.

Причина: обязательные поля в `.env` заполнены не полностью.

### Проверено безопасно

- `.env=SET`
- `.env.example=SET`
- значения секретов не показывались;
- использовались только статусы `SET` / `EMPTY` / `MISSING`;
- Redis, Telegram, Bitrix24, платные API, массовый сбор и `orchestrator/scheduler.py` не запускались.

### Обязательные MVP-поля

| Поле | Статус |
|---|---|
| `ANTHROPIC_API_KEY` | `EMPTY` |
| `TELEGRAM_BOT_TOKEN` | `EMPTY` |
| `TELEGRAM_MANAGER_CHAT_ID` | `SET` |
| `TELEGRAM_API_ID` | `SET` |
| `TELEGRAM_API_HASH` | `EMPTY` |
| `TELEGRAM_PHONE` | `SET` |
| `BITRIX24_WEBHOOK_URL` | `EMPTY` |
| `GMAIL_USER` | `EMPTY` |
| `GMAIL_APP_PASSWORD` | `EMPTY` |
| `GMAIL_TENDER_FOLDER` | `SET` |
| `REDIS_URL` | `SET` |
| `DATABASE_URL` | `SET` |

### Agent 4 / MAX publisher

Поля для реальной генерации, озвучки, видео и публикаций пока в основном пустые. Это не блокирует первый технический MVP по лидам, но блокирует реальные публикации.

Ключевые пустые поля: `MAX_BOT_TOKEN`, `MAX_CHAT_ID`, `POSTMYPOST_TOKEN`, `POSTMYPOST_PROJECT_ID`, `OPENROUTER_API_KEY`, `REPLICATE_API_TOKEN`, `ELEVENLABS_API_KEY`, `PUBLISHER_TELEGRAM_BOT_TOKEN`, `PUBLISHER_TELEGRAM_CHANNEL_ID`.

### Дополнительно

Telegram session-файлы в `data/` не найдены. После заполнения Telegram API-полей нужно будет отдельно создать/проверить сессии `tg_monitor` и `sender`.

### Следующий маленький шаг

Заполнить в локальном `.env`:

- `ANTHROPIC_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_API_HASH`
- `BITRIX24_WEBHOOK_URL`
- `GMAIL_USER`
- `GMAIL_APP_PASSWORD`

После этого повторить безопасную проверку `SET/EMPTY/MISSING`. Только если обязательные поля будут закрыты, переходить к Redis.

## 2026-05-07 — Фокус этого чата: многоагентная система

### Важно

В этом чате продолжаем разработку многоагентной системы `design-studio-lead-engine`.

Сайт ведётся отдельно в другой ветке/чате проекта. Здесь сайт не является текущим незакрытым шагом.

### Где остановились по многоагентной системе

Система уже собрана архитектурно:

```text
Agent 1 Scout -> Agent 2 Collector -> Agent 3 Processor -> Agent 5 CRM/Analytics -> Agent 6 Outreach
```

Agent 4 Publisher существует как внутренний контент-движок, но не является блокером первого технического MVP-прогона.

### Текущий незакрытый шаг

Первый сквозной MVP-тест пока не запускаем.

Причина: нужно безопасно проверить готовность базовых входов:

```text
.env -> Redis -> Telegram-сессии -> Bitrix24 -> один сквозной тест
```

### Следующий маленький шаг

Безопасно проверить `.env` и `.env.example`:

- не показывать значения секретов;
- показывать только `SET` / `EMPTY` / `MISSING`;
- определить, какие обязательные поля MVP ещё пустые;
- если есть пустые обязательные поля, не запускать Redis и систему.

## 2026-05-07 — Синхронизация: сайт уже создан и редактируется

### Итог

Сайт уже не только на этапе ТЗ. В другом чате создана локальная рабочая версия сайта:

```text
site/
```

Внутри есть:

- `site/index.html`
- `site/assets/styles.css`
- `site/assets/app.js`
- `site/README.md`
- `site/assets/vpp-logo-full.png`
- `site/assets/vpp-logo-mark.png`

Открытие сайта:

```bash
./OPEN_SITE.command
```

Команду запускать из корня проекта.

### Важно

- Старый Bitrix24-сайт не использовать как будущую публичную ссылку.
- Новый сайт сейчас локальный и редактируется.
- Vercel/GitHub-деплой не запускался.
- Публикации нет.
- Внешние карточки, канал `СИЛА Проекта`, CRM, `.env`, токены и секреты не трогались.

### Следующий маленький шаг

Открыть локальный сайт через `./OPEN_SITE.command` и глазами проверить:

- шапку и логотип;
- первый экран;
- услуги;
- контакты;
- мобильную версию.

После этого править только точечные замечания.

## 2026-05-07 — Обязательный следующий GEO/AI-шаг зафиксирован

### Итог

Документ подготовлен:

```text
docs/geo-ai-source-of-truth.md
```

Зачем: связать для AI и поиска единый публичный след компании:

```text
ООО Вектор Плюс-Про -> ИНН/ОГРН -> сайт -> СРО -> услуги -> кейсы -> СИЛА Проекта
```

### Где зафиксировано

- `tasks/geo-ai-source-of-truth-next-step.md`
- `tasks/geo-ai-lead-source-backlog.md`
- `tasks/roadmap.md`
- `research/geo-ai-visibility-audit.md`
- `REPORT.md`

### Важно

Этот шаг не означает публикацию без согласования, не добавляет новых агентов и не меняет MVP-архитектуру.

### Следующий маленький шаг

Черновик блока `О компании` для сайта и канала `СИЛА Проекта` подготовлен:

```text
docs/about-company-and-channel-draft.md
```

Реальные ссылки и контакты добавлены в черновик, но Яника уточнила: старый Bitrix24-сайт не добавлять как будущую публичную ссылку. Новый сайт будем делать внутри текущей многоагентной структуры.

Ссылка 2GIS добавлена: `https://2gis.ru/krasnodar/firm/70000001103967582`.

Структура нового сайта подготовлена:

```text
docs/new-site-structure.md
```

ТЗ/промпт для Claude Design создан:

```text
docs/new-site-design-brief.md
```

Актуальный следующий маленький шаг: открыть локальный сайт через `./OPEN_SITE.command` и проверить шапку, первый экран, услуги, контакты и мобильную версию. Ничего не публиковать без отдельного подтверждения.

## 2026-05-06 — MVP-readiness проверен

### Итог

Первый сквозной MVP-тест пока не запускаем.

Причина простая: система уже собрана по логике агентов, но базовые входы ещё не готовы.

### Что проверено безопасно

- `REPORT.md`, `CLAUDE.md`, `tasks/session-notes.md`, `docs/agent-system-gap-check.md`, `../../lessons/system/agent-block-schemes-and-creation-map.md`, `tasks/next-mvp-readiness-check-2026-05-06.md` прочитаны.
- `.env=SET`, `.env.example=SET`.
- Секреты не показывались, использовались только `SET` / `EMPTY` / `MISSING`.
- Обязательные MVP-поля частично пустые: `ANTHROPIC_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_API_HASH`, `BITRIX24_WEBHOOK_URL`, `GMAIL_USER`, `GMAIL_APP_PASSWORD`, `DATABASE_URL`.
- Redis не готов: `REDIS_URL=SET`, `REDIS_PING=EMPTY`.
- Telegram-сессии не готовы: `TG_MONITOR_SESSION=MISSING`, `TG_SENDER_SESSION=MISSING`.
- Bitrix24 не готов: `BITRIX24_WEBHOOK_URL=EMPTY`.
- Agent 4 publisher-поля в рабочем `.env` пока `MISSING`.

### Что не запускалось

- `orchestrator/scheduler.py`.
- Платные API.
- Массовый сбор лидов.
- Реальные публикации.
- Новые агенты.

### Следующий маленький шаг

Заполнить обязательные поля MVP в `.env`, потом повторить проверку `SET` / `EMPTY` / `MISSING`.

## 2026-05-06 — Следующая задача поставлена из lessons

### Безопасная подготовка MVP-прогона

Создан файл задачи:

```text
tasks/next-mvp-readiness-check-2026-05-06.md
```

Смысл задачи:

```text
.env -> Redis -> Telegram-сессии -> Bitrix24 -> один сквозной MVP-тест
```

Главное правило: не добавлять новых агентов и не расширять архитектуру, пока не закрыты базовые блокеры запуска.

Что должен сделать следующий чат проекта:

- безопасно проверить `.env` по статусам `SET/EMPTY/MISSING`;
- не показывать значения секретов;
- определить, какие поля блокируют MVP;
- не запускать платные API, массовый сбор и реальные публикации;
- проверить Redis только после закрытия обязательных `.env` полей;
- дать список ручных действий для Яны;
- обновить `REPORT.md` и `tasks/session-notes.md`.

Готовый полный промпт для запуска лежит в файле задачи.

## 2026-04-28 — Сессия 13 (Этап 0: аудит и фикс)

### Аудит + все критические баги исправлены

#### Что исправлено (9 файлов)

| Файл | Баг | Фикс |
|---|---|---|
| `shared/db.py` | `create_engine(None)` падал при импорте | Ленивая инициализация `_get_engine()` |
| `shared/redis_client.py` | Нет bot_state хелперов → approver создавал прямые Redis-коннекты | Добавлены `set/get/delete_bot_state()` |
| `lead_detector/__init__.py` | `lead.model_dump()` — datetime не сериализуется в JSON | `lead.model_dump(mode="json")` |
| `approver/__init__.py` | MarkdownV2 + динамический контент → TG падал | HTML parse_mode + `html.escape()`, убраны прямые Redis-коннекты |
| `tg_monitor/__init__.py` | `push_raw`, `RawLead`, `ALL_KEYWORDS` — мёртвые импорты | Убраны, docstring исправлен |
| `sender/__init__.py` | Та же сессия что tg_monitor → SQLite race condition | Отдельный `data/tg_sender_session` |
| `agent5_crm/__init__.py` | OutreachLead из `leads:outreach` никем не обрабатывался | Добавлен поток 2 + `_outreach_to_qualified()` |
| `requirements.txt` | `anthropic==0.28.0` не поддерживает claude-4.x модели | Обновлено до `anthropic>=0.50.0` |
| `data/.gitkeep` | Директория `data/` не существовала — Telethon не мог писать сессии | Создана `data/` с `.gitkeep` |

#### Синтакс-чек: 12 файлов ✅ — ноль ошибок

#### Следующий шаг (Этап 1 — credentials, делает Яна/Сергей)
Без этого запуск невозможен — см. чеклист ниже.

---

## 2026-04-28 — Сессия 12

### Агент 6 — полная цепочка аутрича (Волна 1)

#### Что сделано
- `shared/redis_client.py` — добавлены очереди и функции для аутрич-пайплайна: `outreach:candidates`, `outreach:for_approval`, `outreach:approved`, `outreach:sent`
- `agent6_outreach/tg_monitor/__init__.py` — теперь пушит кандидатов в `outreach:candidates` + добавлен `reply_handler` для отслеживания ответов на наши сообщения
- `agent6_outreach/relevance/__init__.py` — Claude Haiku оценка 0–10, порог 7, до 10 кандидатов за вызов
- `agent6_outreach/responder/__init__.py` — Claude Sonnet генерация живого ответа от имени сотрудника ВПП
- `agent6_outreach/approver/__init__.py` — python-telegram-bot daemon: ✅/✏️/❌, TTL 30 мин, Redis state для edit-диалога
- `agent6_outreach/sender/__init__.py` — Telethon daemon: задержка 2–15 мин рандом, дневной лимит OUTREACH_MAX_REPLIES_PER_DAY, tracking в Redis
- `agent6_outreach/lead_detector/__init__.py` — Claude Haiku детектор интереса, вызывается из tg_monitor, OutreachLead → leads:outreach → Агент 5
- `orchestrator/scheduler.py` — добавлены `start_approver()`, `start_sender()`, `run_relevance_pipeline()` каждые 2 мин

#### Полный аутрич-цикл теперь замкнут
```
tg_monitor (видит пост) → outreach:candidates
  ↓ каждые 2 мин (APScheduler)
relevance (Haiku score) → responder (Sonnet reply) → outreach:for_approval
  ↓ approver daemon (TG-бот)
менеджер ✅/✏️/❌ → outreach:approved
  ↓ sender daemon (Telethon)
отправка с задержкой 2–15 мин → outreach:sent (hash)
  ↓ tg_monitor reply_handler + lead_detector
если интерес → OutreachLead → leads:outreach → Агент 5 → Bitrix24 + TG
```

#### Следующий шаг (Сессия 13)
**Avito коллектор** (Агент 2, Волна 1, Шаг 4):
`agent2_collector/avito_collector/` — мониторинг поисковой выдачи Avito по ключевым словам, ротация User-Agent, → RawLead → Redis

Перед этим можно сделать сквозной ручной тест цепочки аутрича:
1. Добавить тестового кандидата в `outreach:candidates` вручную через redis-cli
2. Убедиться что relevance его обрабатывает
3. Проверить что approver присылает TG-сообщение с кнопками

---

## 2026-04-28 — Сессия 11

### Агент 3 — полный Процессор лидов + CRM-роутер + оркестратор

#### Что сделано
- `agent3_processor/cleaner/` — дедупликация по fingerprint (MD5 hash, Redis SET, TTL 30 дней) + стоп-слова нецелевых
- `agent3_processor/enricher/` — regex: 50 городов, 8 типов объектов, площадь, телефон/email/TG
- `agent3_processor/scorer/` — Claude API → JSON {score, reason}, 4 варианта: hot/warm/cold/off
- `agent3_processor/offer_gen/` — Claude API → текст первого сообщения (только для hot/warm), для cold шаблон
- `agent3_processor/__init__.py` — склейка пайплайна: cleaner → enricher → scorer → offer_gen → push_qualified
- `agent5_crm/__init__.py` — runner: pop_qualified → create_lead (Bitrix) → notify (TG)
- `agent5_crm/notifier/__init__.py` — TG уведомления 🔥⚡🤝❌ с Markdown форматированием
- `orchestrator/scheduler.py` — исправлены пути импортов, добавлен tg_monitor в daemon-поток, правильное расписание

#### Сквозной пайплайн теперь полон (MVP Волна 1 — коллектор + процессор)
```
tender_collector (Gmail) → Redis:raw → agent3_processor → Redis:qualified → agent5_crm → Bitrix24 + TG
tg_monitor (Telethon) → Redis:raw → тот же пайплайн
```

#### Следующий шаг (Сессия 12)
Цепочка аутрича Агент 6 (без неё мониторинг видит лиды но не отвечает):
1. `agent6_outreach/relevance/` — Claude API оценка 0–10
2. `agent6_outreach/responder/` — генерация первого ответа как человек
3. `agent6_outreach/approver/` — TG-бот ✅/✏️/❌ с таймаутом 30 мин
4. `agent6_outreach/sender/` — Telethon отправка с задержкой 2–15 мин
5. `agent6_outreach/lead_detector/` — интерес в ответе → Агент 5

---

## 2026-04-28 — Сессия 10

### GitHub-аудит + первый рабочий код агентов

#### Что сделано
- Проведён аудит GitHub: найдены и сравнены лучшие репозитории по теме
- В `requirements.txt` добавлены: `imap-tools==1.6.0` и `fast-bitrix24==1.5.12`
- Написан рабочий код (не заглушки):
  - `agents/agent2_collector/tender_collector/__init__.py` — Gmail IMAP через `imap-tools`, создаёт RawLead → Redis
  - `agents/agent5_crm/bitrix/__init__.py` — Bitrix24 через `fast-bitrix24`: create_lead, update_lead, add_note
  - `agents/agent6_outreach/tg_monitor/__init__.py` — Telethon реалтайм мониторинг чатов по ALL_KEYWORDS
  - `agents/agent6_outreach/sales_dialog/__init__.py` — стадийный диалог (intro→qualification→proposal→objection→closing→handoff), концепция SalesGPT, реализация через Claude API
  - `shared/redis_client.py` — добавлен blocklist (Redis SET): add_to_blocklist, is_blocked, blocklist_size

#### Какие библиотеки взяли и почему
- `imap-tools` (500+ ⭐, MIT, free) — чистый Python IMAP, заменяет imaplib
- `fast-bitrix24` (104 ⭐, MIT, free, российский автор) — async/sync REST wrapper Bitrix24
- Концепция SalesGPT (2.5k ⭐) — взяли стадийную машину состояний, переписали под Claude API без LangChain
- Паттерн telegram-keyword-monitor — взяли подход, реализовали через наш Telethon

#### Что НЕ взяли
- CrewAI / LangGraph — пришлось бы переписывать всю архитектуру
- brightdata — платный сервис
- kaymen99/sales-outreach — LinkedIn + HubSpot, не наши платформы

#### Роадмап
Создан полный роадмап: `tasks/roadmap.md` — три волны, порядок, зависимости.

#### Следующий шаг (Сессия 11)
**Агент 3 — Процессор лидов** (без него лиды копятся в Redis и никуда не движутся):
1. `agent3_processor/cleaner/` — дедупликация + фильтр нецелевых
2. `agent3_processor/enricher/` — извлечение города, типа объекта, контакта
3. `agent3_processor/scorer/` — Claude API → hot/warm/cold/off
4. `agent3_processor/offer_gen/` — Claude API → персональный оффер
5. `agent3_processor/__init__.py` — склейка пайплайна
6. `agent5_crm/notifier/__init__.py` — TG-уведомления менеджеру

После этого — первый сквозной тест: tender_collector → Redis → Агент 3 → Bitrix24 → TG

---

## 2026-04-28 — Сессия 9

### Контент-стратегия + интеграция Max-канала

#### Что сделано
- Разработана контент-стратегия: 5 каналов, разный голос, не дублируется
- MAX = Поток А (перепланировки, бот ПРОВЕРКА)
- Telegram = оба потока, акцент Б, экспертный голос от ГИПа
- VK = Поток А + жизнь компании, разговорный стиль
- Дзен = SEO-статьи оба потока, 1500-3000 слов
- Карты/2GIS = локальный поиск, новости, фото
- Добавлены `dzen_poster` и `content_pipeline` в Агент 4
- "Канал Мах перепланировка" полностью интегрирован в lead engine:
  - 18 готовых постов → `content/library/posts/`
  - Шаблоны визуалов → `content/library/templates/`
  - Промпты на изображения → `content/library/visual_prompts/`
  - Реестры источников/идей → `content/library/sources/`
  - Стратегические документы → `content/strategy/`
  - Бот ПРОВЕРКА спецификация → `content/bot_spec/` (заменить Gemini на Claude API)
- Проект "Канал Мах перепланировка" закрыт как отдельный (активы перенесены)
- "max-ai-automation-channel" — отдельное направление Яники, не трогать
- CLAUDE.md обновлён: контент-стратегия + полная карта агентов v2

#### Важные решения
- profi_collector поднят в Волну 1 (с авторизацией через Playwright)
- tender_intel возвращён (коммерческие площадки с открытыми ценами)
- content_spy переименован в content_pipeline (собирает + переписывает + в очередь)
- review_monitor добавлен в Агент 1 (перехват недовольных клиентов конкурентов)
- cold_email добавлен в Агент 6 (B2B рассылка застройщикам с рабочего email)
- `admin_bot` добавлен в Агент 5 — TG-бот управления: /status /restart /stop /logs /pause
- Первый пост опубликован в MAX «СИЛА Проекта» (draft-002, 2026-04-28)
- Журнал публикаций: `content/pipeline/published-log.md`
- Правила стиля постов зафиксированы в memory

#### Следующий шаг
Агент 2: `tender_collector` — Gmail/IMAP парсинг тендерных писем → Redis

---

## 2026-04-28 — Сессия 8

### Финализация структуры агентов + CLAUDE.md

#### Что сделано
- Запущен агент-аналитик — независимо оценил всю архитектуру
- Принята плоская структура Агента 6 (было `monitor/tg` → стало `tg_monitor`)
- Убраны нежизнеспособные субагенты: `profi_spy`, `content_spy`, `tender_spy`
- Перенесены в Волну 2-3: `ya_uslugi`, `hh`, `youdo`, `property_signal`, `sales_dialog`
- Переименования: `tender` → `tender_collector`, `kp_trigger` → `proposal_trigger`, `analyst` → `stats_reporter`, `dialog` → `sales_dialog`
- Создана полная структура папок всех агентов и субагентов с `__init__.py`
- Создан `CLAUDE.md` проекта — полная карта агентов, правила, связанные проекты
- Исправлен путь Obsidian MCP в `~/.claude/settings.json`

#### Ключевые решения аналитика
- Волна 1 сокращена до реально достижимого MVP: tender_collector + avito + Агент 3 + Агент 5 + tg_monitor + approver
- Добавить в shared/: blocklist (Redis SET) для фильтрации ботов/конкурентов
- Добавить в оркестратор: hard cap токенов Claude API + алерт
- Redis AOF persistence обязательна
- Approver circuit breaker: нет ответа за 30 мин → лид не отправляется

#### Следующий шаг
Агент 2: `tender_collector` — Gmail/IMAP парсинг тендерных писем → Redis

---

## 2026-04-27 — Сессия 7

### Аудит проекта перед стартом кодинга

#### Проверка состояния файлов
- Прочитаны все существующие файлы проекта — инфраструктура (shared/, orchestrator/, config/) подтверждена рабочей
- Все файлы агентов (agents/**/__init__.py) — пустые заглушки, реального кода нет
- Obsidian vault прочитан напрямую через Read (MCP не загрузился в сессии): canvas-файлы `Карта скилов.canvas` и `Система агентов.canvas`

#### Исправление ошибки в памяти
- `tender_scraper.py` находится по пути `modules/tender_scraper.py` (не в корне vpp_bot)
- Файл — заглушка MVP (30 строк): принимает ссылку/файл от менеджера вручную, нет Gmail/IMAP
- **Агент 2 пишется с нуля** — `tender_scraper.py` не использовать как основу

#### Аудит субагентов — добавлены пропущенные (было 41 → стало 46)
Добавлены в `research/multi-agent-system.md`:
- **Диалоговый менеджер** (Агент 6, Реактивный, Волна 1) — SalesGPT-логика когда человек ответил: стадии интерес → квалификация → предложение → закрытие / передача менеджеру
- **Max-монитор** (Агент 6, Реактивный, Волна 2) — мониторинг комментариев в соцсети Max
- **TenChat-монитор** (Агент 6, Реактивный, Волна 2) — B2B: застройщики и девелоперы в TenChat
- **Яндекс Кью-монитор** (Агент 6, Реактивный, Волна 3)
- **TenChat-Охотник** (Агент 6, Hunter, Волна 2)

#### Карта скилов (из Obsidian canvas)
**Реально установлены:** skill-creator, context7-mcp, claude-api, security-review, review, init, update-config, simplify, loop, schedule
**Запланированы но не установлены (Волна 1):** agent-sdk-dev, mcp-server-dev, hookify, telegram plugin, security-guidance, feature-dev, session-report
Зафиксировано в памяти: `memory/reference_skills_map.md`

#### MCP Obsidian
- Конфигурация в `~/.claude/settings.json` правильная ✅
- Пакет `mcp-obsidian-vault` v0.4.0 установлен ✅
- Сервер стартует корректно с `OBSIDIAN_VAULT_PATH` ✅
- **Не загружается в сессии** — требует перезапуска Claude Code
- Workaround: читать vault напрямую через Read tool по пути `/Users/yanika/Documents/Вайбкодинг/Obsidian Vault/`

#### Следующий шаг (не изменился)
Агент 2 — Gmail IMAP-парсер тендерных писем → Redis

---

## 2026-04-24 — Сессии 1–3
- Создан проект, проведено исследование, получена карта источников от владельца.
- Карта v3.0 создана: 8 категорий, 6 подпроектов, инструменты, архитектура пайплайна.

## 2026-04-26 — Сессия 6 (финальная за день)

### Архитектура финализирована
- Добавлен Агент 6: Социальный аутрич v2 — реактивный монитор + Охотник (Hunter)
- Принято решение: без n8n/Make, стек на Python
- Изучены GitHub-репозитории → зафиксированы строительные блоки → `research/github-building-blocks.md`
- Охотник (Hunter): проактивный поиск по истории TG/VK/Avito/HH/форумам
- SalesGPT → диалоговый движок когда человек ответил
- MiloAgent → архитектура A/B тестирования и самообучения
- informer → rate limiting и работа с user accounts в Telethon

### Инфраструктура создана (код)
- Структура папок всего проекта
- `.env.example`, `requirements.txt`, `.gitignore`
- `config/settings.py` — все настройки + ключевые слова потоков А и Б
- `shared/models.py` — RawLead, QualifiedLead, OutreachLead (Pydantic)
- `shared/redis_client.py` — очереди raw/qualified/outreach
- `shared/db.py` — PostgreSQL: LeadRecord, DuplicateFingerprint, AgentLog
- `shared/logger.py` — loguru, единый логгер
- `orchestrator/scheduler.py` — APScheduler, расписание всех агентов

### Obsidian визуализация
- Vault: `/Users/yanika/Documents/Вайбкодинг/Obsidian Vault/`
- Создана папка `Вектор Плюс-Про/`
- `Система агентов.canvas` — полная визуальная карта агентов с цветами и стрелками
- 6 заметок по каждому агенту с деталями и wiki-links

### Obsidian MCP подключён
- Сервер: `mcp-obsidian-vault` v0.4.0
- Настроен в `~/.claude/settings.json`
- Активируется при следующем запуске Claude Code

### Вывод по GitHub
Готового комплексного решения нет. Строим своё, используем блоки:
- parser_avito → Агент 2 (Avito)
- telegram-keyword-monitor + informer → Агент 6 (TG мониторинг)
- SalesGPT → Агент 6 (диалог)
- MiloAgent → Агент 6 (A/B, самообучение)
- kaymen99/sales-outreach → Агент 3 (пайплайн квалификации)
- brightdata/ai-lead-generator → Агент 3 (скоринг)

---

## 2026-04-24–25 — Сессия 4–5

### Уточнения по каналам (от владельца)
- Profi.ru / Яндекс Услуги: **не вели профиль, а откликались на заявки клиентов**. На Профи — платно за отклик, на Услугах — бесплатно до лимита. Оба **работали и давали клиентов** когда были активны.
- Яндекс Карты: **даже точка не настроена** — теряем весь локальный поиск.
- Тендеры: письма с тендерами **приходят каждый день в отдельную папку**, но некому обрабатывать вручную.
- Авито: объявления есть, интерес есть, но заказов мало.

### Компания: ООО «Вектор Плюс-Про»
Прочитаны файлы: О Компании.docx, Общая информация.docx, ЦА.docx, Аналитика.docx, боли.docx, Документ о продукте.docx, idea_project_vpp.md

**Ключевые факты:**
- Команда: Сергей Макеев (ГИП, НОПРИЗ, СРО) + Яна (директор по развитию)
- Два направления: инженерное проектирование (вся Россия, удалённо) + перепланировки под ключ (Краснодар + Краснодарский край)
- Главное УТП: единственные в Краснодаре с полной цепочкой собственный конструктив + перепланировка + сопровождение до ЕГРН
- Конкуренты в Краснодаре: Перестройка 23, КЦСП, Горслужба, Перепланкрд, Goldhands — у всех нет полной цепочки
- Цены: полный цикл перепланировки 55к (рынок 55–150к) — очень конкурентно
- Гарантия: дорабатываем до результата без доплат (если исходные данные не менялись)

### Связанный проект
Уже существует задел KP-генератора (`/идея проекта КП/`):
- Telegram-бот + Web API
- Модуль парсинга тендеров (`tender_scraper.py`) уже написан
- Интеграция с Bitrix24 запланирована
- Lead engine должен подавать лиды в этот пайплайн

### Два отдельных лид-потока
1. **Перепланировки** — локальный поток, Краснодар
2. **Инженерное проектирование** — федеральный поток, вся Россия

**Следующий шаг:** закрыть этап исследования — обновить карту с разделением на два потока и выбрать с чего начинаем MVP.

## 2026-05-17 — Frontend/backend visual integration

- Контекст: пользователь прислал frontend в папке `Многоагентная система-визуал` и попросил “поженить” его с реальными агентами проекта.
- Решение: исходную папку не удалять; создать рабочую структуру `frontend/agent-system-visual` и `backend/agent_dashboard_api`.
- Backend:
  - `backend/agent_dashboard_api/dashboard_data_builder.py` строит graph data из `data/reports/agent_dashboard.json`;
  - `backend/agent_dashboard_api/server.py` отдаёт frontend, `/api/health`, `/api/dashboard`, `/api/agent-system-data` и runtime `/data.js`;
  - режим только read-only, внешние сервисы не запускаются.
- Frontend:
  - скопирован в `frontend/agent-system-visual`;
  - `app.jsx` теперь показывает live local source и generated_at из dashboard;
  - `panels.jsx` показывает реальные `agents`, `subroles`, `channels`, `artifacts`, `safety locks`, `nodes`;
  - `graph.jsx` исправлен: убран лишний `preventDefault` в wheel-handler.
- Проверка:
  - py_compile backend OK;
  - API health OK;
  - API graph data OK: `agents=6`, `subroles=33`, `scenarios=4`;
  - Playwright открыл `http://127.0.0.1:8787/`;
  - консоль: 0 errors, 1 warning от Babel standalone;
  - Playwright проверил scenario playback и inspector Agent 5 CRM;
  - screenshot: `output/playwright/agent-system-visual.png`.
- Важно: `Local Visual API` — сервисный модуль, не Agent 7.
- Следующий шаг: решить, нужен ли быстрый MVP на текущем CDN/Babel frontend или переводить в Vite/React для нормальной разработки.

## 2026-05-17 — Chat/voice control поверх визуализации агентов

- Контекст: продукт планируется хранить на сервере, поэтому нужен интерфейс управления агентами через чат и голос, без закрытия визуальной карты.
- Решение: добавлен нижний dock `Chat / voice command center` в `frontend/agent-system-visual`, граф остаётся видимым в основной области.
- Backend:
  - создан `backend/agent_dashboard_api/agent_control.py`;
  - `server.py` получил `POST /api/agent-control/chat`, `/voice`, `/image`, `/knowledge-search`;
  - все endpoints по умолчанию dry-run, внешние вызовы выключены.
- Модели:
  - текущий режим разработки: Codex/подписка + `LLM_PROVIDER=dry_run`;
  - OpenRouter-маршруты сохранены как отложенный server mode;
  - дешевые задачи: `LLM_MODEL_DEFAULT_FREE`;
  - управление агентами: `LLM_MODEL_AGENT_CONTROL`;
  - разработка: `LLM_MODEL_DEVELOPMENT`;
  - маркетинг: `LLM_MODEL_MARKETING`;
  - база знаний: `LLM_MODEL_KNOWLEDGE`;
  - голос: `WHISPER_PROVIDER`, `WHISPER_MODEL`;
  - картинки: `IMAGE_MODEL_PROVIDER`, `IMAGE_MODEL`;
  - embeddings: `EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`.
- Документация:
  - создан `docs/agent-control-chat-voice-openrouter-plan.md`;
  - обновлены README frontend/backend и технологические карты.
- Проверка:
  - Python compile OK;
  - JSX parse через Babel syntax plugin OK;
  - health endpoint OK;
  - chat endpoint вернул `MiniMax 2.7`, `DRY_RUN_NOT_SENT`, внешние вызовы false;
  - voice endpoint вернул `DRY_RUN_NOT_TRANSCRIBED`;
  - image endpoint вернул `DRY_RUN_IMAGE_NOT_GENERATED`;
  - knowledge endpoint вернул `DRY_RUN_NOT_EMBEDDED`.
- Исправлен баг: `Поставь` больше не классифицируется как маркетинговый `пост`.
- Уточнение: пока продукт не размещён на сервере, OpenRouter не является рабочим режимом по умолчанию.
- Локальный `.env` переключён на `LLM_PROVIDER=dry_run` и `AGENT_CONTROL_LIVE_LLM=0` без чтения/вывода секретов.
- `scripts/set_env_secret.py` расширен новыми не секретными model route ключами, чтобы позже их можно было безопасно менять.
- Следующий шаг: продолжать разработку из Codex; OpenRouter/server mode включать позже отдельным решением.

## 2026-05-17 — Добавлен третий LLM-режим для показа мастеру

- Контекст: нужен временный серверный показ системы мастеру, чтобы он мог сам открыть работающий интерфейс.
- Решение: добавлен режим `LLM_RUNTIME_MODE=demo_server_free`.
- Назначение режима:
  - система разворачивается на сервере;
  - `LLM_PROVIDER=openrouter`;
  - `AGENT_CONTROL_LIVE_LLM=1`;
  - все текстовые LLM-маршруты принудительно используют одну бесплатную модель `LLM_MODEL_DEMO_FREE`;
  - дорогие production-модели не используются.
- Создан шаблон `.env.demo-server-free.example`.
- Создан документ `docs/demo-server-free-openrouter-mode.md`.
- `config/settings.py` теперь различает три режима:
  - `local_codex` — текущая разработка через Codex, backend dry-run;
  - `demo_server_free` — показ мастеру на сервере через бесплатную OpenRouter-модель;
  - `production_server_router` — финальный серверный режим с разными моделями.
- Локальный `.env` оставлен в `LLM_RUNTIME_MODE=local_codex`, `LLM_PROVIDER=dry_run`, `AGENT_CONTROL_LIVE_LLM=0`.
- Проверено без реальных API:
  - `local_codex` принудительно даёт `provider=dry_run`;
  - `demo_server_free` даёт `provider=openrouter`;
  - в `demo_server_free` `development`, `marketing`, `agent_control`, `knowledge`, `analysis`, `reply`, `content` используют одну модель `deepseek/deepseek-v4-flash:free`;
  - `production_server_router` возвращает разные модели под задачи.
- Следующий шаг: подготовить server deploy checklist для демо мастеру, но не включать OpenRouter локально.

## 2026-05-17 — Agent control chat: UX отправки сообщения

- Пользователь сообщил: написала `привет`, но ничего не заработало.
- Проверка backend:
  - `/api/health` OK;
  - `POST /api/agent-control/chat` на `привет` OK;
  - текущий режим `local_codex` возвращает `provider=dry_run`, `llm_status=DRY_RUN_NOT_SENT`.
- Вывод: API работает, но UI был недостаточно понятен: Enter в textarea не отправлял сообщение.
- Исправлено:
  - Enter отправляет сообщение;
  - Shift+Enter переносит строку;
  - если страница открыта как файл, показывается предупреждение открыть backend URL;
  - добавлена подсказка с `runtime_mode`.
- Проверено: JSX syntax OK, endpoint отвечает.

## 2026-04-28 — Fix Telethon sender auth

- Разобрана ошибка в одноразовой команде авторизации sender-сессии: лишняя закрывающая скобка после `print(...)` и опечатка `client.eisconnect()` вместо `client.disconnect()`.
- Добавлен безопасный скрипт `scripts/auth_telegram_session.py` для авторизации отдельных Telethon-сессий `monitor` и `sender`.
- Создано локальное `.venv` и установлены зависимости из `requirements.txt`.
- Проверено: синтаксис скрипта корректный, `--help` запускается.
- Осталось: заполнить `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_PHONE` в `.env`, затем запустить авторизацию sender.
- Начат шаг заполнения окружения: создан локальный `.env`, файл игнорируется git.
- Исправлен `config/settings.py`: пустые числовые переменные окружения больше не ломают запуск.
