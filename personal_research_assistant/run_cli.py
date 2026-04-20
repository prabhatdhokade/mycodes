"""CLI entrypoint for the Personal Research Assistant."""

from __future__ import annotations

from app.agent import PersonalResearchAssistant
from app.types import AgentReply


def main() -> None:
    print("Personal Research Assistant")
    print("Type 'exit' to quit.\n")
    print("Examples:")
    print("- search latest ai safety paper")
    print("- save important note: Confirm legal review by Friday")
    print("- what do you remember about legal review?\n")

    agent = PersonalResearchAssistant.with_defaults(
        base_dir="runtime",
        interactive_hitl=True,
        enable_streaming=True,
    )

    while True:
        user_input = input("You> ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Assistant> Goodbye!")
            break
        if not user_input:
            continue

        response = agent.handle_turn(user_input, stream=True)
        if isinstance(response, AgentReply):
            print(f"Assistant> {response.text}")
            continue

        print("Assistant> ", end="", flush=True)
        for chunk in response:
            print(chunk, end="", flush=True)
        print()


if __name__ == "__main__":
    main()
