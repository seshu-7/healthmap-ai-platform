# Testing Guide

## Test Pyramid

| Layer | Count | What |
|-------|:-----:|------|
| Unit Tests | 37+ | Tools, agents, RAG, MCP, evals, models, API |
| AI Eval Suite | 5 scenarios | Correctness, completeness, hallucination, format |
| E2E Tests | 8 | Health, RAG, agents, evals, MCP discovery |

## Running Tests

```bash
# Unit tests
cd services/ai-agent-service && pytest tests/ -v --cov=app

# AI evals (CI mode — blocks deployment if < 80%)
python -m app.evals.eval_runner --ci --threshold 0.80

# E2E (requires docker-compose up)
cd e2e && pytest -v
```

## Eval Scoring
- **Correctness**: Is risk score in expected range?
- **Completeness**: Are all required findings mentioned?
- **Hallucination**: Anything mentioned NOT in source data?
- **Format**: Valid JSON with required keys?
