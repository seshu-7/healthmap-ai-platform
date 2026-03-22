"""Unit Tests — 37+ tests covering tools, agents, RAG, MCP, evals, models, API."""
import json, pytest
from unittest.mock import patch, MagicMock

class TestTools:
    @patch("app.agents.tools.httpx.get")
    def test_get_demographics_success(self, mock_get):
        from app.agents.tools import get_patient_demographics
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"patient_id":"P001","first_name":"John"})
        mock_get.return_value.raise_for_status = MagicMock()
        data = json.loads(get_patient_demographics.invoke("P001"))
        assert data["patient_id"] == "P001"

    @patch("app.agents.tools.httpx.get")
    def test_get_demographics_not_found(self, mock_get):
        from app.agents.tools import get_patient_demographics
        import httpx
        mock_get.return_value = MagicMock(status_code=404)
        mock_get.return_value.raise_for_status.side_effect = httpx.HTTPStatusError("", request=MagicMock(), response=MagicMock(status_code=404))
        data = json.loads(get_patient_demographics.invoke("X"))
        assert "error" in data

    @patch("app.agents.tools.httpx.get")
    def test_get_labs_success(self, mock_get):
        from app.agents.tools import get_patient_labs
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"results":[{"test_name":"eGFR","value":35}]})
        mock_get.return_value.raise_for_status = MagicMock()
        data = json.loads(get_patient_labs.invoke({"patient_id":"P001","limit":5}))
        assert "results" in data

    @patch("app.agents.tools.httpx.get")
    def test_get_medications_success(self, mock_get):
        from app.agents.tools import get_patient_medications
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"medications":[{"drug_name":"Lisinopril"}]})
        mock_get.return_value.raise_for_status = MagicMock()
        data = json.loads(get_patient_medications.invoke("P001"))
        assert "medications" in data

    @patch("app.agents.tools.retrieve_guidelines")
    def test_search_guidelines(self, mock_ret):
        from app.agents.tools import search_clinical_guidelines
        mock_ret.return_value = [MagicMock(content="CKD guide",score=0.92,metadata={"document_title":"CKD","condition":"ckd"})]
        data = json.loads(search_clinical_guidelines.invoke({"query":"CKD","condition":"ckd"}))
        assert len(data) == 1
        assert data[0]["relevance_score"] == 0.92

    @patch("app.agents.tools.httpx.post")
    def test_create_alert(self, mock_post):
        from app.agents.tools import create_patient_alert
        mock_post.return_value = MagicMock(status_code=201)
        mock_post.return_value.raise_for_status = MagicMock()
        data = json.loads(create_patient_alert.invoke({"patient_id":"P001","priority":"URGENT","title":"High","description":"eGFR low","recommended_action":"Review"}))
        assert data["alert"]["priority"] == "URGENT"

class TestOnboardingAgent:
    def test_graph_compiles(self):
        from app.agents.onboarding_agent import build_onboarding_graph
        assert build_onboarding_graph() is not None

    def test_fetch_demographics_error(self):
        from app.agents.onboarding_agent import fetch_demographics
        state = {"patient_id":"X","demographics":{},"errors":[]}
        with patch("app.agents.onboarding_agent.get_patient_demographics") as m:
            m.invoke.return_value = json.dumps({"error":"Not found"})
            r = fetch_demographics(state)
            assert len(r["errors"]) > 0

    def test_route_creates_alert_high_risk(self):
        from app.agents.onboarding_agent import route_result
        state = {"patient_id":"P001","risk_score":8,"risk_level":"HIGH","key_findings":["eGFR low"],
            "recommendations":["Nephrology"],"demographics":{"first_name":"John","last_name":"Doe"},
            "labs":[],"medications":[],"alert_created":False,"summary":"","next_steps":[],"errors":[]}
        with patch("app.agents.onboarding_agent.create_patient_alert") as m:
            m.invoke.return_value = json.dumps({"status":"created"})
            r = route_result(state)
            assert r["alert_created"] is True

    def test_route_no_alert_low_risk(self):
        from app.agents.onboarding_agent import route_result
        state = {"patient_id":"P002","risk_score":3,"risk_level":"LOW","key_findings":["Stable"],
            "recommendations":["Monitor"],"demographics":{"first_name":"Jane","last_name":"Smith"},
            "labs":[],"medications":[],"alert_created":False,"summary":"","next_steps":[],"errors":[]}
        r = route_result(state)
        assert r["alert_created"] is False

    def test_summary_contains_info(self):
        from app.agents.onboarding_agent import route_result
        state = {"patient_id":"P001","risk_score":7,"risk_level":"HIGH","key_findings":["eGFR low"],
            "recommendations":["Review"],"demographics":{"first_name":"John","last_name":"Doe"},
            "labs":[{"t":1}],"medications":[{"m":1}],"alert_created":False,"summary":"","next_steps":[],"errors":[]}
        with patch("app.agents.onboarding_agent.create_patient_alert") as m:
            m.invoke.return_value = json.dumps({"status":"created"})
            r = route_result(state)
            assert "John Doe" in r["summary"]
            assert "7/10" in r["summary"]


