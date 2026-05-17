"""
Агент 5 — analytics_reporter.

Собирает MVP-отчёт по каналам:
канал -> расход -> лиды -> сделки -> CPL -> CAC -> profit -> окупаемость -> рентабельность.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CHANNEL_REGISTRY_PATH = PROJECT_ROOT / "content/library/sources/channel-registry-mvp.csv"
CHANNEL_COSTS_PATH = PROJECT_ROOT / "data/channel_costs_mvp.csv"
CHANNEL_FACTS_PATH = PROJECT_ROOT / "data/channel_facts_mvp.csv"
REPORT_PATH = PROJECT_ROOT / "data/reports/channel_report_mvp.csv"

REPORT_FIELDS = [
    "period_start",
    "period_end",
    "channel_id",
    "channel_name",
    "status",
    "priority_wave",
    "source_type",
    "traffic_channel",
    "cost_rub",
    "lead_count",
    "qualified_count",
    "meeting_count",
    "deal_count",
    "revenue_rub",
    "profit_rub",
    "cpl_rub",
    "cac_rub",
    "payback_ratio",
    "romi_percent",
    "profitability_percent",
    "decision",
]


@dataclass
class ChannelTotals:
    cost_rub: float = 0.0
    lead_count: int = 0
    qualified_count: int = 0
    meeting_count: int = 0
    deal_count: int = 0
    revenue_rub: float = 0.0


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {path}")
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def _write_csv(path: Path, rows: Iterable[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=REPORT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _to_float(value: str | None) -> float:
    if value in (None, ""):
        return 0.0
    return float(str(value).replace(",", "."))


def _to_int(value: str | None) -> int:
    if value in (None, ""):
        return 0
    return int(float(str(value).replace(",", ".")))


def _format_money(value: float) -> str:
    return f"{value:.2f}"


def _format_metric(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}"


def _safe_div(numerator: float, denominator: float) -> float | None:
    return None if denominator == 0 else numerator / denominator


def _in_period(row: dict[str, str], period_start: str | None, period_end: str | None) -> bool:
    if period_start and row.get("period_start") != period_start:
        return False
    if period_end and row.get("period_end") != period_end:
        return False
    return True


def _period_value(rows: list[dict[str, str]], field: str, fallback: str = "") -> str:
    for row in rows:
        if row.get(field):
            return row[field]
    return fallback


def _aggregate(
    costs: list[dict[str, str]],
    facts: list[dict[str, str]],
    period_start: str | None,
    period_end: str | None,
) -> dict[str, ChannelTotals]:
    totals: dict[str, ChannelTotals] = {}

    for row in costs:
        if not _in_period(row, period_start, period_end):
            continue
        channel_id = row["channel_id"]
        totals.setdefault(channel_id, ChannelTotals()).cost_rub += _to_float(row.get("cost_rub"))

    for row in facts:
        if not _in_period(row, period_start, period_end):
            continue
        channel_id = row["channel_id"]
        total = totals.setdefault(channel_id, ChannelTotals())
        total.lead_count += _to_int(row.get("lead_count"))
        total.qualified_count += _to_int(row.get("qualified_count"))
        total.meeting_count += _to_int(row.get("meeting_count"))
        total.deal_count += _to_int(row.get("deal_count"))
        total.revenue_rub += _to_float(row.get("revenue_rub"))

    return totals


def _decision(
    status: str,
    total: ChannelTotals,
    romi: float | None,
    profitability: float | None,
) -> str:
    if status == "planned":
        return "planned"
    if total.lead_count == 0 and total.cost_rub == 0:
        return "no_data_yet"
    if total.lead_count == 0 and total.cost_rub > 0:
        return "check_tracking_or_pause"
    if total.deal_count == 0:
        return "watch_quality"
    if romi is None:
        return "keep_tracking"
    if romi >= 100 and (profitability is None or profitability >= 30):
        return "scale"
    if romi >= 0:
        return "keep"
    return "pause_or_fix"


def build_report(
    period_start: str | None = None,
    period_end: str | None = None,
    output_path: Path = REPORT_PATH,
) -> list[dict[str, str]]:
    registry = _read_csv(CHANNEL_REGISTRY_PATH)
    costs = _read_csv(CHANNEL_COSTS_PATH)
    facts = _read_csv(CHANNEL_FACTS_PATH)

    totals = _aggregate(costs, facts, period_start, period_end)
    resolved_period_start = period_start or _period_value(costs + facts, "period_start")
    resolved_period_end = period_end or _period_value(costs + facts, "period_end")

    rows: list[dict[str, str]] = []
    for channel in registry:
        channel_id = channel["channel_id"]
        total = totals.get(channel_id, ChannelTotals())
        profit = total.revenue_rub - total.cost_rub
        cpl = _safe_div(total.cost_rub, total.lead_count)
        cac = _safe_div(total.cost_rub, total.deal_count)
        payback = _safe_div(total.revenue_rub, total.cost_rub)
        romi = _safe_div(profit * 100, total.cost_rub)
        profitability = _safe_div(profit * 100, total.revenue_rub)

        rows.append({
            "period_start": resolved_period_start,
            "period_end": resolved_period_end,
            "channel_id": channel_id,
            "channel_name": channel["channel_name"],
            "status": channel["status"],
            "priority_wave": channel["priority_wave"],
            "source_type": channel["source_type"],
            "traffic_channel": channel["traffic_channel"],
            "cost_rub": _format_money(total.cost_rub),
            "lead_count": str(total.lead_count),
            "qualified_count": str(total.qualified_count),
            "meeting_count": str(total.meeting_count),
            "deal_count": str(total.deal_count),
            "revenue_rub": _format_money(total.revenue_rub),
            "profit_rub": _format_money(profit),
            "cpl_rub": _format_metric(cpl),
            "cac_rub": _format_metric(cac),
            "payback_ratio": _format_metric(payback),
            "romi_percent": _format_metric(romi),
            "profitability_percent": _format_metric(profitability),
            "decision": _decision(channel["status"], total, romi, profitability),
        })

    _write_csv(output_path, rows)
    return rows


def run() -> int:
    """Создаёт MVP-отчёт и возвращает количество строк."""
    return len(build_report())


if __name__ == "__main__":
    print(f"rows={run()} report={REPORT_PATH}")
