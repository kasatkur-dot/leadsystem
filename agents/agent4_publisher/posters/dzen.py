"""Дзен-публикация: безопасный адаптер-заготовка."""

from __future__ import annotations

from pathlib import Path


def publish_file(path: str | Path, lead_id: str | None = None, dry_run: bool = False) -> dict:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Файл для Дзена не найден: {file_path}")
    if dry_run:
        return {"dry_run": True, "channel": "dzen", "file": str(file_path)}
    raise NotImplementedError("Дзен-публикация требует отдельного API/ручного канала и будет включена позже.")
