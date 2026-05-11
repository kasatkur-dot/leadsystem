# Final Stabilization Checkpoint — 2026-05-12

> Статус: более ранний checkpoint. Актуальная сводка после дополнительной проверки security/config и Bitrix artifacts находится в `tasks/stabilization-checkpoint-2026-05-12.md`. Этот файл оставлен как историческая запись и не должен быть главным источником решений.

Статус: перед сохранением / коммитом / публикацией.

Коммит, push, deploy и реальные интеграции не выполнялись.

## Что уже проверено

### 1. Site

Готово к сохранению после финального человеческого просмотра:

- `site/`
- локальные изображения `site/assets/images/*.webp`
- `site/assets/app.bundle.js`
- `site/README.md`
- `site/DESIGN.md`

Проверено:

- `node --check site/assets/app.bundle.js`
- `node --check site/tools/build-bundle.mjs`
- локальные ссылки сайта без пропусков;
- первый экран desktop/mobile через локальный preview;
- hero-заголовок больше не режется через дефис и не уходит в соседний блок.

Требует внимания перед публичным deploy:

- реальный просмотр в браузере на desktop/mobile;
- решение: нужна ли static/prerender-сборка для SEO;
- security headers уже на стороне хостинга;
- не подключать формы/CRM/Bitrix24 без отдельного подтверждения.

### 2. Docs / Research

Готово к сохранению как методологическая база:

- `docs/`
- `research/`
- `docs/README.md`
- `research/README.md`

Проверено:

- точных дублей по SHA нет;
- явных секретов по value-паттернам нет;
- добавлена навигация и приоритет чтения.

Правило при конфликте:

```text
REPORT.md -> tasks/roadmap.md -> профильный docs/research -> старый tasks/tasks.md
```

Ограничение:

- часть файлов остаётся `draft/audit/plan`, не считать их финальным ТЗ без сверки с `REPORT.md`.

### 3. Content

Готово к сохранению как контентная база:

- `content/README.md`
- `content/library/`
- `content/pipeline/`
- `content/strategy/`
- `content/studio_brand/`
- `content/site/`
- `content/bot_spec/`

Проверено:

- точных дублей по SHA нет;
- явных секретов по value-паттернам нет;
- `pipeline/published-log.md` — единственный источник правды о публикациях.

Важно:

- название `draft-*` не означает, что пост не опубликован;
- уже опубликованы минимум `draft-002` и `draft-019` в MAX;
- автопубликация, PostMyPost, CRM-интеграции и внешние рассылки не запускаются без отдельного подтверждения.

### 4. Dashboard / Reports

Готово к сохранению как read-only management layer:

- `data/README.md`
- `data/reports/README.md`
- `data/reports/agent_dashboard.json`
- `data/reports/agent_dashboard.md`
- `data/reports/agent_dashboard.html`
- `data/reports/channel_report_mvp.csv`
- dashboard build scripts.

Проверено:

```text
dashboard_build_status=OK
overall_status=OK
agents_count=6
event_count=12
redis=False
bitrix24=False
telegram_send=False
imap=False
llm=False
scheduler=False
publisher=False
```

Важный продуктовый хвост:

- добавить в Agent 5 слой статуса персонального КП/лендинга;
- добавить будущую метрику `CR visit->deal`;
- подготовить поля `visit_count` / `visitor_id`.

### 5. Agents / Backend

Готово к сохранению только после группировки по подблокам:

- `shared/`
- `config/`
- `orchestrator/`
- `agents/agent1_scout/`
- `agents/agent2_collector/`
- `agents/agent3_processor/`
- `agents/agent4_publisher/`
- `agents/agent5_crm/`
- `agents/agent6_outreach/`
- `scripts/`
- `requirements.txt`

Проверено:

- весь Python backend компилируется в проектной `.venv` Python 3.9;
- checker/dashboard scripts работают и в `.venv`, и в системном `python3`;
- `scripts/check_agent_okr_contract.py` возвращает `agent_contract_status=OK`;
- `scripts/dry_run_synthetic_lead.py` возвращает `raw_lead_status=OK`, `qualified_lead_status=OK`;
- `scripts/dry_run_agent5_payload.py` возвращает `bitrix_payload_status=OK`, `telegram_payload_status=OK`;
- Agent 4 Publisher dry-run работает: `generate post`, `generate image`, `publish max --dry-run`;
- `stats_reporter` больше не пустой, он прокидывает вызовы в `analytics_reporter`.

Риск:

- backend-изменений много. Перед коммитом сохранять не одним большим комом, а логическими группами.

## Что нельзя трогать / сохранять

Не коммитить и не переносить:

- `.env`
- `secrets/`
- `credentials/`
- `data/*.session`
- `logs/`
- `.venv/`
- `.playwright-cli/`
- `.playwright-mcp/`
- `output/`
- `agents/agent4_publisher/output/`
- любые реальные токены, webhook, cookie, закрытые переписки, персональные данные клиентов.

Эти пути сейчас защищены `.gitignore`.

## Рекомендуемый порядок сохранения

Если будем делать коммиты, лучше не один общий, а по группам:

1. `security/project-rules`
   - `.gitignore`
   - `AGENTS.md`
   - `CLAUDE.md`
   - `REPORT.md`
   - `.env.example`

2. `site/public-package`
   - `site/`
   - связанные `docs/site-*`
   - `content/site/`

3. `docs-research-content`
   - `docs/`
   - `research/`
   - `content/`
   - `tasks/*` без runtime.

4. `dashboard-reports`
   - `data/README.md`
   - `data/reports/README.md`
   - dashboard reports;
   - dashboard scripts.

5. `agents-backend`
   - `agents/`
   - `shared/`
   - `config/`
   - `orchestrator/`
   - backend scripts;
   - `requirements.txt`.

## Проверки перед любым commit

Запустить из корня проекта:

```bash
.venv/bin/python -m py_compile $(find agents orchestrator shared config scripts -type f -name '*.py' | sort)
.venv/bin/python scripts/check_agent_okr_contract.py
.venv/bin/python scripts/build_agent_dashboard.py
.venv/bin/python scripts/build_agent_dashboard_markdown.py
.venv/bin/python scripts/build_agent_dashboard_viewer.py
.venv/bin/python scripts/dry_run_synthetic_lead.py
.venv/bin/python scripts/dry_run_agent5_payload.py
node --check site/assets/app.bundle.js
node --check site/tools/build-bundle.mjs
```

Проверить перед сохранением:

```bash
git status --short
git status --ignored --short
```

Если в `git status --short` появились `.env`, `*.session`, `logs/`, `.venv/`, `.playwright-*`, `output/` — остановиться и исправить `.gitignore`.

## Следующий маленький шаг

Перед коммитом или публикацией выбрать режим:

1. `только сохранить checkpoint без коммита`;
2. `подготовить первый логический commit security/project-rules`;
3. `продолжить продуктовый хвост Agent 5: персональное КП/лендинг + CR visit->deal`.
