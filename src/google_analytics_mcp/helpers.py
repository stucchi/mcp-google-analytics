"""Shared helpers for formatting and error handling."""

from __future__ import annotations

import asyncio
import functools
import json
from typing import Any, Callable, Coroutine


def format_json(data: Any) -> str:
    """Pretty-print a dict/list as JSON text."""
    return json.dumps(data, indent=2, default=str)


def proto_to_dict(msg: Any) -> dict:
    """Convert a protobuf message to a plain dict."""
    from google.protobuf.json_format import MessageToDict

    return MessageToDict(msg._pb, preserving_proto_field_name=True)


async def run_sync(fn: Callable, *args: Any, **kwargs: Any) -> Any:
    """Run a sync function in a thread so we don't block the event loop."""
    return await asyncio.to_thread(functools.partial(fn, **kwargs) if kwargs else fn, *args)


def with_setup_guide(fn: Callable[..., Coroutine[Any, Any, str]]) -> Callable[..., Coroutine[Any, Any, str]]:
    """Decorator that catches NotConfiguredError and returns the setup guide."""

    @functools.wraps(fn)
    async def wrapper(*args: Any, **kwargs: Any) -> str:
        from google_analytics_mcp.auth import NotConfiguredError

        try:
            return await fn(*args, **kwargs)
        except NotConfiguredError as e:
            return str(e)

    return wrapper
