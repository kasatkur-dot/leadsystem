"""Small LLM router used by lead agents.

Local development is currently driven from Codex/subscription, so the product
backend should stay in `dry_run` unless `.env` explicitly enables a provider.
OpenRouter model routes are preserved for the later server deployment mode.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from config import settings


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class LLMConfigError(RuntimeError):
    """Raised when the selected LLM provider is not configured."""


def _content_to_text(content: object) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        chunks: list[str] = []
        for part in content:
            if isinstance(part, str):
                chunks.append(part)
            elif isinstance(part, dict):
                value = part.get("text") or part.get("content")
                if isinstance(value, str):
                    chunks.append(value)
        return "\n".join(chunk for chunk in chunks if chunk).strip()
    return ""


def _model_for(task: str) -> str:
    if task in {"agent_control", "orchestrator", "task_management", "manager"}:
        return settings.LLM_MODEL_AGENT_CONTROL
    if task in {"development", "coding", "architecture", "debug"}:
        return settings.LLM_MODEL_DEVELOPMENT
    if task in {"marketing", "content", "copywriting", "publisher"}:
        return settings.LLM_MODEL_MARKETING
    if task in {"knowledge", "kb_search", "retrieval"}:
        return settings.LLM_MODEL_KNOWLEDGE
    if task in {"default_free", "cheap", "free"}:
        return settings.LLM_MODEL_DEFAULT_FREE
    if task in {"analysis", "scoring", "relevance", "lead_detector"}:
        return settings.LLM_MODEL_ANALYSIS
    if task in {"reply", "offer", "sales_dialog"}:
        return settings.LLM_MODEL_REPLY
    return settings.LLM_MODEL_REPLY


def _normal_messages(system: str, user: str | None, messages: list[dict] | None) -> list[dict]:
    if messages is not None:
        return messages
    if user is None:
        raise ValueError("user or messages is required")
    return [{"role": "user", "content": user}]


def complete_text(
    *,
    system: str,
    user: str | None = None,
    messages: list[dict] | None = None,
    task: str = "reply",
    max_tokens: int = 300,
    temperature: float = 0.2,
) -> str:
    """Return text from the configured LLM provider.

    Supported providers:
    - `anthropic`: direct Claude API via `ANTHROPIC_API_KEY`;
    - `openrouter`: OpenAI-compatible API via `OPENROUTER_API_KEY`;
    - `dry_run` / `none`: fail fast so callers can use their local fallback.
    """
    provider = settings.LLM_PROVIDER
    model = _model_for(task)
    normalized_messages = _normal_messages(system, user, messages)

    if provider in {"dry_run", "none", "disabled"}:
        raise LLMConfigError("LLM_PROVIDER отключен")

    if provider == "anthropic":
        if not settings.ANTHROPIC_API_KEY:
            raise LLMConfigError("ANTHROPIC_API_KEY пустой")
        import anthropic

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=normalized_messages,
        )
        return response.content[0].text.strip()

    if provider == "openrouter":
        if not settings.OPENROUTER_API_KEY:
            raise LLMConfigError("OPENROUTER_API_KEY пустой")
        body = {
            "model": model,
            "messages": [{"role": "system", "content": system}, *normalized_messages],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        if settings.OPENROUTER_SITE_URL:
            headers["HTTP-Referer"] = settings.OPENROUTER_SITE_URL
        if settings.OPENROUTER_APP_TITLE:
            headers["X-OpenRouter-Title"] = settings.OPENROUTER_APP_TITLE
        request = urllib.request.Request(
            OPENROUTER_URL,
            headers=headers,
            data=json.dumps(body).encode("utf-8"),
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            err_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenRouter error {exc.code}: {err_body}") from exc

        if isinstance(data, dict) and data.get("error"):
            raise RuntimeError(f"OpenRouter error: {data['error']}")

        choice = data["choices"][0]
        message = choice.get("message") or {}
        text = _content_to_text(message.get("content"))
        if text:
            return text

        finish_reason = choice.get("finish_reason")
        native_finish_reason = choice.get("native_finish_reason")
        response_model = data.get("model")
        message_keys = sorted(message.keys())
        raise RuntimeError(
            "OpenRouter returned empty message content "
            f"(model={response_model}, finish_reason={finish_reason}, "
            f"native_finish_reason={native_finish_reason}, message_keys={message_keys})"
        )

    raise LLMConfigError(f"Неизвестный LLM_PROVIDER: {provider}")
