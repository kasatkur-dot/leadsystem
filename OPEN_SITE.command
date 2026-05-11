#!/bin/zsh

SCRIPT_DIR="${0:A:h}"
SITE_LAUNCHER="${SCRIPT_DIR}/site/open-site.command"

if [ ! -x "$SITE_LAUNCHER" ]; then
  chmod +x "$SITE_LAUNCHER" >/dev/null 2>&1 || true
fi

exec "$SITE_LAUNCHER"
