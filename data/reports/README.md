# Reports Navigation

Эта папка хранит локальные отчёты и dashboard-снимки проекта.

## Главные файлы

- `agent_dashboard.json` — основной машинный снимок состояния 6 агентов.
- `agent_dashboard.md` — read-only Markdown-снимок для человека.
- `agent_dashboard.html` — локальная read-only HTML-панель.
- `channel_report_mvp.csv` — MVP-отчёт по каналам: расходы, лиды, сделки, ROMI и решение по каналу.
- `agent_okr_contract_check.json` — проверка соответствия агентной модели OKR/контрактам.

## Тестовые отчёты

Файлы `agent3_*`, `agent5_*`, `bitrix_close_test_lead_*`, `synthetic_lead_dry_run.json` — это локальные следы тестов. Их можно читать для диагностики, но нельзя считать реальной клиентской базой.

Отчёты `bitrix_close_test_lead_*` относятся к operational CRM test artifacts: они могут содержать реальные Bitrix lead ID и следы фактического тестового обновления лида. Такие файлы должны оставаться локально и не попадать в Git/публикацию.

## Безопасность

- Не хранить здесь реальные токены, webhook URL, пароли, cookie, закрытые переписки и персональные данные клиентов.
- Если в отчёте есть поле про ключ или webhook, там должен быть только статус, например `found/missing/hidden`, но не само значение.
- Runtime-файлы `*.session`, логи и `.env` не относятся к отчётам и не должны попадать в Git.

## Как пересобрать dashboard безопасно

```bash
python3 scripts/build_agent_dashboard.py
python3 scripts/build_agent_dashboard_markdown.py
python3 scripts/build_agent_dashboard_viewer.py
```

Эти скрипты должны работать read-only по внешним системам: без Redis, Bitrix24, Telegram, IMAP, LLM, scheduler, publisher и платных API.
