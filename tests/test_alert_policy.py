"""Tests for `AlertEmissionController` and `parse_alert_rules`."""

from __future__ import annotations

from custom_components.deauth_guard.alert_policy import (
    AlertEmissionController,
    AlertRule,
    parse_alert_rules,
)


def test_parse_drops_invalid() -> None:
    assert parse_alert_rules(None) == []
    assert parse_alert_rules([{"min_count": 0, "window_seconds": 10}]) == []
    assert parse_alert_rules(
        [{"min_count": 2, "window_seconds": 60}]
    ) == [AlertRule(2, 60)]


def test_simulation_no_rules_always_emits() -> None:
    a = AlertEmissionController([], simulation_mode=True)
    assert a.should_emit(1.0) is True
    assert a.should_emit(2.0) is True


def test_production_no_rules_first_only() -> None:
    a = AlertEmissionController([], simulation_mode=False)
    assert a.should_emit(10.0) is True
    assert a.should_emit(11.0) is False
    assert a.should_emit(12.0) is False


def test_sliding_window_two_in_ten() -> None:
    a = AlertEmissionController(
        [AlertRule(min_count=2, window_seconds=10)],
        simulation_mode=False,
    )
    assert a.should_emit(100.0) is False
    assert a.should_emit(101.0) is True
    assert a.should_emit(102.0) is False


def test_reset() -> None:
    a = AlertEmissionController([], simulation_mode=False)
    assert a.should_emit(0.0) is True
    a.reset()
    assert a.should_emit(1.0) is True
