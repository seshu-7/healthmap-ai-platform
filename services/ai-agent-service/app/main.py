"""HealthMap AI Agent Service - FastAPI Application."""
import uuid, time, structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.models.schemas import OnboardingRequest, RiskAssessmentRequest, AgentType
from app.agents.onboarding_agent import run_patient_onboarding
from app.agents.clinical_crew import run_clinical_assessment
from app.evals.eval_runner import run_all_evals
from app.mcp.servers import initialize_mcp_servers, registry

settings = get_settings()
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI Agent Service", env=settings.app_env)
    logger.info(
        "Resolved service configuration",
        patient_service_url=settings.patient_service_url,
        lab_service_url=settings.lab_service_url,
        medication_service_url=settings.medication_service_url,
        has_google_api_key=bool(settings.google_api_key),
    )
    initialize_mcp_servers()
    logger.info("MCP servers initialized", count=len(registry.list_servers()))
    yield
    logger.info("Shutting down")

app = FastAPI(title="HealthMap AI Agent Service", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.middleware("http")
async def log_requests(request: Request, call_next):
    rid = str(uuid.uuid4())
    start = time.time()
    response = await call_next(request)
    logger.info("request", request_id=rid, method=request.method, path=request.url.path,
                status=response.status_code, duration_ms=int((time.time()-start)*1000))
    response.headers["X-Request-ID"] = rid
    return response

@app.get("/health")
async def health():
    return {"status": "healthy", "service": settings.app_name, "env": settings.app_env, "mcp_servers": len(registry.list_servers())}

@app.get("/ready")
async def readiness():
    checks = {"pinecone": bool(settings.pinecone_api_key), "llm": bool(settings.google_api_key)}
    if not all(checks.values()):
        raise HTTPException(status_code=503, detail={"checks": checks})
    return {"status": "ready", "checks": checks}

@app.post("/api/v1/agents/onboarding")
async def patient_onboarding(request: OnboardingRequest):
    logger.info("onboarding_started", patient_id=request.patient_id)
    try:
        result = await run_patient_onboarding(request.patient_id, request.coordinator_id)
        return {
            "request_id": result.get("request_id"), "agent_type": AgentType.ONBOARDING,
            "patient_id": request.patient_id, "status": "completed",
            "result": {"risk_score": result.get("risk_score"), "risk_level": result.get("risk_level"),
                "summary": result.get("summary"), "key_findings": result.get("key_findings",[]),
                "recommendations": result.get("recommendations",[]),
                "alert_created": result.get("alert_created",False), "next_steps": result.get("next_steps",[])},
            "sources": [g.get("source","") for g in result.get("guidelines",[]) if isinstance(g,dict)],
            "processing_time_ms": result.get("processing_time_ms",0), "errors": result.get("errors",[]),
        }
    except Exception as e:
        logger.error("onboarding_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/agents/assessment")
async def clinical_assessment(request: RiskAssessmentRequest):
    try:
        return await run_clinical_assessment(request.patient_id, "system")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/rag/search")
async def search_guidelines(query: str, condition: str = None, top_k: int = 5):
    from app.rag.retrieval import retrieve_guidelines
    results = retrieve_guidelines(query=query, condition_filter=condition, top_k=top_k)
    return {"query": query, "results": [{"content":r.content,"score":r.score,"metadata":r.metadata} for r in results]}

@app.post("/api/v1/rag/ingest")
async def ingest_document(text: str, document_id: str, title: str, condition: str, doc_type: str = "guideline"):
    from app.rag.ingestion import ingest_document as _ingest
    return _ingest(text=text, document_id=document_id, document_title=title, condition=condition, document_type=doc_type)

@app.get("/api/v1/mcp/servers")
async def list_mcp_servers():
    return {"servers": registry.list_servers()}

@app.get("/api/v1/mcp/tools")
async def list_tools():
    return {"tools": registry.list_all_tools()}

@app.post("/api/v1/evals/run")
async def run_evals(threshold: float = 0.80):
    report = run_all_evals(accuracy_threshold=threshold)
    if not report["summary"]["meets_threshold"]:
        raise HTTPException(status_code=422, detail=report)
    return report

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.port, reload=settings.debug)
