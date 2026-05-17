#!/usr/bin/env bash
# Start the dashboard server. Copy .env.demo-server-free.example to .env and fill OPENROUTER_API_KEY before running.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_BIN="$PROJECT_ROOT/.venv/bin/python"

cd "$PROJECT_ROOT"

if [ ! -f ".env" ]; then
  echo "ERROR: .env not found. Copy .env.demo-server-free.example to .env and fill OPENROUTER_API_KEY."
  exit 1
fi

if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="python3"
fi

"$PYTHON_BIN" - <<'PY'
from pathlib import Path

env_path = Path(".env")
values = {}
for raw_line in env_path.read_text(encoding="utf-8").splitlines():
    line = raw_line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    key, value = line.split("=", 1)
    values[key.strip()] = value.strip().strip('"').strip("'")

runtime_mode = values.get("LLM_RUNTIME_MODE", "")
openrouter_status = "SET" if values.get("OPENROUTER_API_KEY") else "EMPTY"
print(f"LLM_RUNTIME_MODE={runtime_mode or 'EMPTY'}")
print(f"OPENROUTER_API_KEY={openrouter_status}")

if runtime_mode == "demo_server_free" and openrouter_status != "SET":
    raise SystemExit("ERROR: demo_server_free requires OPENROUTER_API_KEY=SET in .env")
PY

read_env_value() {
  local key="$1"
  "$PYTHON_BIN" - "$key" <<'PY'
from pathlib import Path
import sys

target = sys.argv[1]
env_path = Path(".env")
for raw_line in env_path.read_text(encoding="utf-8").splitlines():
    line = raw_line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    key, value = line.split("=", 1)
    if key.strip() == target:
        print(value.strip().strip('"').strip("'"))
        break
PY
}

RUNTIME_MODE="$(read_env_value LLM_RUNTIME_MODE)"
HOST_VALUE="$(read_env_value HOST)"
PORT_VALUE="$(read_env_value PORT)"
if [ -z "$HOST_VALUE" ]; then
  if [ "$RUNTIME_MODE" = "demo_server_free" ]; then
    HOST_VALUE="0.0.0.0"
  else
    HOST_VALUE="127.0.0.1"
  fi
fi
if [ -z "$PORT_VALUE" ]; then
  PORT_VALUE="8787"
fi

if [ ! -f "data/reports/agent_dashboard.json" ]; then
  echo "Building agent dashboard data..."
  "$PYTHON_BIN" scripts/build_agent_dashboard.py
fi

echo "Starting dashboard on ${HOST_VALUE}:${PORT_VALUE}."
"$PYTHON_BIN" -m backend.agent_dashboard_api.server --host "$HOST_VALUE" --port "$PORT_VALUE"
