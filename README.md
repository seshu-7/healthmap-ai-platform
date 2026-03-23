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

## Setting Up on a New Machine

Follow these steps exactly after cloning the repository on any new machine.

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and **running**
- Git installed

### Step 1 — Clone the repository
```bash
git clone <your-repo-url>
cd healthmap-ai-platform
```

### Step 2 — Create your `.env` file (REQUIRED)

> **Important:** The `.env` file is intentionally excluded from Git (see `.gitignore`) because it contains secret API keys. You must create it manually on every new machine.

```bash
cp .env.example .env
```

Then open `.env` and fill in your real values:

| Variable | Where to get it |
|----------|----------------|
| `GOOGLE_API_KEY` | [Google AI Studio](https://aistudio.google.com) |
| `PINECONE_API_KEY` | Your [Pinecone](https://app.pinecone.io) dashboard |
| `PINECONE_INDEX_NAME` | Your Pinecone index name (default: `healthmap-clinical`) |
| `PINECONE_ENVIRONMENT` | Your Pinecone region (e.g. `us-east-1`) |
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Your Supabase anon/public key |
| `JWT_SECRET` | Any random string, minimum 32 characters |

### Step 3 — Start all services
```bash
docker compose up -d
```
Docker automatically handles all dependencies (`node_modules`, Python packages, Java build). No manual `npm install` or `pip install` needed.

### Step 4 — Verify everything is running
```bash
docker compose ps
```
All services should show `running`. Then open:
- Frontend: http://localhost:5173
- API Gateway: http://localhost:3000
- AI Agent Service: http://localhost:8000/health

### Step 5 — Load sample clinical guidelines (optional but recommended)
```bash
docker compose exec ai-agent-service python -m app.rag.ingestion --sample-data
```

### What the `.gitignore` excludes and why

| Excluded file/folder | Reason | What to do on new machine |
|----------------------|--------|--------------------------|
| `.env` | Contains secret API keys — never commit these | Copy `.env.example` → `.env`, fill in real values |
| `node_modules/` | 300MB+ auto-generated JS packages | Docker handles this automatically |
| `__pycache__/`, `.venv/` | Python-generated bytecode and packages | Docker handles this automatically |
| `dist/`, `build/` | Compiled output — generated from source | Docker handles this automatically |
| `.terraform/`, `*.tfstate` | Cloud infrastructure state files | Run `terraform init` if deploying to AWS |
| `.DS_Store`, `*.log` | OS metadata and log files | Nothing needed |

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
