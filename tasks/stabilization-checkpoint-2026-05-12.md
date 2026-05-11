# Stabilization Checkpoint - 2026-05-12

Проект: `design-studio-lead-engine`

Статус: финальная сверка перед любым сохранением/commit/publish/deploy.

Важно: этот checkpoint не является разрешением на публикацию, commit или deploy. Он фиксирует, какие блоки уже проверены, какие требуют дополнительной проверки и какие файлы нельзя трогать.

## Что проверено

### 1. Site

Статус: готов к сохранению как проверенный локальный блок после финального просмотра.

Что уже стабилизировано:

- локальные визуалы вместо внешних Unsplash-картинок;
- исправлены мобильные и desktop-переносы hero-заголовка;
- удалён лишний preload, который создавал browser warning;
- пересобран `site/assets/app.bundle.js`;
- проверены локальные ссылки, JS-синтаксис, базовые security/a11y-паттерны;
- скриншоты и output-артефакты теперь игнорируются через `.gitignore`.

Что ещё проверить перед публичной публикацией:

- ручной просмотр сайта в реальном браузере на desktop/mobile;
- финальные security headers на хостинге;
- решение по static/prerender или production-сборке;
- формы/CRM/Bitrix24 подключать только отдельным подтверждением.

### 2. Agents / Backend

Статус: кодовый блок технически проверен, но требует сохранения по частям.

Что уже стабилизировано:

- весь Python backend компилируется в проектной `.venv` Python 3.9;
- checker/dashboard/dry-run scripts проходят безопасно без внешних вызовов;
- Agent 4 Publisher проверен в dry-run: `generate post`, `generate image`, `publish max --dry-run`;
- Agent 5 payload dry-run проходит без внешних вызовов;
- Agent 5 `stats_reporter` теперь является compatibility-wrapper на рабочий `analytics_reporter`;
- `datetime.UTC` заменён на `timezone.utc` для совместимости с Python 3.9.

Что требует проверки перед сохранением:

- backend-изменений много, поэтому сохранять лучше блоками;
- отдельно проверить Agent 4 publish adapters перед реальной публикацией;
- отдельно проверить Agent 6/outreach перед любыми внешними сообщениями;
- реальные API/CRM/Telegram/Bitrix24/LLM вызовы не запускать без подтверждения.

### 3. Docs / Research

Статус: готово как навигационная и исследовательская база.

Что уже стабилизировано:

- добавлены `docs/README.md` и `research/README.md`;
- точных дублей по SHA среди `docs/`, `research/`, `tasks/` не найдено;
- явных секретов-значений не найдено;
- зафиксирован порядок чтения: `REPORT.md` -> `tasks/roadmap.md` -> профильный `docs/`/`research/` -> старый `tasks/tasks.md`.

Ограничение:

- часть документов остаётся рабочими draft/audit/plan-материалами, их нельзя считать финальным ТЗ без сверки с `REPORT.md`.

### 4. Content

Статус: готово как контентная база, без автопубликации.

Что уже стабилизировано:

- добавлен `content/README.md`;
- точных дублей по SHA внутри `content` не найдено;
- явных секретов-значений не найдено;
- `content/pipeline/published-log.md` зафиксирован как единственный источник правды о публикациях;
- подтверждено, что название `draft-*` не равно статусу "не опубликовано".

Что требует контроля:

- любые публикации в MAX/TG/VK/другие каналы только после отдельного согласования;
- клиентские данные и реальные кейсы перед публикацией проверять на чувствительность.

### 5. Dashboard / Reports

Статус: готово как read-only dashboard и отчетный слой.

Что уже стабилизировано:

- добавлены `data/README.md` и `data/reports/README.md`;
- пересобраны `data/reports/agent_dashboard.json`, `.md`, `.html`;
- dashboard status `OK`, 6 агентов, 12 событий;
- внешние вызовы при сборке dashboard выключены;
- явных секретов-значений не найдено.

Что нельзя трогать:

