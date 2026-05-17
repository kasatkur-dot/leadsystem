"""Safe local control layer for chat/voice management of project agents.

This module is intentionally conservative: by default it builds handoff
previews and model-routing decisions, but does not call OpenRouter, Whisper,
image models, embeddings, Redis, Bitrix24, Telegram or the scheduler.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Any

from config import settings

try:
    from shared.llm_client import LLMConfigError, complete_text
except ImportError:  # pragma: no cover - only for unusual direct execution
    LLMConfigError = RuntimeError  # type: ignore
    complete_text = None  # type: ignore


MAX_MESSAGE_CHARS = 4_000


@dataclass(frozen=True)
class ModelRoute:
    key: str
    label: str
    task: str
    model: str
    provider: str
    purpose: str
    status: str = "configured_route"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def build_model_routes() -> list[ModelRoute]:
    free_text_mode = settings.LLM_RUNTIME_MODE in {"openrouter_free_test", "demo_server_free"}
    agent_control_label = "Agent control / OpenRouter free" if free_text_mode else "MiniMax 2.7"
    development_label = "Development / OpenRouter free" if free_text_mode else "Claude Opus 4.7"
    marketing_label = "Marketing / OpenRouter free" if free_text_mode else "Google Flash"
    knowledge_label = "Knowledge / OpenRouter free" if free_text_mode else "Knowledge answer model"
    return [
        ModelRoute(
            key="default_free",
            label="DeepSeek Flash / free",
            task="default_free",
            model=settings.LLM_MODEL_DEFAULT_FREE,
            provider=settings.LLM_PROVIDER,
            purpose="Недорогие обычные ответы агентов и простые проверки.",
        ),
        ModelRoute(
            key="agent_control",
            label=agent_control_label,
            task="agent_control",
            model=settings.LLM_MODEL_AGENT_CONTROL,
            provider=settings.LLM_PROVIDER,
            purpose="Управление агентами, постановка задач, маршрутизация команд.",
        ),
        ModelRoute(
            key="development",
            label=development_label,
            task="development",
            model=settings.LLM_MODEL_DEVELOPMENT,
            provider=settings.LLM_PROVIDER,
            purpose="Разработка, архитектура, сложный дебаг и code review.",
        ),
        ModelRoute(
            key="marketing",
            label=marketing_label,
            task="marketing",
            model=settings.LLM_MODEL_MARKETING,
            provider=settings.LLM_PROVIDER,
            purpose="Маркетинговые тексты, посты, офферы и контентные черновики.",
        ),
        ModelRoute(
            key="knowledge",
            label=knowledge_label,
            task="knowledge",
            model=settings.LLM_MODEL_KNOWLEDGE,
            provider=settings.LLM_PROVIDER,
            purpose="Ответы поверх базы знаний после retrieval/embedding-поиска.",
        ),
        ModelRoute(
            key="transcription",
            label="Whisper",
            task="transcription",
            model=settings.WHISPER_MODEL,
            provider=settings.WHISPER_PROVIDER,
            purpose="Расшифровка голосовых команд пользователя.",
            status="route_only_not_called",
        ),
        ModelRoute(
            key="image",
            label="Kling / Nano Banana image route",
            task="image",
            model=settings.IMAGE_MODEL,
            provider=settings.IMAGE_MODEL_PROVIDER,
            purpose="Картинки для вывода в чат после отдельного включения генератора.",
            status="route_only_not_called",
        ),
        ModelRoute(
            key="embedding",
            label="Embedding model",
            task="embedding",
            model=settings.EMBEDDING_MODEL,
            provider=settings.EMBEDDING_PROVIDER,
            purpose="Векторный поиск по базе знаний.",
            status="route_only_not_called",
        ),
    ]


def build_model_manifest() -> dict[str, Any]:
    return {
        "runtime_mode": settings.LLM_RUNTIME_MODE,
        "live_llm_enabled": bool(settings.AGENT_CONTROL_LIVE_LLM),
        "default_provider": settings.LLM_PROVIDER,
        "routes": [route.__dict__ for route in build_model_routes()],
        "safety": {
            "external_calls_by_default": False,
            "requires_flag_for_live_llm": "AGENT_CONTROL_LIVE_LLM=1",
            "secrets_policy": "API keys are never returned by this endpoint.",
        },
    }


def handle_chat(payload: dict[str, Any], dashboard: dict[str, Any]) -> dict[str, Any]:
    message = _clean_text(payload.get("message"))
    mode = _clean_text(payload.get("mode")) or "manage"
    target_agent_id = _clean_text(payload.get("targetAgentId")) or "orchestrator"
    selected_route = _route_for_mode(mode)
    agent = _find_agent(dashboard, target_agent_id)
    intent = _infer_intent(message, mode)
    handoff_preview = _build_handoff_preview(message, mode, target_agent_id, agent, intent, dashboard)

    external_calls = _external_call_state()
    llm_text = ""
    llm_status = "DRY_RUN_NOT_SENT"
    if settings.AGENT_CONTROL_LIVE_LLM:
        llm_status = "LIVE_LLM_ATTEMPTED"
        try:
            llm_text = _call_live_llm(message, selected_route, handoff_preview)
            external_calls["openrouter_llm"] = True
            llm_status = "OK"
        except (LLMConfigError, RuntimeError, ValueError) as exc:
            llm_status = f"FAILED: {exc}"

    return {
        "status": "OK",
        "created_at": utc_now(),
        "mode": mode,
        "intent": intent,
        "target_agent": {
            "id": target_agent_id,
            "label": agent.get("title") or agent.get("label") or target_agent_id,
            "file": agent.get("file", ""),
        },
        "selected_route": selected_route.__dict__,
        "llm_status": llm_status,
        "assistant_message": llm_text or _local_assistant_message(selected_route, handoff_preview),
        "agent_handoff_preview": handoff_preview,
        "requires_confirmation_before": _confirmation_rules(mode),
        "external_calls": external_calls,
    }


def handle_voice(content_type: str, content_length: int) -> dict[str, Any]:
    return {
        "status": "DRY_RUN_NOT_TRANSCRIBED",
        "created_at": utc_now(),
        "route": _route_by_key("transcription").__dict__,
        "received_audio": {
            "content_type": content_type or "unknown",
            "bytes": int(content_length or 0),
        },
        "transcript_preview": "",
        "next_step": (
            "После включения WHISPER_PROVIDER этот endpoint будет отдавать текст, "
            "а затем передавать его в /api/agent-control/chat."
        ),
        "external_calls": _external_call_state(),
    }


def handle_image(payload: dict[str, Any]) -> dict[str, Any]:
    prompt = _clean_text(payload.get("prompt"))
    return {
        "status": "DRY_RUN_IMAGE_NOT_GENERATED",
        "created_at": utc_now(),
        "route": _route_by_key("image").__dict__,
        "prompt_preview": prompt,
        "image": {
            "url": "",
            "alt": "Image generation is configured as a route but disabled in local dry-run.",
        },
        "next_step": "Включать реальную генерацию только отдельной задачей и после проверки стоимости модели.",
        "external_calls": _external_call_state(),
    }


def handle_knowledge_search(payload: dict[str, Any]) -> dict[str, Any]:
    query = _clean_text(payload.get("query"))
    return {
        "status": "DRY_RUN_NOT_EMBEDDED",
        "created_at": utc_now(),
        "embedding_route": _route_by_key("embedding").__dict__,
        "answer_route": _route_by_key("knowledge").__dict__,
        "query_preview": query,
        "matches": [],
        "next_step": "Позже подключить Supabase/Postgres pgvector или локальный индекс базы знаний.",
        "external_calls": _external_call_state(),
    }


def _route_for_mode(mode: str) -> ModelRoute:
    mode_to_route = {
        "manage": "agent_control",
        "agent_control": "agent_control",
        "develop": "development",
        "development": "development",
        "marketing": "marketing",
        "content": "marketing",
        "knowledge": "knowledge",
        "search": "knowledge",
        "image": "image",
        "default": "default_free",
    }
    return _route_by_key(mode_to_route.get(mode, "default_free"))


def _route_by_key(key: str) -> ModelRoute:
    routes = {route.key: route for route in build_model_routes()}
    return routes[key]


def _find_agent(dashboard: dict[str, Any], target_agent_id: str) -> dict[str, Any]:
    if target_agent_id == "orchestrator":
        return {"title": "AI Orchestrator", "file": "CLAUDE.md / AGENTS.md"}
    for agent in dashboard.get("agent_details", []):
        if agent.get("agent_id") == target_agent_id:
            return agent
    return {"title": target_agent_id, "file": ""}


def _infer_intent(message: str, mode: str) -> str:
    text = message.lower()
    words = set(re.findall(r"[a-zа-яё0-9_]+", text))
    if mode in {"develop", "development"} or words.intersection({"код", "ошибка", "ошибки", "bug", "тест"}):
        return "development_task"
    if mode in {"marketing", "content"} or words.intersection({"пост", "посты", "контент", "оффер", "текст"}):
        return "marketing_task"
    if mode in {"knowledge", "search"} or words.intersection({"найди", "база", "базе", "документ", "документы", "знания"}):
        return "knowledge_search_task"
    if mode == "image" or words.intersection({"картинка", "картинку", "изображение", "визуал"}):
        return "image_generation_task"
    return "agent_management_task"


def _build_handoff_preview(
    message: str,
    mode: str,
    target_agent_id: str,
    agent: dict[str, Any],
    intent: str,
    dashboard: dict[str, Any],
) -> dict[str, Any]:
    return {
        "type": "task-handoff",
        "status": "preview_only",
        "from": "human_chat_or_voice",
        "to": target_agent_id,
        "agent_file": agent.get("file", ""),
        "mode": mode,
        "intent": intent,
        "task": message,
        "known_project_agents": _known_project_agents(dashboard),
        "expected_agent_result": {
            "summary": "Коротко что сделано",
            "artifacts": [],
            "checks": [],
            "next_step": "",
        },
        "memory_rule": "После реального выполнения обновить REPORT.md; детали при необходимости в tasks/session-notes.md.",
    }


def _call_live_llm(message: str, route: ModelRoute, handoff_preview: dict[str, Any]) -> str:
    if complete_text is None:
        raise LLMConfigError("shared.llm_client unavailable")
    system = (
        "Ты управляющий слой многоагентной системы design-studio-lead-engine. "
        "Отвечай кратко и только по данным, которые переданы в Handoff preview. "
        "В проекте ровно 6 продуктовых агентов; не придумывай generic-роли вроде "
        "Market Researcher, UX Designer или Content Writer, если их нет в known_project_agents. "
        "Если спрашивают, кто активен или что есть в системе, перечисляй только known_project_agents "
        "и их status/readiness. Не раскрывай секреты, не запускай внешние сервисы без подтверждения."
    )
    user = (
        f"Route: {route.key}\n"
        f"Task: {message}\n"
        f"Handoff preview: {handoff_preview}"
    )
    return complete_text(system=system, user=user, task=route.task, max_tokens=500, temperature=0.2)


def _known_project_agents(dashboard: dict[str, Any]) -> list[dict[str, Any]]:
    agents: list[dict[str, Any]] = []
    for item in dashboard.get("agent_details", []):
        agents.append(
            {
                "agent_id": item.get("agent_id", ""),
                "title": item.get("title", ""),
                "department": item.get("department") or item.get("role", ""),
                "status": item.get("panel_status", ""),
                "readiness_percent": item.get("readiness_percent"),
                "file": item.get("file", ""),
                "next_action": item.get("next_action", ""),
            }
        )
    return agents


def _local_assistant_message(route: ModelRoute, handoff_preview: dict[str, Any]) -> str:
    return (
        f"Команда принята как preview. Маршрут: {route.label} через {route.provider}. "
        f"Целевой агент: {handoff_preview['to']}. Реальный LLM-вызов не выполнялся."
    )


def _confirmation_rules(mode: str) -> list[str]:
    rules = [
        "реальный вызов OpenRouter",
        "запуск Redis/scheduler",
        "отправка в Bitrix24/Telegram/MAX",
        "публикация контента",
    ]
    if mode == "image":
        rules.append("платная генерация изображения")
    return rules


def _external_call_state() -> dict[str, bool]:
    return {
        "openrouter_llm": False,
        "whisper": False,
        "image_generation": False,
        "embeddings": False,
        "redis": False,
        "bitrix24": False,
        "telegram": False,
        "scheduler": False,
        "publisher": False,
    }


def _clean_text(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()[:MAX_MESSAGE_CHARS]
