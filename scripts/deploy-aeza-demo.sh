#!/usr/bin/env bash
# Deploy the dashboard demo to an Aeza/VPS server over SSH.
# Required local env:
#   AEZA_SSH_TARGET=root@SERVER_IP
# Optional:
#   AEZA_PROJECT_DIR=/opt/design-studio-lead-engine
#   AEZA_APP_PORT=8787
#   AEZA_OPENROUTER_API_KEY=...  # if omitted, server runs dry-run dashboard mode
set -euo pipefail

if [ -z "${AEZA_SSH_TARGET:-}" ]; then
  echo "ERROR: set AEZA_SSH_TARGET, example: root@203.0.113.10"
  exit 1
fi

PROJECT_DIR="${AEZA_PROJECT_DIR:-/opt/design-studio-lead-engine}"
APP_PORT="${AEZA_APP_PORT:-8787}"
GIT_REPO="${AEZA_GIT_REPO:-https://github.com/kasatkur-dot/leadsystem.git}"
OPENROUTER_STATUS="EMPTY"
if [ -n "${AEZA_OPENROUTER_API_KEY:-}" ]; then
  OPENROUTER_STATUS="SET"
fi

echo "Deploy target: ${AEZA_SSH_TARGET}"
echo "Project dir: ${PROJECT_DIR}"
echo "App port: ${APP_PORT}"
echo "OPENROUTER_API_KEY: ${OPENROUTER_STATUS}"

ssh "$AEZA_SSH_TARGET" \
  "PROJECT_DIR='$PROJECT_DIR' APP_PORT='$APP_PORT' GIT_REPO='$GIT_REPO' OPENROUTER_STATUS='$OPENROUTER_STATUS' bash -s" <<'REMOTE'
set -euo pipefail

echo "== Installing base packages =="
if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y git python3 python3-venv python3-pip curl
else
  echo "ERROR: this deploy script expects Debian/Ubuntu with apt-get."
  exit 1
fi

echo "== Syncing repository =="
sudo mkdir -p "$PROJECT_DIR"
sudo chown -R "$USER":"$USER" "$PROJECT_DIR"
if [ -d "$PROJECT_DIR/.git" ]; then
  cd "$PROJECT_DIR"
  git fetch origin main
  git reset --hard origin/main
else
  rm -rf "$PROJECT_DIR"
  git clone "$GIT_REPO" "$PROJECT_DIR"
  cd "$PROJECT_DIR"
fi

echo "== Installing Python dependencies =="
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

echo "== Preparing .env =="
if [ ! -f .env ]; then
  if [ "$OPENROUTER_STATUS" = "SET" ]; then
    cp .env.demo-server-free.example .env
    sed -i "s/^OPENROUTER_API_KEY=.*/OPENROUTER_API_KEY=__OPENROUTER_KEY_PLACEHOLDER__/" .env
  else
    cat > .env <<ENV
LLM_RUNTIME_MODE=local_codex
LLM_PROVIDER=dry_run
AGENT_CONTROL_LIVE_LLM=0
HOST=0.0.0.0
PORT=${APP_PORT}
APP_ENV=debug
WHISPER_PROVIDER=dry_run
IMAGE_MODEL_PROVIDER=dry_run
EMBEDDING_PROVIDER=dry_run
ENV
  fi
else
  echo ".env exists, keeping existing server secrets/settings."
fi

chmod +x scripts/start-server.sh

echo "== Installing systemd service =="
sudo tee /etc/systemd/system/vpp-dashboard.service >/dev/null <<UNIT
[Unit]
Description=VPP Lead Engine Dashboard Demo
After=network.target

[Service]
Type=simple
WorkingDirectory=${PROJECT_DIR}
ExecStart=${PROJECT_DIR}/scripts/start-server.sh
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable vpp-dashboard
REMOTE

if [ -n "${AEZA_OPENROUTER_API_KEY:-}" ]; then
  printf '%s' "$AEZA_OPENROUTER_API_KEY" | ssh "$AEZA_SSH_TARGET" \
    "PROJECT_DIR='$PROJECT_DIR' python3 - <<'PY'
from pathlib import Path
import os
import sys

project_dir = Path(os.environ['PROJECT_DIR'])
env_path = project_dir / '.env'
key = sys.stdin.read()
text = env_path.read_text(encoding='utf-8')
if '__OPENROUTER_KEY_PLACEHOLDER__' in text:
    text = text.replace('__OPENROUTER_KEY_PLACEHOLDER__', key)
elif 'OPENROUTER_API_KEY=' in text:
    lines = []
    for line in text.splitlines():
        if line.startswith('OPENROUTER_API_KEY='):
            lines.append('OPENROUTER_API_KEY=' + key)
        else:
            lines.append(line)
    text = '\n'.join(lines) + '\n'
else:
    text = text.rstrip() + '\nOPENROUTER_API_KEY=' + key + '\n'
env_path.write_text(text, encoding='utf-8')
print('OPENROUTER_API_KEY=SET')
PY"
fi

ssh "$AEZA_SSH_TARGET" \
  "APP_PORT='$APP_PORT' bash -s" <<'REMOTE'
set -euo pipefail
echo "== Starting service =="
sudo systemctl restart vpp-dashboard
sleep 2
sudo systemctl --no-pager --full status vpp-dashboard || true

echo "== Health check =="
curl -fsS "http://127.0.0.1:${APP_PORT}/api/health"
echo
REMOTE

echo "Deploy finished. Open: http://$(echo "$AEZA_SSH_TARGET" | sed 's/.*@//'):${APP_PORT}/"
