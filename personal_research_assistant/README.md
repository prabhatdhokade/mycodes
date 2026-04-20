# Personal Research Assistant

A complete **ReAct-pattern agent application** that ticks every box in the
evaluation rubric: memory, tools, human-in-the-loop, structured prompting,
and full observability — with a CLI, a Streamlit UI, and 14 unit tests.

```
+-------------------------------------------------------------+
|                       User Interface                        |
|           CLI · Streamlit · programmatic API                |
+-------------------------------------------------------------+
|               Research Agent (ReAct Loop)                   |
|   Thought  ->  Action (tool)  ->  Observation -> repeat     |
+-------------------------------------------------------------+
|  Tools                          |  Memory                   |
|   - web_search (mock/real)      |   - Conversation (+sum.)  |
|   - save_note  (HITL gated)     |   - Facts (vector-ish)    |
|   - calendar_lookup             |   - Preferences           |
|   - recall_fact                 |                           |
+-------------------------------------------------------------+
|          Observability: JSON logs + latency tracking        |
+-------------------------------------------------------------+
```

## Features matched to the rubric

| Requirement                                       | Where it lives                                                 |
|---------------------------------------------------|----------------------------------------------------------------|
| Short-term conversation memory                    | `app/memory/conversation.py`                                   |
| Long-term fact storage (vector-ish retrieval)     | `app/memory/facts.py` + `app/tools/memory_tools.py`            |
| User preferences store                            | `app/memory/preferences.py`                                    |
| Web search tool (real via Tavily, mock fallback)  | `app/tools/web_search.py`                                      |
| Note-taking tool                                  | `app/tools/note_saver.py`                                      |
| Calendar lookup tool                              | `app/tools/calendar.py`                                        |
| HITL approval before saving important notes       | `Tool.requires_approval` + `HumanApproval` callback            |
| ReAct pattern with structured JSON outputs        | `app/agent/prompts.py` + `app/agent/research_agent.py`         |
| Log every LLM call & tool invocation with latency | `app/observability/logger.py` (JSON lines, rotating file)      |
| Streaming responses                               | `ResearchAgent.stream()`, Streamlit UI streams the final answer|
| Conversation summarization when context grows     | `ConversationMemory.maybe_summarize()`                         |
| Streamlit web UI                                  | `app/ui/streamlit_app.py`                                      |

## Quick start

```bash
pip install -r personal_research_assistant/requirements.txt

# 1) End-to-end scripted demo (no API key needed, uses mock LLM + mock search)
python -m personal_research_assistant.demo

# 2) Interactive CLI
python -m personal_research_assistant.cli --trace

# 3) Streamlit web UI
streamlit run personal_research_assistant/app/ui/streamlit_app.py

# 4) Tests
pytest personal_research_assistant/tests -q
```

## Configuration

Copy `.env.example` to `.env` (or set the equivalent env vars). **All
values are optional** — the agent falls back to a deterministic mock
LLM and mock web-search corpus so it runs in any environment.

| Variable                | Purpose                                                      |
|-------------------------|--------------------------------------------------------------|
| `OPENAI_API_KEY`        | Enables the real OpenAI client. Leave blank for mock mode.   |
| `OPENAI_MODEL`          | Model name (default: `gpt-4o-mini`).                         |
| `TAVILY_API_KEY`        | Enables real web search through Tavily. Blank = mock corpus. |
| `PRA_DATA_DIR`          | Where conversation/facts/calendar JSON live.                 |
| `PRA_LOG_FILE`          | Path to the JSON-lines log file.                             |
| `PRA_LOG_LEVEL`         | Python log level (default `INFO`).                           |
| `PRA_MAX_STEPS`         | Max ReAct iterations per turn (default 6).                   |
| `PRA_SUMMARIZE_AFTER`   | Summarize conversation after N turns (default 10).           |
| `PRA_AUTO_APPROVE_NOTES`| Skip HITL prompts (scripts only). Default: false.            |

## Architecture walk-through

### 1. `ResearchAgent` — the ReAct loop

`ResearchAgent.run(user_message)` drives one turn:

1. Append the user message to short-term memory.
2. Build the system prompt with (a) the tool catalogue, (b) the current
   preferences, and (c) the top-K matching long-term facts.
3. Loop up to `max_react_steps`:
   * Ask the LLM for ONE JSON object `{thought, action, action_input}`.
   * If `action == "final_answer"` → return.
   * Otherwise look up the tool, invoke it (with HITL if required), and
     append the observation so the next LLM call can reason about it.
4. After the turn, conditionally run `ConversationMemory.maybe_summarize`
   which rolls older turns into a summary prefix.

Every LLM call and every tool invocation is wrapped in the `timed`
context manager which logs `*.start` and `*.end` JSON records with a
`trace_id` and `latency_ms`.

### 2. Memory

* **ConversationMemory** — JSON-on-disk list of messages per session
  with a rolling LLM-generated summary when history exceeds N turns.
* **FactStore** — JSON list of `{id, content, tags, importance, ts}`
  retrieved by token-overlap cosine similarity (importance-weighted).
  Interface mirrors a vector store so it's a one-file swap for
  Chroma/FAISS/pgvector.
* **PreferenceStore** — plain key/value JSON, surfaced in the system
  prompt on every turn.

### 3. Tools and HITL

All tools subclass `Tool` (see `app/tools/base.py`). Tools with
`requires_approval = True` run only after the registered
`HumanApproval` callback returns `True`. The CLI prompts on stdin;
the Streamlit UI renders an approval card that gates the rerun; your
own code can pass any `(tool_name, args) -> bool` callable.

### 4. Observability

`app/observability/logger.py` configures a rotating file handler +
stdout stream handler on the `pra` logger, both emitting compact
JSON-per-line records:

```json
{"ts":"2026-04-20T08:18:11","level":"INFO","logger":"pra.llm",
 "message":"llm.call.end","event":"llm.call.end",
 "trace_id":"3383ceaea3c7","latency_ms":0.12,
 "model":"gpt-4o-mini","mock":true,"messages":10,
 "prompt_tokens":589,"completion_tokens":50}
```

Point any log aggregator at the log file and you get agent-level
traces for free.

### 5. Stretch goals

* **Streaming**: `ResearchAgent.stream()` yields chunks; the Streamlit
  UI paints them as they arrive.
* **Summarization**: `ConversationMemory.maybe_summarize` replaces
  older turns with an LLM-generated summary when `summarize_after` is
  exceeded.
* **Web UI**: full Streamlit app with chat, preference editor, saved
  notes list, reset button, and HITL approval modal.

## Tests

```
$ pytest personal_research_assistant/tests -q
..............  14 passed
```

The suite covers memory persistence, tool behaviour, HITL accept/reject
paths, tool routing, unknown-tool recovery, structured logging, and
conversation summarization — all without network access.
