# Personal Research Assistant

A complete, runnable agent application that meets the requested architecture:

- **Memory**: short-term conversation + long-term fact storage (JSON persistence)
- **Tools**: web search (mock), note saver/lookup, calendar lookup
- **HITL checkpoint**: approval before saving important notes
- **Prompting**: ReAct-style structured decision output
- **Observability**: structured JSON logs for LLM calls, tool invocations, decisions, and latencies
- **Stretch goals included**:
  - streaming responses
  - conversation summarization when context grows
  - Streamlit UI

## Project layout

```text
personal_research_assistant/
  app/
    agent.py
    hitl.py
    llm.py
    memory.py
    observability.py
    tools.py
    types.py
  tests/
    test_agent.py
  run_cli.py
  streamlit_app.py
  requirements.txt
```

## Quickstart (CLI)

```bash
cd personal_research_assistant
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run_cli.py
```

### CLI example prompts

- `search latest ai safety paper`
- `remember this: My preferred citation style is APA`
- `save important note: Confirm legal review by Friday`
- `what do you remember about citation style?`
- `calendar tomorrow`

Type `exit` to quit.

## Run tests

```bash
cd personal_research_assistant
pytest -q
```

## Observability

Logs are written to JSONL at:

`personal_research_assistant/runtime/logs/agent.log`

Each event includes:

- `event_type` (e.g., `agent_decision`, `llm_call`, `tool_invocation`, `hitl_checkpoint`)
- `latency_ms`
- `payload`
- `timestamp`
- `trace_id`

## Streamlit UI (stretch goal)

```bash
cd personal_research_assistant
streamlit run streamlit_app.py
```

Features:
- chat interface
- optional streaming toggle
- auto-approve toggle for important-note HITL flow
- conversation persists to runtime memory files
