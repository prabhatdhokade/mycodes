"""End-to-end scripted demo of the Personal Research Assistant.

This script exercises every evaluation criterion without requiring an
API key:

  1. Correct tool routing by query intent (search / calendar / notes).
  2. Memory persisting across conversation turns.
  3. HITL checkpoint on important notes.
  4. Structured logs for agent decisions and tool calls.
  5. Long-term fact recall.

Run with:
    python -m personal_research_assistant.demo
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

from personal_research_assistant.app.agent import ResearchAgent
from personal_research_assistant.app.config import settings


def _banner(title: str) -> None:
    bar = "=" * 72
    print(f"\n{bar}\n{title}\n{bar}")


def _print_steps(result) -> None:
    for i, s in enumerate(result.steps, 1):
        obs = s.observation
        if len(obs) > 300:
            obs = obs[:300] + "…"
        print(f"  [{i}] {s.action} :: {obs}")


def main() -> None:
    session_dir = settings.data_dir
    for name in ["conversation_demo.json", "facts.json", "preferences.json"]:
        p = session_dir / name
        if p.exists():
            p.unlink()

    approvals = iter([True, False])

    def approval_cb(tool: str, args: dict) -> bool:
        decision = next(approvals, True)
        print(f"  [HITL] Tool={tool!r} args={list(args)} -> approved={decision}")
        return decision

    agent = ResearchAgent(session_id="demo", approval=approval_cb)
    agent.preferences.set("name", "Ada")
    agent.preferences.set("interests", "ML, climbing, coffee")

    _banner("1) Web search routing")
    r = agent.run("Search for information about the ReAct prompting pattern")
    print(f"answer> {r.answer}")
    _print_steps(r)

    _banner("2) Calendar routing")
    r = agent.run("What's on my calendar today?")
    print(f"answer> {r.answer}")
    _print_steps(r)

    _banner("3) Save an important note (HITL approve)")
    r = agent.run("Please save note that my VPN code is rotating monthly, important!")
    print(f"answer> {r.answer}")
    _print_steps(r)

    _banner("4) Save another note (HITL reject)")
    r = agent.run("Save a note that I like dark roast coffee, important!")
    print(f"answer> {r.answer}")
    _print_steps(r)

    _banner("5) Memory recall across turns")
    r = agent.run("What did I save about my VPN?")
    print(f"answer> {r.answer}")
    _print_steps(r)

    _banner("Log tail")
    log_path = Path(settings.log_file)
    if log_path.exists():
        tail = log_path.read_text(encoding="utf-8").strip().splitlines()[-8:]
        for line in tail:
            try:
                obj = json.loads(line)
                print(
                    textwrap.shorten(
                        f"{obj.get('ts')} {obj.get('level')} {obj.get('event', obj.get('message'))} "
                        f"{ {k: v for k, v in obj.items() if k not in {'ts','level','logger','message','event'}} }",
                        width=200,
                    )
                )
            except json.JSONDecodeError:
                print(line)

    _banner("Done")
    print(
        "Run the UI with:\n"
        "    streamlit run personal_research_assistant/app/ui/streamlit_app.py\n"
        "Or the interactive CLI with:\n"
        "    python -m personal_research_assistant.cli"
    )


if __name__ == "__main__":
    main()
