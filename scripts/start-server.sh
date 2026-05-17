#!/usr/bin/env bash
# Start the dashboard server. Copy .env.demo-server-free.example → .env and fill OPENROUTER_API_KEY before running.
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

if [ ! -f ".env" ]; then
  echo "ERROR: .env not found. Copy .env.demo-server-free.example → .env and fill OPENROUTER_API_KEY."
  exit 1
fi

export $(grep -v '^#' .env | grep -v '^$' | xargs)

if [ ! -f "data/reports/agent_dashboard.json" ]; then
  echo "Building agent dashboard data..."
  python3 scripts/build_agent_dashboard.py
fi

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8787}"

echo "Starting dashboard on http://${HOST}:${PORT}/"
python3 -m backend.agent_dashboard_api.server --host "$HOST" --port "$PORT"
