"""Голосовая озвучка через ElevenLabs."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import re
import urllib.error
import urllib.request

from config import settings
from agents.agent4_publisher.core.config import OUT_VOICE


def _slug(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9а-яА-ЯёЁ]+", "-", text).strip("-").lower()
    return cleaned[:48] or "voice"


def synthesize_voice(text: str, output: str | None = None, dry_run: bool = False) -> Path:
    path = Path(output) if output else OUT_VOICE / f"{datetime.now():%Y%m%d-%H%M%S}-{_slug(text)}.mp3"
    path.parent.mkdir(parents=True, exist_ok=True)

    if dry_run:
        placeholder = path.with_suffix(".txt")
        placeholder.write_text(f"DRY-RUN VOICE SCRIPT\n{text}\n", encoding="utf-8")
        return placeholder

    if not settings.ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY пустой. Для озвучки заполни `.env`.")
    if not settings.ELEVENLABS_VOICE_ID:
        raise RuntimeError("ELEVENLABS_VOICE_ID пустой. Для озвучки заполни `.env`.")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{settings.ELEVENLABS_VOICE_ID}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": settings.ELEVENLABS_API_KEY,
        },
        data=json.dumps({
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }).encode("utf-8"),
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            path.write_bytes(response.read())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"ElevenLabs вернул ошибку {exc.code}: {body}") from exc
    return path
