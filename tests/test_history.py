"""Tests for `DeauthHistoryStore` and `DeauthRecord`."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.deauth_guard.const import BAND_2_4_GHZ, LOWEST_HISTORY_MAX
from custom_components.deauth_guard.history import (
    DeauthHistoryStore,
    DeauthRecord,
    STORE_SCHEMA_VERSION,
)


def test_deauth_record_from_dict() -> None:
    r = DeauthRecord.from_dict(
        {"ts": 1.5, "data": {"a": 1, "band": BAND_2_4_GHZ}}
    )
    assert r.ts == 1.5
    assert r.data["a"] == 1
    assert r.data["band"] == BAND_2_4_GHZ


def test_normalize_persisted_skips_bad_version() -> None:
    good = {
        "version": STORE_SCHEMA_VERSION,
        "rows": [{"ts": 0.0, "data": {"x": 1}}],
    }
    out = DeauthHistoryStore._normalize_persisted(good)  # noqa: SLF001
    assert len(out) == 1
    out2 = DeauthHistoryStore._normalize_persisted(  # noqa: SLF001
        {"version": 999, "rows": good["rows"]}
    )
    assert out2 == []


def test_normalize_persisted_skips_malformed_row() -> None:
    raw = {
        "version": STORE_SCHEMA_VERSION,
        "rows": [
            {"ts": 0.0, "data": {"ok": True}},
            {"ts": "bad", "data": {}},
        ],
    }
    out = DeauthHistoryStore._normalize_persisted(raw)  # noqa: SLF001
    assert len(out) == 1
    assert out[0].data.get("ok") is True


@pytest.mark.asyncio
async def test_async_add_binds_timestamp_and_persists(
    mock_hass: MagicMock,
) -> None:
    store_mock = AsyncMock()
    store_mock.async_load = AsyncMock(return_value=None)
    store_mock.async_save = AsyncMock()
    with patch("custom_components.deauth_guard.history.Store", return_value=store_mock):
        s = DeauthHistoryStore(mock_hass, max_entries=100)
        await s.async_load()
        rec = await s.async_add({"k": 1}, now=42.0)
        assert rec.ts == 42.0
        assert rec.data == {"k": 1}
        assert store_mock.async_save.await_count >= 1
    one = s.as_list()
    assert len(one) == 1
    assert one[0]["ts"] == 42.0
    assert one[0]["k"] == 1


@pytest.mark.asyncio
async def test_constructor_clamps_max_below_minimum(
    mock_hass: MagicMock,
) -> None:
    store_mock = AsyncMock()
    store_mock.async_load = AsyncMock(return_value=None)
    store_mock.async_save = AsyncMock()
    with patch("custom_components.deauth_guard.history.Store", return_value=store_mock):
        s = DeauthHistoryStore(mock_hass, max_entries=3)
        await s.async_load()
    assert s.max_entries == LOWEST_HISTORY_MAX


@pytest.mark.asyncio
async def test_ring_trims_oldest(mock_hass: MagicMock) -> None:
    store_mock = AsyncMock()
    store_mock.async_load = AsyncMock(return_value=None)
    store_mock.async_save = AsyncMock()
    with patch("custom_components.deauth_guard.history.Store", return_value=store_mock):
        s = DeauthHistoryStore(mock_hass, max_entries=3)
        await s.async_load()
    for i in range(5):
        await s.async_add({"i": i}, now=float(i))
    await asyncio.sleep(0)
    assert [r["i"] for r in s.as_list()] == [2, 3, 4]
    last = s.last()
    assert last is not None
    assert last.data["i"] == 4


@pytest.mark.asyncio
async def test_async_clear_empties(mock_hass: MagicMock) -> None:
    store_mock = AsyncMock()
    store_mock.async_load = AsyncMock(return_value=None)
    store_mock.async_save = AsyncMock()
    with patch("custom_components.deauth_guard.history.Store", return_value=store_mock):
        s = DeauthHistoryStore(mock_hass, max_entries=20)
        await s.async_load()
    await s.async_add({"a": 1}, now=1.0)
    assert len(s.as_list()) == 1
    await s.async_clear()
    assert s.as_list() == []
    assert s.last() is None


@pytest.mark.asyncio
async def test_set_max_entries_trims_and_schedules_persist(
    mock_hass: MagicMock,
) -> None:
    store_mock = AsyncMock()
    store_mock.async_load = AsyncMock(return_value=None)
    store_mock.async_save = AsyncMock()
    with patch("custom_components.deauth_guard.history.Store", return_value=store_mock):
        s = DeauthHistoryStore(mock_hass, max_entries=20)
        await s.async_load()
    for i in range(8):
        await s.async_add({"i": i}, now=float(i))
    s.set_max_entries(3)
    await asyncio.sleep(0)
    assert len(s.as_list()) == 3
    assert s.as_list()[0]["i"] == 5
    assert s.as_list()[-1]["i"] == 7
