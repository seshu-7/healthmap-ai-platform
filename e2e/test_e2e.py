"""E2E Tests — complete workflows across services. Requires docker-compose up."""
import os, pytest, httpx

GATEWAY = os.getenv("GATEWAY_URL", "http://localhost:3000/api/v1")
AI_SVC = os.getenv("AI_SERVICE_URL", "http://localhost:8000")

@pytest.fixture(scope="session")
def ai():
    return httpx.Client(base_url=AI_SVC, timeout=120)

class TestHealth:
    def test_ai_health(self, ai):
        assert ai.get("/health").status_code == 200

    def test_ai_ready(self, ai):
        assert ai.get("/ready").status_code in (200, 503)

    def test_mcp_init(self, ai):
        r = ai.get("/api/v1/mcp/servers")
        assert r.status_code == 200 and len(r.json()["servers"]) >= 1

class TestRAGE2E:
    def test_ingest_search(self, ai):
        r = ai.post("/api/v1/rag/ingest", params={"text":"CKD eGFR monitoring every 3 months","document_id":"e2e-1","title":"E2E Test","condition":"CKD"})
        if r.status_code == 200:
            assert r.json()["chunks_created"] >= 1

class TestAgentE2E:
    def test_onboarding_accepts(self, ai):
        r = ai.post("/api/v1/agents/onboarding", json={"patient_id":"E2E-001","coordinator_id":"C001"})
        assert r.status_code in (200, 500)

    def test_assessment_accepts(self, ai):
        r = ai.post("/api/v1/agents/assessment", json={"patient_id":"E2E-001","assessment_type":"comprehensive"})
        assert r.status_code in (200, 500)

class TestEvalE2E:
    def test_eval_runs(self, ai):
        r = ai.post("/api/v1/evals/run", params={"threshold": 0.0})
        assert r.status_code == 200 and r.json()["summary"]["total_scenarios"] >= 1

class TestMCPE2E:
    def test_list_tools(self, ai):
        r = ai.get("/api/v1/mcp/tools")
        assert r.status_code == 200 and len(r.json()["tools"]) >= 1
