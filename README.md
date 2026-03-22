# HealthMap AI Care Management Platform

Enterprise AI-driven care management platform using autonomous agents to automate clinical workflows.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     React Dashboard                           │
│               (Care Coordinators / Nurses)                    │
└──────────────────────┬───────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼───────────────────────────────────────┐
│                  API GATEWAY (Nest.js)                         │
│       JWT Auth │ Rate Limiting │ REST + GraphQL                │
└───────┬────────────────────────────────┬─────────────────────┘
        │ REST (proxy)                   │ REST
┌───────▼─────────┐          ┌───────────▼─────────────────────┐
│  Spring Boot    │          │   AI AGENT SERVICE (Python)      │
│  (Existing)     │◄─────────│   LangChain / LangGraph / CrewAI│
│  Patient CRUD   │  tools   │   RAG (Pinecone) / MCP / Evals  │
│  Labs / Meds    │          └───────┬──────────┬──────────────┘
└───────┬─────────┘                  │          │
┌───────▼─────────┐          ┌───────▼───┐ ┌───▼──────────┐
│   PostgreSQL    │          │ Pinecone  │ │  Supabase    │
│   Patient Data  │          │ Vector DB │ │  Audit Logs  │
└─────────────────┘          └───────────┘ └──────────────┘
```

## Services

| Service | Tech | Port | Description |
|---------|------|------|-------------|
| `ai-agent-service` | Python 3.11, FastAPI | 8000 | AI agents, RAG, evals |
| `api-gateway` | Node.js 20, Nest.js | 3000 | Auth, routing, GraphQL |
| `frontend` | React 18, TypeScript | 5173 | Care coordinator dashboard |

## Quick Start

```bash
cp .env.example .env          # Add your API keys
docker-compose up -d           # Start all services
./scripts/setup.sh             # Verify health
# Load sample clinical guidelines:
cd services/ai-agent-service && python -m app.rag.ingestion --sample-data
```

## Running Services

See [Operations Guide](docs/OPERATIONS.md) for detailed startup/shutdown procedures, verification checklist, and troubleshooting.

## Running Tests

```bash
# Unit tests
cd services/ai-agent-service && pytest tests/ -v --cov=app
cd services/api-gateway && npm test

# AI eval suite (blocks deployment if accuracy < 80%)
cd services/ai-agent-service && python -m app.evals.eval_runner --ci

# End-to-end
docker-compose up -d && cd e2e && pytest -v
```

## Documentation

- [Architecture Guide](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Testing Guide](docs/TESTING.md)
- [Use Cases & Workflows](docs/USE_CASES.md)
