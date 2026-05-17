# Aeza Demo Deploy

Цель: выложить dashboard demo на VPS Aeza без включения CRM, Telegram, Redis-сбора, publisher и массовых действий.

## Что уже есть

- Код лежит в GitHub: `https://github.com/kasatkur-dot/leadsystem`.
- Серверный режим описан в `docs/demo-server-free-openrouter-mode.md`.
- Автоматический deploy-скрипт: `scripts/deploy-aeza-demo.sh`.

## Быстрый деплой

На локальной машине в папке проекта:

```bash
export AEZA_SSH_TARGET="root@SERVER_IP"
export AEZA_SSH_KEY="$HOME/.ssh/aeza_vpp_leadsystem"
export AEZA_APP_PORT="8787"
export AEZA_OPENROUTER_API_KEY="..."
./scripts/deploy-aeza-demo.sh
```

Если `AEZA_OPENROUTER_API_KEY` не задан, скрипт поднимет dashboard в безопасном dry-run режиме:

```text
LLM_RUNTIME_MODE=local_codex
LLM_PROVIDER=dry_run
AGENT_CONTROL_LIVE_LLM=0
```

## Что делает скрипт

- Подключается к VPS по SSH.
- Ставит системные пакеты: `git`, `python3`, `python3-venv`, `python3-pip`, `curl`.
- Клонирует или обновляет репозиторий в `/opt/design-studio-lead-engine`.
- Создаёт `.venv` и ставит `requirements.txt`.
- Создаёт `.env`, если его ещё нет.
- Создаёт systemd service `vpp-dashboard`.
- Запускает сервис.
- Проверяет `http://127.0.0.1:8787/api/health`.

## Что скрипт не делает

- Не включает Bitrix24.
- Не отправляет Telegram/MAX/VK сообщения.
- Не запускает Redis-сбор, scheduler, publisher.
- Не публикует контент.
- Не пишет реальные ключи в Git.
- Не настраивает nginx/домен/HTTPS. Это отдельный следующий шаг.

## После деплоя

Открыть:

```text
http://SERVER_IP:8787/
```

Проверить:

```text
http://SERVER_IP:8787/api/health
http://SERVER_IP:8787/data.js
```

Если нужен доступ через домен и HTTPS, следующим шагом добавить nginx reverse proxy и сертификат.