class TestDeterministicScoring:
    def test_scoring_critical_path(self):
        from app.agents.scoring import score_patient_risk
        result = score_patient_risk(
            demographics={"primary_condition": "ckd", "date_of_birth": "1945-01-01"},
            labs=[
                {"test_name": "eGFR", "value": 22},
                {"test_name": "Potassium", "value": 5.8},
                {"test_name": "Phosphorus", "value": 5.2},
                {"test_name": "Creatinine", "value": 3.1},
            ],
            medications=[{"drug_name": "Lisinopril"}],
            guidelines=[{"source": "CKD guideline"}],
        )
        assert result["risk_score"] >= 9
        assert result["risk_level"] == "CRITICAL"
        assert result["scoring_policy_version"] == "healthmap-v1"

    def test_scoring_low_path(self):
        from app.agents.scoring import score_patient_risk
        result = score_patient_risk(
            demographics={"primary_condition": "diabetes", "date_of_birth": "1990-01-01"},
            labs=[
                {"test_name": "eGFR", "value": 72},
                {"test_name": "Potassium", "value": 4.2},
            ],
            medications=[{"drug_name": "Metformin"}],
            guidelines=[{"source": "DM guideline"}],
        )
        assert 1 <= result["risk_score"] <= 3
        assert result["risk_level"] == "LOW"

    def test_scoring_missing_data_gaps(self):
        from app.agents.scoring import score_patient_risk
        result = score_patient_risk(
            demographics={"primary_condition": "ckd"},
            labs=[],
            medications=[],
            guidelines=[],
        )
        assert "Missing eGFR" in result["data_gaps"]
        assert "Missing potassium" in result["data_gaps"]
        assert "No guideline snippets retrieved" in result["data_gaps"]

class TestRAGPipeline:
    def test_chunk_creates_chunks(self):
        from app.rag.ingestion import chunk_document
        chunks = chunk_document("Test sentence. " * 200, "d1", "Test", "test")
        assert len(chunks) >= 1
        assert all("id" in c and "metadata" in c for c in chunks)

    def test_chunk_metadata(self):
        from app.rag.ingestion import chunk_document
        chunks = chunk_document("Content. " * 100, "d1", "CKD Protocol", "CKD")
        assert chunks[0]["metadata"]["condition"] == "ckd"
        assert chunks[0]["metadata"]["chunk_index"] == 0

    def test_token_count(self):
        from app.rag.ingestion import chunk_document
        chunks = chunk_document("Hello world. " * 500, "t", "T", "t")
        for c in chunks:
            assert 0 < c["metadata"]["token_count"] <= 600

    def test_multiple_chunks_created(self):
        from app.rag.ingestion import chunk_document
        chunks = chunk_document("Word " * 3000, "t", "T", "t")
        assert len(chunks) >= 2

