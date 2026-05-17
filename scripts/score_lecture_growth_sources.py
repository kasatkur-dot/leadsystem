"""Score the 2026-05-15 lecture growth source map locally.

The script is read-only against external systems. It only reads a local CSV and
writes local reports. It does not call Bitrix24, Telegram, MAX, VK, ads, Redis,
LLM APIs, scheduler, publisher, or any paid service.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = PROJECT_ROOT / "content" / "library" / "sources" / "lecture-2026-05-15-growth-source-map.csv"
REPORT_JSON_PATH = PROJECT_ROOT / "data" / "reports" / "lecture_growth_source_score.json"
REPORT_MD_PATH = PROJECT_ROOT / "data" / "reports" / "lecture_growth_source_score.md"


SEGMENT_WEIGHTS = {
    "b2b": 5,
    "commercial_real_estate": 5,
    "warehouses": 5,
    "retail_fitout": 5,
    "crm_base": 5,
    "all_segments": 4,
    "local_search": 4,
    "private_and_small_business": 3,
}

PLATFORM_WEIGHTS = {
    "Bitrix24": 5,
    "Tender": 5,
    "Web": 5,
    "MAX": 4,
    "2GIS": 4,
    "Yandex": 4,
    "Telegram": 3,
    "VK": 3,
    "Avito": 3,
    "Forums": 2,
}

RISK_PENALTY = {
    "low": 0,
    "medium": 2,
    "high": 5,
}

STATUS_BONUS = {
    "approved": 3,
    "approved_readonly": 3,
    "candidate": 1,
    "testing": 2,
    "rejected": -5,
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _relative(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return [
            {key: (value or "").strip() for key, value in row.items()}
            for row in csv.DictReader(file)
            if any((value or "").strip() for value in row.values())
        ]


def _score(row: dict[str, str]) -> dict[str, Any]:
    segment = row.get("segment", "")
    platform = row.get("platform", "")
    risk = row.get("risk_level", "")
    status = row.get("status", "")
    allowed_contact = row.get("allowed_contact_method", "")

    audience_score = SEGMENT_WEIGHTS.get(segment, 2)
    platform_score = PLATFORM_WEIGHTS.get(platform, 2)
    readiness_score = STATUS_BONUS.get(status, 0)
    risk_score = max(0, 5 - RISK_PENALTY.get(risk, 3))
    has_safe_contact = 1 if allowed_contact and "approved" in allowed_contact or allowed_contact.startswith("own_") or allowed_contact.startswith("manual_") else 0

    total = audience_score + platform_score + readiness_score + risk_score + has_safe_contact

    if risk == "low" and total >= 14:
        priority = "P1"
    elif total >= 12:
        priority = "P2"
    elif total >= 9:
        priority = "P3"
    else:
        priority = "P4"

    if status in {"approved", "approved_readonly"} and risk == "low":
        action_now = "Можно готовить локальный dry-run и материалы без внешнего запуска."
    elif "approved" in allowed_contact:
        action_now = "Нужен ручной список кандидатов и approval перед любым касанием."
    elif allowed_contact.startswith("manual_"):
        action_now = "Только ручная проверка и ручной ответ после отдельного разрешения."
    else:
        action_now = "Сначала read-only исследование, без контактов и публикаций."

    delayed = []
    if platform in {"Telegram", "VK", "Forums"}:
        delayed.append("Найти конкретные площадки и проверить правила размещения.")
    if platform in {"Web"}:
        delayed.append("Собрать шорт-лист компаний и удалить нерелевантные.")
    if platform in {"2GIS", "Yandex"}:
        delayed.append("Проверить права доступа к карточке и текущий профиль.")
    if platform == "Tender":
        delayed.append("Подготовить фильтры тендеров и чеклист документов.")
    if risk == "medium":
        delayed.append("Юридически проверить способ первого касания.")
    if platform == "Bitrix24":
        delayed.append("После read-only анализа отдельно согласовать реактивацию старых контактов.")

    if not delayed:
        delayed.append("После первого dry-run решить, переводить ли источник в тест.")

    return {
        "source_id": row.get("source_id", ""),
        "source_name": row.get("source_name", ""),
        "platform": platform,
        "segment": segment,
        "owner_agent": row.get("owner_agent", ""),
        "status": status,
        "risk_level": risk,
        "allowed_contact_method": allowed_contact,
        "utm_source": row.get("utm_source", ""),
        "priority": priority,
        "score": total,
        "score_parts": {
            "audience": audience_score,
            "platform": platform_score,
            "readiness": readiness_score,
            "risk": risk_score,
            "safe_contact": has_safe_contact,
        },
        "action_now": action_now,
        "delayed_items": delayed,
        "bitrix_tags": [
            f"source:{row.get('utm_source', '')}",
            f"segment:{segment}",
            f"platform:{platform.lower()}",
            f"risk:{risk}",
        ],
        "next_action": row.get("next_action", ""),
        "notes": row.get("notes", ""),
    }


def _summary(scored: list[dict[str, Any]]) -> dict[str, Any]:
    by_priority: dict[str, int] = {}
    by_risk: dict[str, int] = {}
    by_owner: dict[str, int] = {}
    for item in scored:
        by_priority[item["priority"]] = by_priority.get(item["priority"], 0) + 1
        by_risk[item["risk_level"]] = by_risk.get(item["risk_level"], 0) + 1
        by_owner[item["owner_agent"]] = by_owner.get(item["owner_agent"], 0) + 1

    top_sources = sorted(scored, key=lambda item: (-int(item["score"]), item["source_id"]))[:5]
    approval_required = [
        item
        for item in scored
        if item["risk_level"] != "low" or item["status"] not in {"approved", "approved_readonly"}
    ]
    return {
        "source_count": len(scored),
        "by_priority": dict(sorted(by_priority.items())),
        "by_risk": dict(sorted(by_risk.items())),
        "by_owner": dict(sorted(by_owner.items())),
        "top_sources": [
            {
                "source_id": item["source_id"],
                "source_name": item["source_name"],
                "priority": item["priority"],
                "score": item["score"],
            }
            for item in top_sources
        ],
        "approval_required_count": len(approval_required),
    }


def _write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Lecture Growth Source Score",
        "",
        f"Generated at: `{report['generated_at']}`",
        "",
        "Статус: локальный read-only скоринг. Внешние сервисы и отправки не запускались.",
        "",
        "## Summary",
        "",
        f"- Источников: {report['summary']['source_count']}",
        f"- Требуют approval или уточнения: {report['summary']['approval_required_count']}",
        f"- Приоритеты: {json.dumps(report['summary']['by_priority'], ensure_ascii=False)}",
        f"- Риски: {json.dumps(report['summary']['by_risk'], ensure_ascii=False)}",
        "",
        "## Top Sources",
        "",
        "| ID | Источник | Приоритет | Score |",
        "|---|---|---|---:|",
    ]
    for item in report["summary"]["top_sources"]:
        lines.append(f"| {item['source_id']} | {item['source_name']} | {item['priority']} | {item['score']} |")

    lines.extend(
        [
            "",
            "## Full Score",
            "",
            "| ID | Источник | Платформа | Сегмент | Риск | Приоритет | Score | Что делать сейчас | Что отложить |",
            "|---|---|---|---|---|---|---:|---|---|",
        ]
    )
    for item in report["sources"]:
        delayed = "<br>".join(item["delayed_items"])
        lines.append(
            "| {source_id} | {source_name} | {platform} | {segment} | {risk_level} | {priority} | {score} | {action_now} | {delayed} |".format(
                **item,
                delayed=delayed,
            )
        )

    lines.append("")
    REPORT_MD_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = _read_rows(SOURCE_PATH)
    scored = [_score(row) for row in rows]
    report = {
        "status": "OK",
        "generated_at": _utc_now(),
        "source_file": _relative(SOURCE_PATH),
        "readonly": True,
        "external_calls": {
            "redis": False,
            "bitrix24": False,
            "telegram_send": False,
            "max": False,
            "vk": False,
            "ads": False,
            "llm": False,
            "scheduler": False,
            "publisher": False,
        },
        "summary": _summary(scored),
        "sources": scored,
    }
    REPORT_JSON_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_markdown(report)

    print("lecture_growth_source_score_status=OK")
    print(f"source_count={report['summary']['source_count']}")
    print(f"approval_required_count={report['summary']['approval_required_count']}")
    print(f"report_file={_relative(REPORT_JSON_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
