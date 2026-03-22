# Operations Guide

## Stopping All Services

### Using Docker Compose
```bash
# Stop and remove all containers (preserves volumes/data by default)
docker compose down

# Stop and remove all containers + volumes (clean slate)
docker compose down -v
```

### Killing Running Processes
Stop all manually running service terminals:
```powershell
# In each terminal running services, press:
Ctrl+C
```

Services to stop:
- **AI Service** (uvicorn on port 8000)
- **Frontend** (npm dev on port 5173)
- **API Gateway** (npm start on port 3000)
- **Patient Service** (Spring Boot on port 8081 - should stop with docker compose down)

---

## Restarting on Another Day

### 1. Start Infrastructure (Docker Compose)
```powershell
cd c:\Users\sesha\OneDrive\Desktop\healthmap-ai-platform\healthmap-ai-platform
docker compose up -d
```

Wait for containers to be healthy:
```powershell
docker compose ps
# Should show: patient-service, postgres/H2 database as "running"
```

### 2. Start AI Service (FastAPI)
```powershell
cd services/ai-agent-service
& ..\..\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 3. Start Frontend (React + Vite)
Open a new terminal:
```powershell
cd services/frontend
npm run dev
```

Expected output:
```
VITE v5.x.x  ready in XXX ms

➜  Local:   http://localhost:5173/
```

### 4. Start API Gateway (NestJS)
Open a new terminal:
```powershell
cd services/api-gateway
npm start
```

Expected output:
```
[NestFactory] Starting Nest application...
[InstanceLoader] ...
[RoutesResolver] AppController{...}
[NestApplication] Nest application successfully started
```

---

## Verification Checklist

### Check All Services Are Running
```powershell
# Verify Docker containers
docker compose ps

# Verify port bindings (Windows PowerShell)
Get-NetTCPConnection -LocalPort 8000 | Select-Object LocalAddress, LocalPort, State
Get-NetTCPConnection -LocalPort 5173 | Select-Object LocalAddress, LocalPort, State
Get-NetTCPConnection -LocalPort 3000 | Select-Object LocalAddress, LocalPort, State
Get-NetTCPConnection -LocalPort 8081 | Select-Object LocalAddress, LocalPort, State
```

### Verify Connectivity
```powershell
# Health check API Gateway
Invoke-RestMethod -Uri http://localhost:3000/health -Method Get | ConvertTo-Json

# Test AI Service
$body = @{ patient_id = 'P001'; coordinator_id = 'test' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/v1/agents/onboarding `
  -Body $body -ContentType 'application/json' -TimeoutSec 90 | ConvertTo-Json -Depth 6

# Frontend should be accessible
Start-Process http://localhost:5173
```

---

## Troubleshooting

### Port Already in Use
```powershell
# Find process using port (example: port 8000)
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object OwningProcess
Stop-Process -Id <PID> -Force

# Or use docker compose to clean up
docker compose down
docker container prune -f
```

### Services Not Connecting
1. Check Docker is running: `docker ps`
2. Verify all containers are up: `docker compose ps`
3. Check logs: `docker compose logs <service-name>`
4. Restart: `docker compose down && docker compose up -d`

### AI Service Import Errors
```powershell
cd services/ai-agent-service
& ..\..\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Frontend Dependencies Missing
```powershell
cd services/frontend
npm install
npm run dev
```

### API Gateway Issues
```powershell
cd services/api-gateway
npm install
npm start
```

---

## Development Notes

- **Hot Reload**: AI service and Frontend auto-reload on code changes
- **Environment**: `.env` file in workspace root loaded automatically on startup
- **Database**: H2 in-memory database; data lost on container restart (unless mounted)
- **Vector DB**: Pinecone (cloud) - persists across restarts
- **Sample Data**: Load with `python -m app.rag.ingestion --sample-data` (after AI service starts)

---

## Quick Reference

| Service | Port | Tech | Reload | Command |
|---------|------|------|--------|---------|
| AI Agent | 8000 | FastAPI | ✅ Auto | `uvicorn app.main:app --reload` |
| Frontend | 5173 | React/Vite | ✅ Auto | `npm run dev` |
| API Gateway | 3000 | NestJS | ❌ Manual | `npm start` |
| Patient Service | 8081 | Spring Boot | N/A | `docker compose` |
