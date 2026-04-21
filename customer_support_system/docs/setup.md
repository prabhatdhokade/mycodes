# Setup Instructions

## Prerequisites

- Python 3.10+
- pip
- (Optional) OpenAI API key for real LLM reasoning

## Local development

```bash
cd customer_support_system
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run tests

```bash
pytest                         # 79 unit + integration tests
pytest --cov=src               # with coverage (requires pytest-cov)
```

## Run the evaluation suite

```bash
python -m src.cli eval
python -m src.cli eval --json-report report.json
```

## Run the interactive CLI

```bash
python -m src.cli chat --customer-id cust_001
python -m src.cli chat --customer-id cust_001 --auto-approve  # demo mode
python -m src.cli chat --customer-id cust_001 --auto-deny     # strict mode
python -m src.cli chat --customer-id cust_001 --queue-hitl    # queue pending actions
```

### Slash commands inside chat

| Command         | Effect                                                |
| --------------- | ----------------------------------------------------- |
| `/trace`        | Show current tracer summary (spans / cost / tokens)   |
| `/state`        | Dump current state dict (excluding messages)          |
| `/history`      | Dump last 10 persisted messages                       |
| `/pending`      | Dump pending HITL actions                             |
| `/approve <id>` | Approve a pending action by `action_id`               |
| `/help`         | Show slash command help                               |
| `exit`          | Leave the chat (prints trace summary)                 |

## Using a real OpenAI backend

```bash
export OPENAI_API_KEY=sk-...
export CSS_MODEL=gpt-4o-mini
python -m src.cli chat --customer-id cust_001
```

## Exporting traces (Langfuse / LangSmith compatible JSONL)

```bash
export CSS_TRACE_FILE=./trace.jsonl
python -m src.cli chat --customer-id cust_001
```

Each line is a `Span` with:
- `span_id`, `trace_id`, `parent_id`
- `name`, `kind` (`llm` | `tool` | `agent` | `router` | `guardrail` | `hitl`)
- `start_ts`, `end_ts`, `inputs`, `outputs`
- `tokens_in`, `tokens_out`, `model`, `cost_usd`, `status`

## Optional: LangGraph adapter

```bash
pip install langgraph langchain-core
python -c "from src.langgraph_adapter import build_langgraph_app; print(build_langgraph_app())"
```

The adapter returns a compiled LangGraph `StateGraph` whose nodes call the
same orchestrator methods.
