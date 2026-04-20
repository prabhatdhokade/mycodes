"""Streamlit chat UI for the Personal Research Assistant.

Run with:

    streamlit run personal_research_assistant/app/ui/streamlit_app.py
"""

from __future__ import annotations

import json
import re
import sys
import time
from dataclasses import asdict
from pathlib import Path

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st  # noqa: E402

from personal_research_assistant.app.agent import ResearchAgent  # noqa: E402


st.set_page_config(
    page_title="Personal Research Assistant",
    page_icon="PRA",
    layout="wide",
)

st.title("Personal Research Assistant")
st.caption("ReAct agent · memory · tools · HITL · observability")

if "chat" not in st.session_state:
    st.session_state.chat = []  # list[{role, content, steps?}]
if "session_id" not in st.session_state:
    st.session_state.session_id = "streamlit"
if "approvals" not in st.session_state:
    st.session_state.approvals = {}  # tool name -> bool
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


def approval_callback(tool_name: str, args: dict) -> bool:
    """Ask the user via a modal-ish block and wait (rerun-driven)."""

    key = f"approval::{tool_name}::{hash(json.dumps(args, sort_keys=True, default=str))}"
    if key in st.session_state.approvals:
        return st.session_state.approvals[key]
    st.session_state["awaiting_approval"] = {"key": key, "tool": tool_name, "args": args}
    return False


@st.cache_resource(show_spinner=False)
def _agent_for_session(session_id: str) -> ResearchAgent:
    return ResearchAgent(session_id=session_id, approval=approval_callback)


agent = _agent_for_session(st.session_state.session_id)

with st.sidebar:
    st.subheader("Session")
    st.write(f"**Session id:** `{st.session_state.session_id}`")
    st.write(f"**LLM:** {'mock' if agent.llm.is_mock else 'real'} ({agent.llm.model})")
    st.write(f"**Max ReAct steps:** {agent.max_steps}")
    if st.button("Reset conversation"):
        agent.conversation.clear()
        st.session_state.chat = []
        st.session_state.approvals = {}
        st.rerun()

    st.divider()
    st.subheader("Preferences")
    prefs = agent.preferences.all()
    if prefs:
        for k, v in prefs.items():
            st.write(f"- **{k}**: {v}")
    else:
        st.caption("No preferences saved yet.")
    with st.form("pref_form", clear_on_submit=True):
        pk = st.text_input("Key")
        pv = st.text_input("Value")
        if st.form_submit_button("Save preference") and pk:
            agent.preferences.set(pk, pv)
            st.rerun()

    st.divider()
    st.subheader("Saved notes")
    notes = agent.fact_store.all()[-10:]
    if not notes:
        st.caption("No notes yet.")
    for f in notes:
        with st.expander(f"[{f.id}] importance={f.importance}"):
            st.write(f.content)
            if st.button(f"Delete {f.id}", key=f"del_{f.id}"):
                agent.fact_store.delete(f.id)
                st.rerun()

for turn in st.session_state.chat:
    with st.chat_message(turn["role"]):
        st.markdown(turn["content"])
        if turn.get("steps"):
            with st.expander("Agent trace"):
                for i, step in enumerate(turn["steps"], 1):
                    st.markdown(
                        f"**Step {i} · action:** `{step['action']}`\n\n"
                        f"*Thought:* {step['thought']}"
                    )
                    if step["action_input"]:
                        st.code(
                            json.dumps(step["action_input"], indent=2, default=str),
                            language="json",
                        )
                    if step.get("observation"):
                        obs = step["observation"]
                        if len(obs) > 1200:
                            obs = obs[:1200] + "…"
                        st.markdown(f"*Observation:* {obs}")
                    if step.get("approved") is not None:
                        st.caption(f"HITL approved: {step['approved']}")


awaiting = st.session_state.get("awaiting_approval")
if awaiting:
    with st.container(border=True):
        st.warning(f"Approval required for tool `{awaiting['tool']}`")
        st.code(json.dumps(awaiting["args"], indent=2, default=str), language="json")
        col1, col2 = st.columns(2)
        if col1.button("Approve", type="primary"):
            st.session_state.approvals[awaiting["key"]] = True
            del st.session_state["awaiting_approval"]
            if st.session_state.pending_prompt is not None:
                st.rerun()
        if col2.button("Reject"):
            st.session_state.approvals[awaiting["key"]] = False
            del st.session_state["awaiting_approval"]
            if st.session_state.pending_prompt is not None:
                st.rerun()


def _run_turn(user_text: str) -> None:
    st.session_state.chat.append({"role": "user", "content": user_text})
    result = agent.run(user_text)
    placeholder_container = st.chat_message("assistant")
    with placeholder_container:
        placeholder = st.empty()
        accumulated = ""
        for chunk in re.findall(r"\S+\s*", result.answer):
            accumulated += chunk
            placeholder.markdown(accumulated + "▌")
            time.sleep(0.01)
        placeholder.markdown(accumulated)
    steps_payload = [
        {
            "thought": s.thought,
            "action": s.action,
            "action_input": s.action_input,
            "observation": s.observation,
            "approved": s.approved,
        }
        for s in result.steps
    ]
    st.session_state.chat.append(
        {"role": "assistant", "content": result.answer, "steps": steps_payload}
    )


prompt = st.chat_input("Ask me to search, check your calendar, or save a note…")
if prompt and not awaiting:
    st.session_state.pending_prompt = prompt
    _run_turn(prompt)
    st.session_state.pending_prompt = None
    st.rerun()
