"""Streaming protocol adapters.

Supports three output formats, selectable per-request:

  - Vercel AI SDK v5 (AI SDK 4.0+): data stream protocol with typed parts
  - Vercel AI SDK v4 (legacy): text stream protocol
  - Raw SSE: standard Server-Sent Events for non-Vercel clients

Each adapter converts the internal agent stream (AsyncIterator[dict]) into
the wire format expected by the corresponding client SDK.
"""

from __future__ import annotations

import json
from enum import Enum
from typing import Any, AsyncIterator


class StreamProtocol(str, Enum):
    VERCEL_V5 = "vercel_v5"  # AI SDK 4.0+ data stream protocol
    VERCEL_V4 = "vercel_v4"  # Legacy text stream protocol
    SSE = "sse"              # Standard Server-Sent Events


class BaseStreamAdapter:
    """Base class for stream adapters."""

    protocol: StreamProtocol
    content_type: str = "text/event-stream"

    async def adapt(self, stream: AsyncIterator[dict[str, Any]]) -> AsyncIterator[str]:
        raise NotImplementedError


class VercelV5Adapter(BaseStreamAdapter):
    """Vercel AI SDK v5 (Data Stream Protocol).

    Format: each line is `TYPE_ID:JSON_VALUE\\n`
    Part types:
      0 — text delta
      2 — data (metadata/context)
      8 — message annotation (artifacts)
      d — done signal
      e — error
    """

    protocol = StreamProtocol.VERCEL_V5
    content_type = "text/plain; charset=utf-8"

    async def adapt(self, stream: AsyncIterator[dict[str, Any]]) -> AsyncIterator[str]:
        async for event in stream:
            event_type = event.get("type", "")

            if event_type == "text_delta":
                yield f'0:"{self._escape(event["text"])}"\n'

            elif event_type == "context":
                data = json.dumps({"providers": event.get("providers", [])})
                yield f"2:[{data}]\n"

            elif event_type == "artifact":
                annotation = json.dumps({
                    "type": "artifact",
                    "id": event.get("id", ""),
                    "artifact_type": event.get("artifact_type", ""),
                    "title": event.get("title", ""),
                })
                yield f"8:[{annotation}]\n"

            elif event_type == "tool_call":
                tool_data = json.dumps({
                    "toolCallId": event.get("id", ""),
                    "toolName": event.get("name", ""),
                    "args": event.get("args", {}),
                })
                yield f"9:{tool_data}\n"

            elif event_type == "tool_result":
                result_data = json.dumps({
                    "toolCallId": event.get("id", ""),
                    "result": event.get("result", ""),
                })
                yield f"a:{result_data}\n"

            elif event_type == "error":
                yield f'3:"{self._escape(event.get("message", "Unknown error"))}"\n'

            elif event_type == "done":
                usage = event.get("usage", {})
                finish = json.dumps({
                    "finishReason": "stop",
                    "usage": {
                        "promptTokens": usage.get("input_tokens", 0),
                        "completionTokens": usage.get("output_tokens", 0),
                    },
                })
                yield f"d:{finish}\n"

    @staticmethod
    def _escape(text: str) -> str:
        return text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


class VercelV4Adapter(BaseStreamAdapter):
    """Vercel AI SDK v4 (Text Stream Protocol).

    Simple format: raw text chunks streamed directly.
    Metadata is sent as SSE comments.
    """

    protocol = StreamProtocol.VERCEL_V4
    content_type = "text/plain; charset=utf-8"

    async def adapt(self, stream: AsyncIterator[dict[str, Any]]) -> AsyncIterator[str]:
        async for event in stream:
            event_type = event.get("type", "")

            if event_type == "text_delta":
                yield event["text"]

            elif event_type == "context":
                pass

            elif event_type == "done":
                pass


class SSEAdapter(BaseStreamAdapter):
    """Standard Server-Sent Events adapter.

    Format: `event: <type>\\ndata: <json>\\n\\n`
    """

    protocol = StreamProtocol.SSE
    content_type = "text/event-stream; charset=utf-8"

    async def adapt(self, stream: AsyncIterator[dict[str, Any]]) -> AsyncIterator[str]:
        async for event in stream:
            event_type = event.get("type", "")
            data = json.dumps(event)
            yield f"event: {event_type}\ndata: {data}\n\n"


_ADAPTERS: dict[StreamProtocol, type[BaseStreamAdapter]] = {
    StreamProtocol.VERCEL_V5: VercelV5Adapter,
    StreamProtocol.VERCEL_V4: VercelV4Adapter,
    StreamProtocol.SSE: SSEAdapter,
}


def get_adapter(protocol: StreamProtocol | str) -> BaseStreamAdapter:
    if isinstance(protocol, str):
        protocol = StreamProtocol(protocol)
    adapter_cls = _ADAPTERS.get(protocol)
    if not adapter_cls:
        raise ValueError(f"Unsupported stream protocol: {protocol}")
    return adapter_cls()
