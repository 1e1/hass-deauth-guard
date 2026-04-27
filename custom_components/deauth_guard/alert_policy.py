"""When to raise `deauth_guard_attack` (first-only, sliding-window rules, simulation)."""

from __future__ import annotations

from collections import deque
import time
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AlertRule:
    """Fire when at least `min_count` events occur in `window_seconds` (sliding)."""

    min_count: int
    window_seconds: int


def parse_alert_rules(raw: list[dict[str, Any]] | None) -> list[AlertRule]:
    """Normalize options storage into `AlertRule` list (drop invalid entries)."""
    if not raw:
        return []
    out: list[AlertRule] = []
    for item in raw:
        try:
            mc = int(item["min_count"])
            ws = int(item["window_seconds"])
        except (KeyError, TypeError, ValueError):
            continue
        if mc < 1 or ws < 1:
            continue
        out.append(AlertRule(min_count=mc, window_seconds=ws))
    return out


class AlertEmissionController:
    """Decides if a bus event should be emitted for the current (filtered) detection."""

    def __init__(
        self,
        rules: list[AlertRule],
        *,
        simulation_mode: bool,
    ) -> None:
        self._rules = rules
        self._sim = simulation_mode
        self._first_consumed = False
        self._deques: list[deque[float]] = [deque() for _ in rules]

    def reset(self) -> None:
        """Call on integration reload / options change that affect rules."""
        self._first_consumed = False
        for d in self._deques:
            d.clear()

    def should_emit(self, now: float | None = None) -> bool:
        """Return True to fire `deauth_guard_attack` for this detection."""
        t = time.time() if now is None else now

        if self._sim and not self._rules:
            return True
        if not self._sim and not self._rules:
            if not self._first_consumed:
                self._first_consumed = True
                return True
            return False

        for i, rule in enumerate(self._rules):
            dq = self._deques[i]
            dq.append(t)
            cutoff = t - float(rule.window_seconds)
            while dq and dq[0] < cutoff:
                dq.popleft()
            if len(dq) >= rule.min_count:
                dq.clear()
                return True
        return False