- `data/*.session`;
- `logs/`;
- любые runtime/session файлы.

### 6. Config / Security

Статус: базовая защита приведена в порядок.

Что уже стабилизировано:

- `.env`, session-файлы, logs, credentials/tokens игнорируются;
- `.playwright-cli/` и `output/` добавлены в `.gitignore`, чтобы не сохранять generated browser profiles, screenshots и временные визуальные артефакты;
- полезные безопасные файлы `docs/secret-handling-policy.md` и `scripts/set_env_secret.py` не скрываются широким правилом `*secret*`.

Что нельзя сохранять или публиковать:

- `.env`;
- `.venv`;
- `.claude/settings.local.json`;
- `.playwright-cli/`;
- `.playwright-mcp/`;
- `data/*.session`;
- `logs/`;
- `output/`;
- `__pycache__/`;
- `agents/agent4_publisher/output/`;
- любые реальные токены, ключи, cookie, webhooks, credentials.

## Что готово к сохранению

Рекомендуемый порядок сохранения, если будем делать commit/checkpoint:

1. Safety/navigation: `.gitignore`, `REPORT.md`, `AGENTS.md`, `CLAUDE.md`, README-файлы, policy-файлы.
2. Site: `site/` и связанные документы сайта.
3. Docs/research/content: `docs/`, `research/`, `content/` после быстрой проверки чувствительных данных.
4. Dashboard/reports: `data/reports/`, dashboard scripts, README-файлы.
5. Backend core: `shared/`, `config/`, `orchestrator/`, Agent 1/2/3/5.
6. Agent 4 Publisher отдельно.
7. Agent 6 Outreach отдельно.

## Что требует дополнительной проверки

- `MCP_SETUP_RESULT.md` - понять, это отчет по настройке или временный файл.
- `OPEN_SITE.command` - проверить, безопасен ли для сохранения и не содержит локальных секретов.
- `.env.example` - проверить, что содержит только placeholders.
- `ТЗ_СЛИЯНИЕ_КОНТЕНТ_ДВИЖКА.md` - решить, это актуальное ТЗ или рабочий черновик.
- `tasks/session-notes.md` - перед сохранением проверить, что там нет секретов или лишних личных данных.
- `data/reports/bitrix_close_test_lead_*` - проверено: секретов и контактов не найдено, но это operational CRM test artifacts с реальными Bitrix lead ID и следами фактического тестового обновления лида. Оставить локально, не коммитить и не публиковать.

## Что нельзя трогать

Не удалять, не переносить, не коммитить и не публиковать:

- оригиналы клиентских/входящих материалов без отдельного разрешения;
- runtime/session/cache/log/output артефакты;
- секреты и локальные настройки;
- сгенерированные browser profiles и screenshots;
- рабочие `.venv` и зависимости.

## Проверки, которые уже проходили

```bash
.venv/bin/python -m py_compile $(find agents orchestrator shared config scripts -type f -name '*.py' | sort)
.venv/bin/python scripts/check_agent_okr_contract.py
.venv/bin/python scripts/build_agent_dashboard.py
.venv/bin/python scripts/build_agent_dashboard_markdown.py
.venv/bin/python scripts/build_agent_dashboard_viewer.py
.venv/bin/python scripts/dry_run_synthetic_lead.py
.venv/bin/python scripts/dry_run_agent5_payload.py
```

Agent 4 проверялся только в безопасном dry-run режиме. Реальная публикация не запускалась.

## Следующий маленький шаг

Перед любым commit/deploy сделать один короткий audit untracked root-файлов:

- `.env.example`;
- `MCP_SETUP_RESULT.md`;
- `OPEN_SITE.command`;
- `ТЗ_СЛИЯНИЕ_КОНТЕНТ_ДВИЖКА.md`;
- `tasks/session-notes.md`;
- `data/reports/bitrix_close_test_lead_*`.

После этого можно сохранять изменения партиями, начиная с safety/navigation блока.
