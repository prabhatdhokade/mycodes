"""CLI demo entrypoint for the customer support system."""

from __future__ import annotations

import argparse
import json

from agentic_ai_capstone.app import build_default_system


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the multi-agent support demo")
    parser.add_argument("--customer-id", default="cust-1001")
    parser.add_argument("--message", required=True, help="Customer query to process")
    parser.add_argument(
        "--approve-refund",
        action="store_true",
        help="Approve refund actions above threshold",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    system = build_default_system(refund_auto_approve=args.approve_refund)
    result = system.respond(customer_id=args.customer_id, user_message=args.message)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
