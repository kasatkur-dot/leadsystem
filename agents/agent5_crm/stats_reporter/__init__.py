"""Agent 5 stats reporter compatibility layer.

`tasks/roadmap.md` still mentions `stats_reporter` as the weekly reporting
module. The actual MVP channel analytics implementation now lives in
`analytics_reporter`. Keep this thin wrapper so older imports do not point to
an empty module.
"""

from __future__ import annotations

from agents.agent5_crm.analytics_reporter import build_report, run

__all__ = ["build_report", "run"]
