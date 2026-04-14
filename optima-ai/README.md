# Optima AI — Real-Time Code Assistance & Agentic Developer Platform

A production-grade developer assistance platform built on the **Claude Agent SDK**, featuring MCP context providers for grounded code assistance, real-time multi-protocol streaming, artifacts management, and smart prompt versioning.

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
│  Vercel AI SDK v5  │  Vercel AI SDK v4  │  SSE Clients          │
└────────┬───────────┴────────┬───────────┴────────┬──────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (api/)                         │
│  /chat  │  /chat/stream  │  /artifacts  │  /prompts  │  /health │
├──────────────────────────────────────────────────────────────────┤
│                    Services Layer                                 │
│  AuthService  │  CacheService (Redis)  │  MCPConfigService       │
├──────────────────────────────────────────────────────────────────┤
│                    Streaming Infrastructure                       │
│  StreamManager  │  VercelV5Adapter  │  VercelV4Adapter  │  SSE   │
├──────────────────────────────────────────────────────────────────┤
│                    Agent Orchestrator                             │
│  CodeAssistant  │  CodeReviewer  │  TestGenerator  │  Debugger   │
├──────────────────────────────────────────────────────────────────┤
│                 MCP Context Providers                             │
│  FileSystem  │  Database  │  GitHub  │  Atlassian  │  Datahub    │
├──────────────────────────────────────────────────────────────────┤
│              Artifacts & Prompt Management                        │
│  ArtifactManager (versioned)  │  PromptManager + Langfuse        │
└──────────────────────────────────────────────────────────────────┘
```

## Key Components

### MCP Context Providers (`optima_ai/mcp_providers/`)

Unified interface for fetching contextual data from external systems:

- **FileSystem** — Reads project files, supports glob search, respects .gitignore patterns
- **Database** — Fetches table schemas and metadata via async SQLAlchemy
- **GitHub** — Pulls PRs, issues, file contents, and code search results
- **Atlassian** — Fetches Jira tickets and Confluence pages for context
- **Datahub** — Queries data catalog metadata, schemas, and lineage

Providers are dynamically configured per-session via `MCPProviderRegistry`.

### Agent Layer (`optima_ai/agents/`)

Built on the **Claude Agent SDK** pattern:

1. Gather context from configured MCP providers (parallel async fetches)
2. Build system prompt enriched with grounding context blocks
3. Execute the Claude tool-use loop (message → tool calls → results → repeat)
4. Extract artifacts from structured output markers
5. Return `AgentResponse` with content + artifacts + usage metrics

The **AgentOrchestrator** handles intent routing and multi-agent pipelines (e.g., generate → review → test).

### Streaming Infrastructure (`optima_ai/streaming/`)

Real-time token streaming with protocol adapters:

| Protocol | Format | Client SDK |
|----------|--------|------------|
| Vercel v5 | Data stream (typed parts: `0:text`, `2:data`, `d:done`) | AI SDK 4.0+ |
| Vercel v4 | Raw text stream | AI SDK 3.x |
| SSE | Standard Server-Sent Events | Any SSE client |

Protocol is auto-negotiated from request headers (`x-stream-protocol`, `x-vercel-ai-data-stream`).

### Artifacts Management (`optima_ai/artifacts/`)

Tracks and versions all generative outputs:

- **Code blocks**, test cases, documentation, API specs, configs
- Full **version history** with content-hash deduplication
- **Diff computation** between artifact versions
- Session-scoped artifact listing and search

### Prompt Management (`optima_ai/prompts/`)

Smart prompt versioning with **Langfuse** integration:

- Named templates with `{{variable}}` substitution
- Version history with rollback support
- **Cache-through** reads via Redis for low-latency resolution
- Langfuse sync for centralized prompt management, traces, and scoring
- Evaluation feedback loops for continuous improvement

### Backend Services (`optima_ai/services/`)

- **AuthService** — JWT token creation/validation, bcrypt password hashing, refresh token flow
- **CacheService** — Async Redis with namespace isolation, TTL management, cache-aside pattern
- **MCPConfigService** — Dynamic per-user/per-session provider configuration with token injection

## Quick Start

```bash
# Clone and install
cd optima-ai
pip install -e ".[dev]"

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run locally
python scripts/run.py

# Or with Docker
docker compose up
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/chat` | Non-streaming chat with agent |
| POST | `/api/v1/chat/stream` | Streaming chat (auto-negotiated protocol) |
| POST | `/api/v1/artifacts` | Create artifact |
| GET | `/api/v1/artifacts/{id}` | Get artifact |
| PUT | `/api/v1/artifacts/{id}` | Update artifact (creates new version) |
| GET | `/api/v1/artifacts/{id}/diff` | Diff between versions |
| POST | `/api/v1/prompts` | Create/version prompt |
| GET | `/api/v1/prompts/{name}` | Get prompt (latest or specific version) |
| POST | `/api/v1/prompts/render` | Render prompt with variables |
| GET | `/api/v1/providers` | List available MCP providers |
| GET | `/health` | Health check |

## Testing

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## Tech Stack

- **Python 3.11+**, **FastAPI**, **Pydantic v2**
- **Anthropic SDK** (Claude Agent SDK pattern)
- **MCP Protocol** (Model Context Protocol)
- **Redis** (caching, session state)
- **PostgreSQL** (persistence)
- **Langfuse** (prompt management, observability)
- **Docker**, **Docker Compose**
- **OpenTelemetry** (distributed tracing)
- **structlog** (structured logging)
