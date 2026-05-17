---
paths:
  - ".env.example"
  - ".gitignore"
  - "docs/secret-handling-policy.md"
  - "docs/env-fill-checklist.md"
  - "docs/mcp-api-docs-preflight.md"
  - "scripts/set_env_secret.py"
  - "config/**"
---

# Security Rules

Перед работой с секретами, интеграциями и настройками читать:

- `REPORT.md`;
- `agents/Агент безопастности/AGENT_SECURITY.md`;
- `docs/secret-handling-policy.md`;
- `docs/env-fill-checklist.md`;
- `.env.example`.

`agents/Агент безопастности/AGENT_SECURITY.md` — главный файл управления безопасностью. Это не Agent 7, а общий контрольный слой для всех 6 агентов, checker/dashboard и будущих MCP/API-интеграций.

Правила:

- реальные токены, cookies, session strings, credentials и webhook secrets не выводить в ответах и не писать в проектные документы;
- сохранять секреты только локально в `.env`, gitignored `secrets/` или безопасное локальное хранилище;
- перед commit/push/deploy проверять `.gitignore` и отсутствие секретов в индексе;
- если секрет попал в публичный источник, предупреждать о перевыпуске;
- внешние MCP/API/CRM подключения включать только после явного подтверждения пользователя.

Красные линии из `AGENT_SECURITY.md`:

- деньги, подписки, лимиты и платные API — только после явного подтверждения;
- продакшен, деплой, массовые действия и реальные публикации — только после подтверждения;
- секреты, токены, cookies, session-файлы, PII и CRM-данные — не показывать и не отправлять наружу;
- новые MCP, внешняя телеметрия, скрытые интеграции и фоновые действия — только через preflight и approval.

Зелёный коридор:

- читать и править обычные файлы проекта;
- запускать локальные тесты, форматтеры, сборку и dry-run;
- поднимать локальный dev-server без внешних отправок;
- использовать синтетические или обезличенные данные.

AI-риски, которые проверять: prompt injection, lethal trifecta, SSRF, slopsquatting, markdown/image exfiltration, неструктурированный LLM output и небезопасные MCP-инструменты.
