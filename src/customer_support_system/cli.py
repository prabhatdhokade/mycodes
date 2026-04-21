from __future__ import annotations

import argparse

from customer_support_system.system import CustomerSupportSystem


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Interactive multi-agent customer support CLI")
    parser.add_argument("--customer-id", default="CUST-001")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    system = CustomerSupportSystem()
    approval = False
    print("Customer support CLI started. Type 'quit' to exit. Use /approve after a refund handoff.")
    while True:
        user_input = input("you> ").strip()
        if user_input.lower() in {"quit", "exit"}:
            break
        if user_input == "/approve":
            approval = True
            user_input = "Please proceed with the approved refund."
        result = system.handle_message(args.customer_id, user_input, approval_granted=approval)
        approval = False
        print(f"agent[{result['current_agent']}]> {result['response']}")
        if result["pending_actions"]:
            print(f"pending> {result['pending_actions']}")
        print(f"trace_count={result['trace_count']} total_cost_usd={result['total_cost_usd']}")


if __name__ == "__main__":
    main()
