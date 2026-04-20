from __future__ import annotations

import json

from personal_research_assistant.app.agent import ResearchAgent
from personal_research_assistant.app.llm import LLMClient, LLMResponse


class ScriptedLLM(LLMClient):
    """LLM stub that replays a queue of canned responses in order."""

    def __init__(self, replies: list[str]):
        self._client = None
        self.model = "scripted"
        self._replies = list(replies)
        self.calls: list[list[dict[str, str]]] = []

    def complete(self, messages, **_kw):
        self.calls.append(messages)
        content = self._replies.pop(0) if self._replies else json.dumps(
            {"thought": "done", "action": "final_answer", "action_input": {"answer": "ok"}}
        )
        return LLMResponse(content=content, model=self.model)

    def stream(self, messages, **_kw):
        yield self.complete(messages).content


def _step(action: str, **inp: object) -> str:
    return json.dumps(
        {"thought": f"try {action}", "action": action, "action_input": dict(inp)}
    )


def test_react_routes_to_web_search_then_answers(isolated_data_dir):
    llm = ScriptedLLM(
        replies=[
            _step("web_search", query="react prompting"),
            _step("final_answer", answer="ReAct interleaves reasoning and acting."),
        ]
    )
    agent = ResearchAgent(session_id="t1", llm=llm)
    result = agent.run("search for react prompting")
    assert "ReAct" in result.answer
    actions = [s.action for s in result.steps]
    assert actions == ["web_search", "final_answer"]


def test_hitl_rejection_short_circuits(isolated_data_dir):
    llm = ScriptedLLM(
        replies=[
            _step("save_note", title="api keys", content="secret", important=True),
            _step("final_answer", answer="Not saved."),
        ]
    )
    agent = ResearchAgent(
        session_id="t2",
        llm=llm,
        approval=lambda _t, _a: False,
    )
    result = agent.run("please remember this api key, important")
    save_step = next(s for s in result.steps if s.action == "save_note")
    assert save_step.approved is False
    assert not agent.fact_store.all()


def test_hitl_approval_persists_note(isolated_data_dir):
    llm = ScriptedLLM(
        replies=[
            _step("save_note", title="vpn", content="rotate monthly", important=True),
            _step("final_answer", answer="Saved."),
        ]
    )
    agent = ResearchAgent(session_id="t3", llm=llm, approval=lambda _t, _a: True)
    agent.run("save a note that vpn rotates monthly, important")
    assert agent.fact_store.all()
    assert agent.fact_store.all()[0].importance == 5


def test_conversation_memory_persists_across_turns(isolated_data_dir):
    llm = ScriptedLLM(
        replies=[
            _step("final_answer", answer="Hi Ada."),
            _step("final_answer", answer="You told me your name is Ada."),
        ]
    )
    agent = ResearchAgent(session_id="t4", llm=llm)
    agent.run("Hi, I'm Ada.")
    agent.run("What's my name?")
    turns = [m.content for m in agent.conversation.messages]
    assert "Hi, I'm Ada." in turns
    assert any("Ada" in t for t in turns)


def test_unknown_tool_recovers(isolated_data_dir):
    llm = ScriptedLLM(
        replies=[
            _step("nonexistent_tool", foo=1),
            _step("final_answer", answer="Recovered."),
        ]
    )
    agent = ResearchAgent(session_id="t5", llm=llm)
    result = agent.run("do something weird")
    assert result.answer == "Recovered."
    assert "Unknown tool" in result.steps[0].observation


def test_logs_capture_agent_decisions(isolated_data_dir):
    llm = ScriptedLLM(replies=[_step("final_answer", answer="ok")])
    agent = ResearchAgent(session_id="t6", llm=llm)
    agent.run("hello")
    log_file = isolated_data_dir / "agent.log"
    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert "agent.turn.start" in content
    assert "agent.turn.end" in content
    assert "agent.step" in content
    assert '"session_id": "t6"' in content


def test_conversation_summarization_triggers(isolated_data_dir):
    class SummarizingLLM(ScriptedLLM):
        def complete(self, messages, **kw):
            sys_msg = next((m for m in messages if m["role"] == "system"), {"content": ""})
            if "summariz" in sys_msg["content"].lower():
                return LLMResponse(content="rolling summary", model=self.model)
            return super().complete(messages, **kw)

    replies = [_step("final_answer", answer=f"reply {i}") for i in range(15)]
    llm = SummarizingLLM(replies=replies)
    agent = ResearchAgent(session_id="t7", llm=llm)
    summarized = False
    for i in range(12):
        r = agent.run(f"turn {i}")
        summarized = summarized or r.summarized
    assert summarized is True
    assert agent.conversation.summary
