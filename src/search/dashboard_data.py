import json
import re
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class SearchProgress:
    points_earned: int
    points_max: int
    complete: bool

    @property
    def remaining_points(self) -> int:
        return max(0, self.points_max - self.points_earned)

    def __str__(self) -> str:
        status = "complete" if self.complete else "in progress"
        return f"{self.points_earned}/{self.points_max} pts ({status})"


def _extract_dashboard_json(page_source: str) -> Optional[dict[str, Any]]:
    match = re.search(
        r"var dashboard = (\{.*?\});\s*\n\s*var",
        page_source,
        re.DOTALL,
    )
    if not match:
        match = re.search(r"var dashboard = (\{.*?\});\s*\n", page_source, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def _pc_search_counter(dashboard: dict[str, Any]) -> Optional[dict[str, Any]]:
    try:
        counters = dashboard["userStatus"]["counters"]["pcSearch"]
        if counters:
            return counters[0]
    except (KeyError, IndexError, TypeError):
        pass
    return None


def parse_search_progress(page_source: str) -> Optional[SearchProgress]:
    """Read desktop search point progress from the embedded dashboard JSON."""
    dashboard = _extract_dashboard_json(page_source)
    if dashboard is None:
        return None

    counter = _pc_search_counter(dashboard)
    if counter is None:
        return None

    return SearchProgress(
        points_earned=int(counter.get("pointProgress") or 0),
        points_max=int(counter.get("pointProgressMax") or 0),
        complete=bool(counter.get("complete")),
    )
