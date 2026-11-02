"""L1 services - canonical domain event bus & command bus (asyncio pub/sub)."""
from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import Callable
from typing import Any

from david_sling.core.utils import call_maybe_async

Handler = Callable[[Any], Any]


class EventBus:
    """Canonical domain event bus. Topics are strings like 'tick', 'signal.routed'."""

    def __init__(self) -> None:
        self._subs: dict[str, list[Handler]] = defaultdict(list)
        self._lock = asyncio.Lock()
        self.published: int = 0

    def subscribe(self, topic: str, handler: Handler) -> Callable[[], None]:
        self._subs[topic].append(handler)

        def unsubscribe() -> None:
            if handler in self._subs.get(topic, []):
                self._subs[topic].remove(handler)

        return unsubscribe

    async def publish(self, topic: str, event: Any) -> None:
        self.published += 1
        for handler in list(self._subs.get(topic, [])):
            await call_maybe_async(handler, event)
        # wildcard subscribers
        for handler in list(self._subs.get("*", [])):
            await call_maybe_async(handler, topic, event)


class CommandBus:
    """Canonical command bus: exactly one handler per command name.

    Every command is audited by the journal domain via the 'command.*' topics.
    """

    def __init__(self, event_bus: EventBus) -> None:
        self._handlers: dict[str, Handler] = {}
        self._bus = event_bus
        self.executed: int = 0

    def register(self, command: str, handler: Handler) -> None:
        if command in self._handlers:
            raise ValueError(f"duplicate command handler: {command}")
        self._handlers[command] = handler

    async def dispatch(self, command: str, payload: Any) -> Any:
        handler = self._handlers.get(command)
        if handler is None:
            raise KeyError(f"no handler registered for command '{command}'")
        self.executed += 1
        result = await call_maybe_async(handler, payload)
        await self._bus.publish("command.dispatched", {"command": command, "result": result})
        return result
