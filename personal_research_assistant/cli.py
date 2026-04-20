"""Command-line chat interface for the Personal Research Assistant.

Usage:
    python -m personal_research_assistant.cli                       # interactive chat
    python -m personal_research_assistant.cli --auto-approve         # auto-approve notes
    python -m personal_research_assistant.cli --session alice        # pick session id
    python -m personal_research_assistant.cli --once "search for X"  # one-shot mode
"""

from __future__ import annotations

import argparse
import sys

from personal_research_assistant.app.agent import ResearchAgent


def _cli_approval(tool_name: str, args: dict) -> bool:
    print(f"\n[HITL] Tool '{tool_name}' requires approval.")
    print("  Arguments:")
    for k, v in args.items():
        preview = str(v)
        if len(preview) > 200:
            preview = preview[:200] + "…"
        print(f"    - {k}: {preview}")
    while True:
        choice = input("Approve? [y/N]: ").strip().lower()
        if choice in {"y", "yes"}:
            return True
        if choice in {"", "n", "no"}:
            return False
        print("Please answer y or n.")


def _print_trace(result) -> None:
    if not result.steps:
        return
    print("\n--- agent trace ---")
    for i, step in enumerate(result.steps, 1):
        print(f"[{i}] action={step.action}")
        if step.thought:
            print(f"    thought: {step.thought}")
        if step.action_input:
            print(f"    input: {step.action_input}")
        if step.observation and step.action != "final_answer":
            obs = step.observation
            if len(obs) > 400:
                obs = obs[:400] + "…"
            print(f"    observation: {obs}")
    print("-------------------\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Personal Research Assistant CLI")
    parser.add_argument("--session", default="cli", help="Session id (default: cli)")
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Auto-approve HITL-gated actions (useful in scripts).",
    )
    parser.add_argument("--once", help="Run a single prompt and exit.")
    parser.add_argument("--trace", action="store_true", help="Print ReAct trace.")
    parser.add_argument("--stream", action="store_true", help="Stream the final answer.")
    args = parser.parse_args(argv)

    approval = (lambda _t, _a: True) if args.auto_approve else _cli_approval
    agent = ResearchAgent(session_id=args.session, approval=approval)

    mode = "mock" if agent.llm.is_mock else "live"
    print(f"Personal Research Assistant · session='{args.session}' · LLM={mode}")
    print("Type 'exit' to quit, '/reset' to clear conversation.\n")

    def handle(prompt: str) -> None:
        if args.stream:
            for chunk in agent.stream(prompt):
                sys.stdout.write(chunk)
                sys.stdout.flush()
            print()
            return
        result = agent.run(prompt)
        print(f"assistant> {result.answer}")
        if args.trace:
            _print_trace(result)

    if args.once:
        handle(args.once)
        return 0

    while True:
        try:
            line = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        if line.lower() in {"exit", "quit", "/quit"}:
            break
        if line == "/reset":
            agent.conversation.clear()
            print("(conversation cleared)")
            continue
        handle(line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
