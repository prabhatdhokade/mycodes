"""Web-search tool.

Uses the Tavily API when ``TAVILY_API_KEY`` is configured; otherwise
returns deterministic mock results so the agent still runs without
network access. The mock covers enough query patterns to exercise the
full ReAct loop.
"""

from __future__ import annotations

import json
from typing import Any

from ..config import settings
from .base import Tool, ToolResult

try:
    import requests
except Exception:  # pragma: no cover - requests is in requirements.txt
    requests = None  # type: ignore[assignment]


_MOCK_CORPUS: list[dict[str, str]] = [
    {
        "title": "ReAct: Synergizing Reasoning and Acting in Language Models",
        "url": "https://arxiv.org/abs/2210.03629",
        "snippet": (
            "ReAct prompts LLMs to interleave chain-of-thought reasoning with "
            "tool-use actions, improving factual accuracy and reducing hallucinations."
        ),
    },
    {
        "title": "Retrieval-Augmented Generation (Wikipedia)",
        "url": "https://en.wikipedia.org/wiki/Retrieval-augmented_generation",
        "snippet": (
            "RAG augments LLM prompts with documents fetched from an external "
            "knowledge base such as a vector store."
        ),
    },
    {
        "title": "Human-in-the-loop machine learning (Wikipedia)",
        "url": "https://en.wikipedia.org/wiki/Human-in-the-loop",
        "snippet": (
            "HITL workflows gate automated decisions behind human approval or "
            "correction, common in safety-critical or high-stakes settings."
        ),
    },
    {
        "title": "Streamlit documentation",
        "url": "https://docs.streamlit.io",
        "snippet": "Streamlit turns Python scripts into shareable web apps in minutes.",
    },
    {
        "title": "OpenAI API reference",
        "url": "https://platform.openai.com/docs/api-reference/chat",
        "snippet": "Chat completions API for building conversational AI systems.",
    },
]


class WebSearchTool(Tool):
    name = "web_search"
    description = "Search the web for up-to-date information about a query."
    parameters = {
        "query": {"type": "string", "description": "Search query."},
        "k": {"type": "integer", "description": "Max number of results (default 3)."},
    }

    def __init__(self, timeout_sec: float = 8.0) -> None:
        self.timeout_sec = timeout_sec

    def execute(self, query: str, k: int = 3, **_: Any) -> ToolResult:
        query = (query or "").strip()
        if not query:
            return ToolResult(ok=False, output="Empty query.")
        k = max(1, min(int(k or 3), 10))

        if settings.tavily_api_key and requests is not None:
            try:
                resp = requests.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": settings.tavily_api_key,
                        "query": query,
                        "max_results": k,
                        "search_depth": "basic",
                    },
                    timeout=self.timeout_sec,
                )
                resp.raise_for_status()
                payload = resp.json()
                results = [
                    {
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "snippet": r.get("content", ""),
                    }
                    for r in payload.get("results", [])[:k]
                ]
                return ToolResult(
                    ok=True,
                    output=self._format(query, results),
                    meta={"provider": "tavily", "count": len(results)},
                )
            except Exception as exc:
                return ToolResult(
                    ok=False,
                    output=f"Web search failed: {exc!r}",
                    meta={"provider": "tavily"},
                )

        results = _mock_search(query, k)
        return ToolResult(
            ok=True,
            output=self._format(query, results),
            meta={"provider": "mock", "count": len(results)},
        )

    @staticmethod
    def _format(query: str, results: list[dict[str, str]]) -> str:
        if not results:
            return json.dumps({"query": query, "results": []})
        return json.dumps({"query": query, "results": results}, ensure_ascii=False)


def _mock_search(query: str, k: int) -> list[dict[str, str]]:
    q = query.lower()
    ranked: list[tuple[int, dict[str, str]]] = []
    q_tokens = set(q.split())
    for item in _MOCK_CORPUS:
        text = f"{item['title']} {item['snippet']}".lower()
        score = sum(1 for t in q_tokens if t in text)
        if score:
            ranked.append((score, item))
    ranked.sort(key=lambda p: p[0], reverse=True)
    if not ranked:
        return [
            {
                "title": f"No live results for: {query}",
                "url": "",
                "snippet": (
                    "This is a mock web search. Set TAVILY_API_KEY in .env to "
                    "enable real search. The query was recorded for traceability."
                ),
            }
        ]
    return [item for _, item in ranked[:k]]
