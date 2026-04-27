"""Pytest fixtures for deauth_guard tests."""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from typing import Any
from unittest.mock import MagicMock

import pytest

from tests.ha_stubs import register_minimal_homeassistant

register_minimal_homeassistant()


@pytest.fixture
def mock_hass() -> MagicMock:
    """Minimal Home Assistant core mock with a working `async_create_task`."""

    hass = MagicMock()

    def _create_task(coro: Coroutine[Any, Any, Any]) -> asyncio.Task[Any]:
        return asyncio.get_running_loop().create_task(coro)

    hass.async_create_task = MagicMock(side_effect=_create_task)
    return hass
