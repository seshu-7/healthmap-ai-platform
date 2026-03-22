#!/bin/bash
set -e
echo "=== HealthMap AI Platform Setup ==="
command -v docker >/dev/null || { echo "Docker required"; exit 1; }
[ ! -f .env ] && { cp .env.example .env; echo "Edit .env with API keys"; exit 1; }
docker-compose up -d
echo "Waiting for services..."
for i in $(seq 1 30); do curl -sf http://localhost:8000/health >/dev/null 2>&1 && break; sleep 2; done
echo "AI Service: http://localhost:8000"
echo "API Gateway: http://localhost:3000"
echo "AI Docs: http://localhost:8000/docs"
