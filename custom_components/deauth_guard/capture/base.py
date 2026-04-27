"""Abstract event source for 802.11 deauthentication–style events."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import Any


class DeauthEventSource(ABC):
    """Interface implemented by capture backends (simulation, scapy, etc.)."""

    @abstractmethod
    async def async_start(
        self,
        on_event: Callable[[dict[str, Any]], Awaitable[None] | None],
    ) -> None:
        """Begin delivery; `on_event` is called with a payload dict."""

    @abstractmethod
    async def async_stop(self) -> None:
        """Tear down resources (threads, file handles, subprocesses)."""
