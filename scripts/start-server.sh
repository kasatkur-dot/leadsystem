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

if [ ! -f "data/reports/agent_dashboard.json" ]; then
  echo "Building agent dashboard data..."
  "$PYTHON_BIN" scripts/build_agent_dashboard.py
fi

echo "Starting dashboard. Host and port are read by the Python server from environment/.env."
"$PYTHON_BIN" -m backend.agent_dashboard_api.server
