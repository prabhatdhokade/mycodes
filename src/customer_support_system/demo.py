from __future__ import annotations

from customer_support_system.system import CustomerSupportSystem


def main() -> None:
    system = CustomerSupportSystem()
    steps = [
        ("CUST-001", "Can you email my latest invoice and show recent payments?", False),
        ("CUST-001", "Also my service feels slow and I may need a ticket.", False),
        ("CUST-001", "I want a refund for ORD-001.", False),
        ("CUST-001", "Please proceed with the approved refund.", True),
        ("CUST-001", "What contact method do you have on file for me?", False),
    ]
    for index, (customer_id, prompt, approval) in enumerate(steps, start=1):
        result = system.handle_message(customer_id, prompt, approval_granted=approval)
        print(f"Step {index}: {prompt}")
        print(f"  agent: {result['current_agent']}")
        print(f"  response: {result['response']}")
        print(f"  pending: {result['pending_actions']}")
        print(f"  total_cost_usd: {result['total_cost_usd']}")
        print()


if __name__ == "__main__":
    main()
