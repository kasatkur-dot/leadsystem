#!/bin/zsh

set -u

SCRIPT_DIR="${0:A:h}"
cd -- "$SCRIPT_DIR"

HOST="127.0.0.1"
PORT="${1:-4173}"
START_PORT="$PORT"
MAX_PORT=$((START_PORT + 20))
SERVER_PID=""
INDEX_FILE="${SCRIPT_DIR}/index.html"

pause_before_exit() {
  echo ""
  read -r "?Нажмите Enter, чтобы закрыть окно..."
}

open_target() {
  local target="$1"

  if open "$target" >/dev/null 2>&1; then
    return 0
  fi

  open -a "Safari" "$target" >/dev/null 2>&1 && return 0
  open -a "Google Chrome" "$target" >/dev/null 2>&1 && return 0
  open -a "Yandex" "$target" >/dev/null 2>&1 && return 0

  if [[ "$target" == http://* || "$target" == https://* ]]; then
    if command -v osascript >/dev/null 2>&1; then
      osascript -e "open location \"$target\"" >/dev/null 2>&1 && return 0
    fi
  else
    if command -v osascript >/dev/null 2>&1; then
      osascript -e "tell application \"Finder\" to open POSIX file \"$target\"" >/dev/null 2>&1 && return 0
    fi
  fi

  return 1
}

open_file_fallback() {
  echo "Открываю сайт напрямую как файл."
  if open_target "$INDEX_FILE"; then
    echo "Сайт открыт через файл: $INDEX_FILE"
    pause_before_exit
    exit 0
  fi

  echo "Не получилось открыть браузер автоматически."
  echo "Откройте файл вручную:"
  echo "$INDEX_FILE"
  pause_before_exit
  exit 1
}

cleanup() {
  if [ -n "$SERVER_PID" ]; then
    kill "$SERVER_PID" >/dev/null 2>&1 || true
  fi
}
trap cleanup INT TERM EXIT

if [ ! -f "$INDEX_FILE" ]; then
  echo "Не найден файл сайта:"
  echo "$INDEX_FILE"
  pause_before_exit
  exit 1
fi

echo "Запускаю сайт Вектор Плюс-Про..."

if ! command -v python3 >/dev/null 2>&1; then
  echo "Не найден python3, поэтому сервер не запускаю."
  open_file_fallback
fi

while [ "$PORT" -le "$MAX_PORT" ]; do
  URL="http://${HOST}:${PORT}/"

  if curl -fsS "$URL" >/dev/null 2>&1; then
    echo "Сервер уже работает."
    echo "Адрес: $URL"
    if open_target "$URL"; then
      echo "Сайт открыт."
      pause_before_exit
      exit 0
    fi
    echo "Не получилось открыть браузер автоматически."
    echo "Откройте адрес вручную: $URL"
    pause_before_exit
    exit 1
  fi

  if ! lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    break
  fi

  PORT=$((PORT + 1))
done

if [ "$PORT" -gt "$MAX_PORT" ]; then
  echo "Не нашел свободный порт рядом с $START_PORT."
  open_file_fallback
fi

URL="http://${HOST}:${PORT}/"
LOG_FILE="/tmp/vector-plus-pro-site-${PORT}.log"

echo "Адрес: $URL"
echo ""

python3 -m http.server --bind "$HOST" "$PORT" >"$LOG_FILE" 2>&1 &
SERVER_PID=$!

for _ in {1..50}; do
  if curl -fsS "$URL" >/dev/null 2>&1; then
    break
  fi

  if ! kill -0 "$SERVER_PID" >/dev/null 2>&1; then
    break
  fi

  sleep 0.1
done

if curl -fsS "$URL" >/dev/null 2>&1; then
  if open_target "$URL"; then
    echo "Сайт открыт. Чтобы остановить сервер, нажмите Control + C."
    wait "$SERVER_PID"
    exit 0
  fi

  echo "Сервер работает, но браузер не открылся автоматически."
  echo "Откройте адрес вручную: $URL"
  wait "$SERVER_PID"
  exit 0
fi

echo "Сервер не ответил."
echo "Лог: $LOG_FILE"
cat "$LOG_FILE" 2>/dev/null || true
open_file_fallback