class TestMCPServers:
    def test_register_tool(self):
        from app.mcp.servers import MCPServer
        s = MCPServer(name="test", description="Test")
        s.register_tool("t1", "Tool 1", lambda: None, {}, {})
        assert len(s.list_tools()) == 1

    def test_manifest(self):
        from app.mcp.servers import MCPServer
        s = MCPServer(name="my-server", description="Desc", version="2.0")
        m = s.to_manifest()
        assert m["name"] == "my-server" and m["version"] == "2.0"

    @pytest.mark.asyncio
    async def test_invoke_success(self):
        from app.mcp.servers import MCPServer
        s = MCPServer(name="test", description="Test")
        s.register_tool("greet", "Greet", lambda name: f"Hello {name}", {}, {})
        r = await s.invoke("greet", {"name": "World"})
        assert r["status"] == "success" and r["result"] == "Hello World"

    @pytest.mark.asyncio
    async def test_invoke_unknown(self):
        from app.mcp.servers import MCPServer
        s = MCPServer(name="test", description="Test")
        r = await s.invoke("nope", {})
        assert "error" in r

    def test_registry(self):
        from app.mcp.servers import MCPRegistry, MCPServer
        reg = MCPRegistry()
        s1 = MCPServer(name="s1", description="S1")
        s1.register_tool("t1", "T1", lambda: None, {}, {})
        s2 = MCPServer(name="s2", description="S2")
        s2.register_tool("t2", "T2", lambda: None, {}, {})
        reg.register(s1); reg.register(s2)
        assert len(reg.list_all_tools()) == 2

class TestEvalFramework:
    def test_correctness_in_range(self):
        from app.evals.eval_runner import score_correctness
        assert score_correctness(8, (7, 10)) == 1.0

    def test_correctness_out(self):
        from app.evals.eval_runner import score_correctness
        assert score_correctness(3, (7, 10)) < 1.0

    def test_correctness_boundary(self):
        from app.evals.eval_runner import score_correctness
        assert score_correctness(7, (7, 10)) == 1.0

    def test_completeness_all(self):
        from app.evals.eval_runner import score_completeness
        assert score_completeness("eGFR potassium nephrology", ["eGFR","potassium","nephrology"]) == 1.0

    def test_completeness_partial(self):
        from app.evals.eval_runner import score_completeness
        s = score_completeness("eGFR only", ["eGFR","potassium","nephrology"])
        assert 0.3 <= s <= 0.4

    def test_completeness_empty(self):
        from app.evals.eval_runner import score_completeness
        assert score_completeness("x", []) == 1.0

    def test_hallucination_yes(self):
        from app.evals.eval_runner import detect_hallucination
        assert detect_hallucination("diabetes insulin", ["diabetes","insulin"]) is True

    def test_hallucination_no(self):
        from app.evals.eval_runner import detect_hallucination
        assert detect_hallucination("CKD kidney", ["diabetes","insulin"]) is False

    def test_format_pass(self):
        from app.evals.eval_runner import validate_format
        assert validate_format({"risk_score":7,"risk_level":"HIGH","key_findings":[],"recommendations":[]}) is True

    def test_format_fail(self):
        from app.evals.eval_runner import validate_format
        assert validate_format({"risk_score":7}) is False

    def test_run_all_mock(self):
        from app.evals.eval_runner import run_all_evals
        report = run_all_evals()
        assert report["summary"]["total_scenarios"] == 5

    def test_threshold_met(self):
        from app.evals.eval_runner import run_all_evals
        assert run_all_evals(accuracy_threshold=0.0)["summary"]["meets_threshold"] is True

class TestModels:
    def test_onboarding_request(self):
        from app.models.schemas import OnboardingRequest
        assert OnboardingRequest(patient_id="P001", coordinator_id="C001").patient_id == "P001"

    def test_risk_result(self):
        from app.models.schemas import RiskAssessmentResult, RiskLevel
        r = RiskAssessmentResult(patient_id="P001",overall_risk_score=8,risk_level=RiskLevel.HIGH,condition_assessments=[],key_findings=["x"],recommendations=["y"])
        assert r.overall_risk_score == 8

    def test_risk_range(self):
        from app.models.schemas import RiskAssessmentResult, RiskLevel
        with pytest.raises(Exception):
            RiskAssessmentResult(patient_id="P001",overall_risk_score=15,risk_level=RiskLevel.HIGH,condition_assessments=[],key_findings=[],recommendations=[])

class TestAPI:
    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200 and r.json()["status"] == "healthy"

    def test_mcp_servers(self, client):
        assert client.get("/api/v1/mcp/servers").status_code == 200

    def test_mcp_tools(self, client):
        assert client.get("/api/v1/mcp/tools").status_code == 200
