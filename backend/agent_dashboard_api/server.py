"""Local read-only server for the multi-agent visual dashboard.

This server does not start Redis, Bitrix24, Telegram, LLM, scheduler or any
paid service. It only serves static frontend files and reads local reports.
"""

from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

try:
    from .agent_control import (
        build_model_manifest,
        handle_chat,
        handle_image,
        handle_knowledge_search,
        handle_voice,
    )
    from .dashboard_data_builder import (
        DASHBOARD_PATH,
        PROJECT_ROOT,
        build_agent_system_data,
        build_runtime_js,
        load_dashboard,
    )
except ImportError:  # Allows running as: python backend/agent_dashboard_api/server.py
    from agent_control import (  # type: ignore
        build_model_manifest,
        handle_chat,
        handle_image,
        handle_knowledge_search,
        handle_voice,
    )
    from dashboard_data_builder import (  # type: ignore
        DASHBOARD_PATH,
        PROJECT_ROOT,
        build_agent_system_data,
        build_runtime_js,
        load_dashboard,
    )


FRONTEND_DIR = PROJECT_ROOT / "frontend" / "agent-system-visual"


class DashboardHandler(SimpleHTTPRequestHandler):
    server_version = "AgentDashboardHTTP/0.1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler name
        path = urlparse(self.path).path
        if path in ("/api/health", "/health"):
            return self._send_json(
                {
                    "status": "OK",
                    "frontend_dir": str(FRONTEND_DIR),
                    "dashboard_report": str(DASHBOARD_PATH),
                    "external_calls": {
                        "redis": False,
                        "bitrix24": False,
                        "telegram_send": False,
                        "imap": False,
                        "llm": False,
                        "scheduler": False,
                        "publisher": False,
                    },
                    "agent_control": {
                        "api": True,
                        "live_llm_enabled": build_model_manifest().get("live_llm_enabled", False),
                    },
                }
            )
        if path == "/api/dashboard":
            return self._send_json(load_dashboard())
        if path == "/api/agent-system-data":
            return self._send_json(build_agent_system_data(load_dashboard()))
        if path == "/data.js":
            return self._send_js(build_runtime_js(load_dashboard()))
        if path == "/favicon.ico":
            self.send_response(HTTPStatus.NO_CONTENT)
            self.end_headers()
            return
        if path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler name
        path = urlparse(self.path).path
        if path == "/api/agent-control/chat":
            return self._send_json(handle_chat(self._read_json_body(), load_dashboard()))
        if path == "/api/agent-control/voice":
            content_length = int(self.headers.get("Content-Length", "0") or 0)
            content_type = self.headers.get("Content-Type", "")
            if content_length:
                self.rfile.read(content_length)
            return self._send_json(handle_voice(content_type, content_length))
        if path == "/api/agent-control/image":
            return self._send_json(handle_image(self._read_json_body()))
        if path == "/api/agent-control/knowledge-search":
            return self._send_json(handle_knowledge_search(self._read_json_body()))
        return self._send_json(
            {"status": "ERROR", "error": f"Unknown POST endpoint: {path}"},
            status=HTTPStatus.NOT_FOUND,
        )

    def do_OPTIONS(self) -> None:  # noqa: N802 - stdlib handler name
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_js(self, body_text: str) -> None:
        body = body_text.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/javascript; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict:
        content_length = int(self.headers.get("Content-Length", "0") or 0)
        if content_length <= 0:
            return {}
        raw = self.rfile.read(content_length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}
        return payload if isinstance(payload, dict) else {}

    def log_message(self, format: str, *args) -> None:  # noqa: A002 - stdlib signature
        print(f"[agent-dashboard-api] {self.address_string()} - {format % args}")


def main() -> None:
    import os
    parser = argparse.ArgumentParser(description="Run local multi-agent visual dashboard API.")
    # Default to 0.0.0.0 on server (HOST env var), 127.0.0.1 locally
    default_host = os.environ.get("HOST", "0.0.0.0" if os.environ.get("LLM_RUNTIME_MODE") == "demo_server_free" else "127.0.0.1")
    parser.add_argument("--host", default=default_host)
    parser.add_argument("--port", default=int(os.environ.get("PORT", 8787)), type=int)
    args = parser.parse_args()

    if not FRONTEND_DIR.exists():
        raise SystemExit(f"Frontend directory not found: {FRONTEND_DIR}")
    if not DASHBOARD_PATH.exists():
        raise SystemExit(f"Dashboard report not found: {DASHBOARD_PATH}")

    server = ThreadingHTTPServer((args.host, args.port), DashboardHandler)
    print(f"Serving multi-agent visual dashboard at http://{args.host}:{args.port}/")
    print(f"Frontend: {FRONTEND_DIR}")
    print(f"Dashboard source: {DASHBOARD_PATH}")
    print("Safe local mode: no Redis, Bitrix24, Telegram, IMAP, scheduler or publisher calls.")
    print("Agent-control endpoints are dry-run unless AGENT_CONTROL_LIVE_LLM=1.")
    server.serve_forever()


if __name__ == "__main__":
    main()
