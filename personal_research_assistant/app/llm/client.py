"""LLM client abstraction.

The agent talks to a single ``LLMClient`` interface.  In production we use
the OpenAI chat completions API; in development (and in CI) we fall back
to a deterministic rule-based mock that still produces valid ReAct JSON.
This means the whole project runs end-to-end without network or API keys.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Iterable, Iterator

from ..config import settings
from ..observability import get_logger, timed

logger = get_logger("llm")


@dataclass
class LLMResponse:
    content: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    raw: dict[str, Any] | None = None


class LLMClient:
    """Thin wrapper around the chat completion API (or its mock twin)."""

    def __init__(self, model: str | None = None) -> None:
        self.model = model or settings.openai_model
        self._client = None
        if settings.use_real_llm:
            try:
                from openai import OpenAI

                self._client = OpenAI(api_key=settings.openai_api_key)
            except Exception as exc:
                logger.warning(
                    "openai_init_failed",
                    extra={"event": "openai_init_failed", "error": repr(exc)},
                )
                self._client = None

    @property
    def is_mock(self) -> bool:
        return self._client is None

    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.2,
        max_tokens: int = 800,
        response_format: str = "text",
    ) -> LLMResponse:
        """Synchronous chat completion."""

        event_fields = {
            "model": self.model,
            "mock": self.is_mock,
            "messages": len(messages),
            "temperature": temperature,
        }
        with timed(logger, "llm.call", **event_fields) as ctx:
            if self.is_mock:
                text = _mock_complete(messages)
                ctx["prompt_tokens"] = sum(len(m["content"].split()) for m in messages)
                ctx["completion_tokens"] = len(text.split())
                return LLMResponse(content=text, model=f"mock:{self.model}")

            kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if response_format == "json":
                kwargs["response_format"] = {"type": "json_object"}

            resp = self._client.chat.completions.create(**kwargs)  # type: ignore[union-attr]
            choice = resp.choices[0].message.content or ""
            usage = getattr(resp, "usage", None)
            pt = getattr(usage, "prompt_tokens", 0) if usage else 0
            ct = getattr(usage, "completion_tokens", 0) if usage else 0
            ctx["prompt_tokens"] = pt
            ctx["completion_tokens"] = ct
            return LLMResponse(
                content=choice,
                model=self.model,
                prompt_tokens=pt,
                completion_tokens=ct,
                raw=resp.model_dump() if hasattr(resp, "model_dump") else None,
            )

    def stream(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.2,
        max_tokens: int = 800,
    ) -> Iterator[str]:
        """Yield partial content chunks for streaming UIs."""

        if self.is_mock:
            full = _mock_complete(messages)
            for word in re.findall(r"\S+\s*", full):
                yield word
            return

        with self._client.chat.completions.stream(  # type: ignore[union-attr]
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        ) as stream:
            for event in stream:
                if event.type == "content.delta":
                    yield event.delta


_llm_singleton: LLMClient | None = None


def get_llm() -> LLMClient:
    global _llm_singleton
    if _llm_singleton is None:
        _llm_singleton = LLMClient()
    return _llm_singleton


def _last_user_message(messages: Iterable[dict[str, str]]) -> str:
    """Return the most recent non-observation user message."""

    for m in reversed(list(messages)):
        if m.get("role") != "user":
            continue
        content = m.get("content", "") or ""
        if content.startswith("Observation:"):
            continue
        return content
    return ""


def _mock_complete(messages: list[dict[str, str]]) -> str:
    """Deterministic response generator used when no API key is configured.

    The mock inspects the last user message and either:
      * Returns a ReAct JSON action when the system prompt looks like the
        agent's reasoning prompt, or
      * Returns a plain natural-language summary for summarization prompts.
    """

    system = next((m["content"] for m in messages if m["role"] == "system"), "")
    user = _last_user_message(messages)
    user_l = user.lower()

    if "summariz" in system.lower() or "summary" in system.lower():
        snippet = user.strip().replace("\n", " ")
        if len(snippet) > 240:
            snippet = snippet[:240] + "…"
        return f"Summary: {snippet}"

    if "react" in system.lower() or "thought" in system.lower():
        assistant_turns = [m for m in messages if m["role"] == "assistant"]
        already_recalled = any("recall_fact" in (m.get("content") or "") for m in assistant_turns)
        last_observation = ""
        for m in reversed(messages):
            if m["role"] == "user" and m.get("content", "").startswith("Observation:"):
                last_observation = m["content"][len("Observation:"):].strip()
                break

        recall_triggers = [
            "remind me", "my note", "saved note", "preferences",
            "who am i", "what did i", "what have i", "do i have",
            "remember", "about my",
        ]
        if any(kw in user_l for kw in recall_triggers) and not already_recalled:
            return json.dumps(
                {
                    "thought": "The user is asking about stored info; check long-term memory first.",
                    "action": "recall_fact",
                    "action_input": {"query": user},
                }
            )
        if already_recalled and last_observation:
            try:
                payload = json.loads(last_observation)
                results = payload.get("results", [])
            except Exception:
                results = []
            if results:
                top = results[0]
                answer = (
                    f"From your saved notes (id {top['id']}, importance {top['importance']}): "
                    f"{top['content']}"
                )
            else:
                answer = (
                    "I searched your long-term memory but didn't find a matching note yet."
                )
            return json.dumps(
                {
                    "thought": "Summarize recall results for the user.",
                    "action": "final_answer",
                    "action_input": {"answer": answer},
                }
            )
        save_triggers = ["save note", "save this", "take a note", "remember that", "note that", "save a note"]
        already_saved = any("save_note" in (m.get("content") or "") for m in assistant_turns)
        if any(kw in user_l for kw in save_triggers) and not already_saved:
            return json.dumps(
                {
                    "thought": "The user asked to save a note - this is a HITL-guarded action.",
                    "action": "save_note",
                    "action_input": {
                        "title": user[:60],
                        "content": user,
                        "important": True,
                    },
                }
            )
        if already_saved and last_observation:
            if last_observation.startswith("ERROR"):
                answer = "I did not save the note because the approval was declined."
            else:
                answer = f"Done. {last_observation}"
            return json.dumps(
                {
                    "thought": "Report outcome of save_note tool to user.",
                    "action": "final_answer",
                    "action_input": {"answer": answer},
                }
            )
        already_calendar = any("calendar_lookup" in (m.get("content") or "") for m in assistant_turns)
        already_search = any("web_search" in (m.get("content") or "") for m in assistant_turns)

        if any(kw in user_l for kw in ["calendar", "schedule", "meeting", "today", "tomorrow", "appointment"]) and not already_calendar:
            return json.dumps(
                {
                    "thought": "The user wants calendar information.",
                    "action": "calendar_lookup",
                    "action_input": {"query": user},
                }
            )
        if already_calendar and last_observation:
            try:
                payload = json.loads(last_observation)
                events = payload.get("events", [])
            except Exception:
                events = []
            if events:
                lines = [f"- {e['title']} at {e['start']} ({e.get('location', '')})" for e in events]
                answer = "Here's what I found on your calendar:\n" + "\n".join(lines)
            else:
                answer = "I didn't find any matching calendar events."
            return json.dumps(
                {
                    "thought": "Summarize calendar results.",
                    "action": "final_answer",
                    "action_input": {"answer": answer},
                }
            )

        if any(kw in user_l for kw in ["search", "find", "look up", "who is", "what is", "latest"]) and not already_search:
            return json.dumps(
                {
                    "thought": "The user wants factual information - use web search.",
                    "action": "web_search",
                    "action_input": {"query": user},
                }
            )
        if already_search and last_observation:
            try:
                payload = json.loads(last_observation)
                results = payload.get("results", [])
            except Exception:
                results = []
            if results:
                top = results[0]
                answer = f"{top['snippet']} (source: {top['url'] or 'mock'})"
            else:
                answer = "Web search returned no results."
            return json.dumps(
                {
                    "thought": "Summarize search results.",
                    "action": "final_answer",
                    "action_input": {"answer": answer},
                }
            )
        return json.dumps(
            {
                "thought": "No tool is needed - answer directly.",
                "action": "final_answer",
                "action_input": {
                    "answer": (
                        "I'm your research assistant. Ask me to search the web, "
                        "check your calendar, or save a note and I'll help."
                    )
                },
            }
        )

    return f"(mock reply) I heard: {user}"
