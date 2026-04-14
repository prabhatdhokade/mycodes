"""Stream manager — handles lifecycle of streaming sessions.

Coordinates between the agent's async generator and the HTTP response,
handling backpressure, cancellation, and protocol negotiation.
"""

from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator

from starlette.requests import Request
from starlette.responses import StreamingResponse

from optima_ai.agents.base import BaseAgent
from optima_ai.core.logging import get_logger
from optima_ai.streaming.adapters import StreamProtocol, get_adapter

logger = get_logger(__name__)


class StreamManager:
    """Manages streaming sessions between agents and HTTP clients."""

    def __init__(self):
        self._active_streams: dict[str, asyncio.Task] = {}

    def negotiate_protocol(self, request: Request) -> StreamProtocol:
        """Determine the streaming protocol from request headers.

        Priority:
          1. Explicit `x-stream-protocol` header
          2. `x-vercel-ai-data-stream` header (indicates v5)
          3. Accept header hints
          4. Default to SSE
        """
        explicit = request.headers.get("x-stream-protocol", "").lower()
        if explicit in {p.value for p in StreamProtocol}:
            return StreamProtocol(explicit)

        if request.headers.get("x-vercel-ai-data-stream"):
            return StreamProtocol.VERCEL_V5

        accept = request.headers.get("accept", "")
        if "text/event-stream" in accept:
            return StreamProtocol.SSE

        return StreamProtocol.SSE

    async def create_streaming_response(
        self,
        agent: BaseAgent,
        user_message: str,
        request: Request,
        conversation: list[dict] | None = None,
        protocol: StreamProtocol | None = None,
    ) -> StreamingResponse:
        """Create a StreamingResponse that streams agent output in the negotiated format."""
        if protocol is None:
            protocol = self.negotiate_protocol(request)

        adapter = get_adapter(protocol)
        agent_stream = agent.run_stream(user_message, conversation)
        adapted_stream = adapter.adapt(agent_stream)

        async def response_generator() -> AsyncIterator[str]:
            try:
                async for chunk in adapted_stream:
                    yield chunk
            except asyncio.CancelledError:
                logger.info("stream_cancelled")
            except Exception as exc:
                logger.error("stream_error", error=str(exc))
                error_chunk = f"event: error\ndata: {str(exc)}\n\n"
                yield error_chunk

        return StreamingResponse(
            response_generator(),
            media_type=adapter.content_type,
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Stream-Protocol": protocol.value,
            },
        )

    async def cancel_stream(self, stream_id: str) -> bool:
        task = self._active_streams.pop(stream_id, None)
        if task and not task.done():
            task.cancel()
            return True
        return False
