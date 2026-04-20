"""Pytest fixtures that isolate each test in its own data dir."""

from __future__ import annotations

import importlib
import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Point the app at a temporary data directory for every test."""

    monkeypatch.setenv("PRA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("PRA_LOG_FILE", str(tmp_path / "agent.log"))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)

    import personal_research_assistant.app.config as config_mod
    importlib.reload(config_mod)
    import personal_research_assistant.app.observability.logger as log_mod
    importlib.reload(log_mod)
    import personal_research_assistant.app.observability as obs_mod
    importlib.reload(obs_mod)

    import personal_research_assistant.app.llm.client as llm_mod
    importlib.reload(llm_mod)
    llm_mod._llm_singleton = None
    import personal_research_assistant.app.llm as llm_pkg
    importlib.reload(llm_pkg)

    import personal_research_assistant.app.memory.conversation as conv_mod
    importlib.reload(conv_mod)
    import personal_research_assistant.app.memory.facts as facts_mod
    importlib.reload(facts_mod)
    import personal_research_assistant.app.memory.preferences as pref_mod
    importlib.reload(pref_mod)
    import personal_research_assistant.app.memory as mem_mod
    importlib.reload(mem_mod)

    import personal_research_assistant.app.tools.base as tb
    importlib.reload(tb)
    import personal_research_assistant.app.tools.web_search as ws
    importlib.reload(ws)
    import personal_research_assistant.app.tools.note_saver as ns
    importlib.reload(ns)
    import personal_research_assistant.app.tools.calendar as cal
    importlib.reload(cal)
    import personal_research_assistant.app.tools.memory_tools as mt
    importlib.reload(mt)
    import personal_research_assistant.app.tools as tools_pkg
    importlib.reload(tools_pkg)

    import personal_research_assistant.app.agent.prompts as prompts_mod
    importlib.reload(prompts_mod)
    import personal_research_assistant.app.agent.research_agent as agent_mod
    importlib.reload(agent_mod)
    import personal_research_assistant.app.agent as agent_pkg
    importlib.reload(agent_pkg)

    yield tmp_path
