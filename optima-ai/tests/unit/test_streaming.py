"""Tests for streaming adapters."""

from __future__ import annotations

import json

import pytest

from optima_ai.streaming.adapters import (
    SSEAdapter,
    StreamProtocol,
    VercelV4Adapter,
    VercelV5Adapter,
    get_adapter,
)


async def _mock_stream():
    yield {"type": "context", "providers": ["filesystem", "github"]}
    yield {"type": "text_delta", "text": "Hello "}
    yield {"type": "text_delta", "text": "world!"}
    yield {"type": "done", "usage": {"input_tokens": 10, "output_tokens": 5}}


class TestVercelV5Adapter:
    @pytest.mark.asyncio
    async def test_full_stream(self):
        adapter = VercelV5Adapter()
        chunks = []
        async for chunk in adapter.adapt(_mock_stream()):
            chunks.append(chunk)

        assert len(chunks) == 4

        assert chunks[0].startswith("2:")
        assert "filesystem" in chunks[0]

        assert chunks[1].startswith('0:"Hello ')
        assert chunks[2].startswith('0:"world!')

        assert chunks[3].startswith("d:")
        done_data = json.loads(chunks[3][2:])
        assert done_data["finishReason"] == "stop"

    @pytest.mark.asyncio
    async def test_escaping(self):
        adapter = VercelV5Adapter()

        async def stream_with_special_chars():
            yield {"type": "text_delta", "text": 'She said "hello"\nand left'}

        chunks = []
        async for chunk in adapter.adapt(stream_with_special_chars()):
            chunks.append(chunk)

        assert '\\"' in chunks[0]
        assert "\\n" in chunks[0]


class TestVercelV4Adapter:
    @pytest.mark.asyncio
    async def test_outputs_raw_text(self):
        adapter = VercelV4Adapter()
        chunks = []
        async for chunk in adapter.adapt(_mock_stream()):
            chunks.append(chunk)

        assert "Hello " in chunks
        assert "world!" in chunks


class TestSSEAdapter:
    @pytest.mark.asyncio
    async def test_sse_format(self):
        adapter = SSEAdapter()
        chunks = []
        async for chunk in adapter.adapt(_mock_stream()):
            chunks.append(chunk)

        assert all("event: " in c for c in chunks)
        assert all("data: " in c for c in chunks)
        assert all(c.endswith("\n\n") for c in chunks)


class TestGetAdapter:
    def test_get_by_enum(self):
        adapter = get_adapter(StreamProtocol.VERCEL_V5)
        assert isinstance(adapter, VercelV5Adapter)

    def test_get_by_string(self):
        adapter = get_adapter("sse")
        assert isinstance(adapter, SSEAdapter)

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            get_adapter("invalid_protocol")
