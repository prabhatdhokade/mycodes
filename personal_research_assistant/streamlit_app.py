"""Streamlit UI for the Personal Research Assistant."""

from __future__ import annotations

import streamlit as st

from app.agent import PersonalResearchAssistant


def _build_agent(auto_approve_notes: bool) -> PersonalResearchAssistant:
    return PersonalResearchAssistant.with_defaults(
        base_dir="runtime",
        auto_approve_notes=auto_approve_notes,
        interactive_hitl=False,
        enable_streaming=False,
    )


def main() -> None:
    st.set_page_config(page_title="Personal Research Assistant", page_icon=":brain:")
    st.title("Personal Research Assistant")
    st.caption("ReAct agent with memory, tools, HITL, and observability")

    auto_approve = st.sidebar.toggle("Auto-approve important notes", value=True)

    if "assistant" not in st.session_state or st.session_state.get("auto_approve") != auto_approve:
        st.session_state.assistant = _build_agent(auto_approve_notes=auto_approve)
        st.session_state.auto_approve = auto_approve
        st.session_state.messages = []

    assistant: PersonalResearchAssistant = st.session_state.assistant

    for role, content in st.session_state.messages:
        with st.chat_message(role):
            st.markdown(content)

    prompt = st.chat_input("Ask me to search, save notes, or check calendar")
    if prompt:
        st.session_state.messages.append(("user", prompt))
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            reply = assistant.handle_turn(prompt, stream=False)
            st.markdown(reply.text)
        st.session_state.messages.append(("assistant", reply.text))

        with st.expander("Trace details", expanded=False):
            st.write({"trace_id": reply.trace_id, "latency_ms": reply.latency_ms, "tools": reply.used_tools})


if __name__ == "__main__":
    main()
