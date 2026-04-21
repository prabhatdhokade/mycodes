"""Command-line interface for the multi-agent customer support system."""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Optional

from .memory.store import MemoryStore
from .observability import get_tracer
from .orchestrator import (
    AutoApprovePolicy,
    AutoDenyPolicy,
    HITLPolicy,
    Orchestrator,
    QueuedPolicy,
)


class InteractiveConsolePolicy(HITLPolicy):
    """Prompt the operator via stdin to approve or deny a pending action."""

    def approve(self, pending_action):
        print("\n=== HUMAN-IN-THE-LOOP APPROVAL REQUIRED ===")
        print(json.dumps(pending_action, indent=2, default=str))
        while True:
            ans = input("Approve? [y/n/q]: ").strip().lower()
            if ans in ("y", "yes"):
                return "approve"
            if ans in ("n", "no"):
                return "deny"
            if ans in ("q", "quit"):
                return "pending"


def _build_orchestrator(args) -> Orchestrator:
    memory = MemoryStore(path=args.memory_path) if args.memory_path else MemoryStore()
    if args.auto_approve:
        policy: HITLPolicy = AutoApprovePolicy()
    elif args.auto_deny:
        policy = AutoDenyPolicy()
    elif args.queue_hitl:
        policy = QueuedPolicy()
    else:
        policy = InteractiveConsolePolicy()
    return Orchestrator(memory=memory, hitl_policy=policy)


def _run_repl(args) -> int:
    orch = _build_orchestrator(args)
    state = orch.create_session(customer_id=args.customer_id)
    print(f"Customer Support CLI (customer_id={args.customer_id}) — type 'exit' to quit.")
    print(f"Trace id: {state['trace_id']}")
    while True:
        try:
            user = input("\nYou> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user:
            continue
        if user.lower() in ("exit", "quit", ":q"):
            break
        if user.startswith("/"):
            if _handle_slash(user, state, orch):
                continue
        result = orch.step(state, user)
        label = result.agent.upper()
        print(f"{label}> {result.reply}")
        if result.tool_calls:
            for tc in result.tool_calls:
                print(f"  [tool] {tc['name']} ok={tc['ok']}")
        if result.hitl_required:
            print(f"  [HITL] pending: {result.hitl_reason}")
    # Print trace summary on exit
    print("\n--- Trace summary ---")
    print(json.dumps(get_tracer().summary(), indent=2))
    return 0


def _handle_slash(cmd: str, state, orch: Orchestrator) -> bool:
    parts = cmd.split()
    if parts[0] in ("/trace", "/t"):
        print(json.dumps(get_tracer().summary(), indent=2))
        return True
    if parts[0] == "/state":
        redacted = {k: v for k, v in state.items() if k != "messages"}
        print(json.dumps(redacted, indent=2, default=str))
        return True
    if parts[0] == "/history":
        profile = orch.memory.get(state["customer_id"])
        if not profile:
            print("(no history)")
            return True
        for m in profile.conversation_log[-10:]:
            print(f"  [{m['role']}] {m['content'][:120]}")
        return True
    if parts[0] == "/pending":
        print(json.dumps(state.get("pending_actions", []), indent=2, default=str))
        return True
    if parts[0] == "/approve" and len(parts) > 1:
        action_id = parts[1]
        for p in state.get("pending_actions", []):
            if p["action_id"] == action_id and p["status"] == "pending":
                state["hitl_decision"] = "approve"
                # Re-execute via a simple empty-prompt nudge to the current agent
                result = orch.step(state, "approve pending refund")
                print(f"{result.agent.upper()}> {result.reply}")
                return True
        print(f"No pending action with id {action_id}")
        return True
    if parts[0] in ("/help", "/?"):
        print(
            "Slash commands: /trace, /state, /history, /pending, "
            "/approve <action_id>, /help, exit"
        )
        return True
    return False


def _run_eval(args) -> int:
    from .evaluation import run_evaluation, load_default_suite

    suite = load_default_suite()
    report = run_evaluation(suite)
    print(report.format_text())
    if args.json_report:
        with open(args.json_report, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=2, default=str)
        print(f"\nJSON report written to {args.json_report}")
    return 0 if report.pass_rate >= 0.9 else 1


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(prog="customer-support")
    sub = parser.add_subparsers(dest="cmd", required=True)

    chat = sub.add_parser("chat", help="Interactive chat")
    chat.add_argument("--customer-id", default="cust_001")
    chat.add_argument("--memory-path", default=None)
    grp = chat.add_mutually_exclusive_group()
    grp.add_argument("--auto-approve", action="store_true")
    grp.add_argument("--auto-deny", action="store_true")
    grp.add_argument("--queue-hitl", action="store_true")

    ev = sub.add_parser("eval", help="Run evaluation suite")
    ev.add_argument("--json-report", default=None)

    args = parser.parse_args(argv)
    if args.cmd == "chat":
        return _run_repl(args)
    if args.cmd == "eval":
        return _run_eval(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
