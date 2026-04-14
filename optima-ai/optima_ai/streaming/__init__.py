"""Streaming infrastructure — adapters for Vercel AI SDK v5/v4 and raw SSE."""

from optima_ai.streaming.adapters import (
    SSEAdapter,
    StreamProtocol,
    VercelV4Adapter,
    VercelV5Adapter,
    get_adapter,
)
from optima_ai.streaming.manager import StreamManager

__all__ = [
    "SSEAdapter",
    "StreamProtocol",
    "VercelV4Adapter",
    "VercelV5Adapter",
    "StreamManager",
    "get_adapter",
]
