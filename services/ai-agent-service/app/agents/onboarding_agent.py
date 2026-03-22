"""Patient Onboarding Agent using LangGraph.
6-node StateGraph: fetch_demographics -> fetch_labs -> fetch_medications ->
search_guidelines -> assess_risk -> route_result (conditional alert)."""
import json, uuid, time
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import get_settings
from app.agents.scoring import score_patient_risk
from app.agents.tools import (
    get_patient_demographics, get_patient_labs,
    get_patient_medications, search_clinical_guidelines, create_patient_alert,
)

settings = get_settings()

class OnboardingState(TypedDict):
    patient_id: str
    request_id: str
    coordinator_id: str
    demographics: dict
    labs: list
    medications: list
    guidelines: list
    risk_score: int
    risk_level: str
    condition_assessments: list
    key_findings: list
    recommendations: list
    summary: str
    alert_created: bool
    next_steps: list
    errors: list
    scoring_factors: list
    scoring_policy_version: str
    processing_time_ms: int

def fetch_demographics(state: OnboardingState) -> OnboardingState:
    try:
        result = get_patient_demographics.invoke(state["patient_id"])
        data = json.loads(result)
        if "error" in data:
            state["errors"].append(f"Demographics: {data['error']}")
            state["demographics"] = {}
        else:
            state["demographics"] = data
    except Exception as e:
        state["errors"].append(f"Demographics failed: {str(e)}")
        state["demographics"] = {}
    return state

def fetch_labs(state: OnboardingState) -> OnboardingState:
    try:
        result = get_patient_labs.invoke(state["patient_id"])
        data = json.loads(result)
        if "error" in data:
            state["errors"].append(f"Labs: {data['error']}")
            state["labs"] = []
        else:
            state["labs"] = data if isinstance(data, list) else data.get("results", [])
    except Exception as e:
        state["errors"].append(f"Labs failed: {str(e)}")
        state["labs"] = []
    return state

def fetch_medications(state: OnboardingState) -> OnboardingState:
    try:
        result = get_patient_medications.invoke(state["patient_id"])
        data = json.loads(result)
        if "error" in data:
            state["errors"].append(f"Meds: {data['error']}")
            state["medications"] = []
        else:
            state["medications"] = data if isinstance(data, list) else data.get("medications", [])
    except Exception as e:
        state["errors"].append(f"Meds failed: {str(e)}")
        state["medications"] = []
    return state

def search_guidelines_node(state: OnboardingState) -> OnboardingState:
    try:
        primary = state.get("demographics", {}).get("primary_condition")
        conditions = state.get("demographics", {}).get("conditions", [])
        query = f"Care management guidelines for {primary}"
        if conditions:
            query += f" with comorbidities: {', '.join(conditions)}"
        result = search_clinical_guidelines.invoke({"query": query, "condition": primary})
        data = json.loads(result)
        state["guidelines"] = data if isinstance(data, list) else []
    except Exception as e:
        state["errors"].append(f"Guidelines failed: {str(e)}")
        state["guidelines"] = []
    return state

def assess_risk(state: OnboardingState) -> OnboardingState:
    deterministic = score_patient_risk(
        demographics=state.get("demographics", {}),
        labs=state.get("labs", []),
        medications=state.get("medications", []),
        guidelines=state.get("guidelines", []),
    )
    state["risk_score"] = deterministic["risk_score"]
    state["risk_level"] = deterministic["risk_level"]
    state["condition_assessments"] = deterministic["condition_assessments"]
    state["key_findings"] = deterministic["key_findings"]
    state["recommendations"] = deterministic["recommendations"]
    state["scoring_factors"] = deterministic["scoring_factors"]
    state["scoring_policy_version"] = deterministic["scoring_policy_version"]
    state["errors"].extend(deterministic.get("data_gaps", []))

    llm = ChatGoogleGenerativeAI(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        google_api_key=settings.google_api_key,
    )
    system_prompt = """You are a clinical documentation assistant.
The risk score and risk level are already computed by deterministic business rules.
NEVER change risk_score or risk_level.
Use only provided data and return JSON only:
{"key_findings": ["<concise finding with data>"], "recommendations": ["<action>"]}
Keep output concise and clinically grounded."""

    context = f"""## FIXED_RISK
{json.dumps({
    'risk_score': state.get('risk_score'),
    'risk_level': state.get('risk_level'),
    'scoring_policy_version': state.get('scoring_policy_version'),
    'scoring_factors': state.get('scoring_factors', []),
}, indent=2)}
## DEMOGRAPHICS
{json.dumps(state.get('demographics', {}), indent=2)}
## LABS
{json.dumps(state.get('labs', []), indent=2)}
## MEDICATIONS
{json.dumps(state.get('medications', []), indent=2)}
## GUIDELINES
{json.dumps(state.get('guidelines', []), indent=2)}"""

    try:
        resp = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Generate findings and recommendations only:\n{context}"),
        ])
        text = resp.content.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text.rsplit("```", 1)[0]
        narrative = json.loads(text)
        llm_findings = narrative.get("key_findings", [])
        llm_recommendations = narrative.get("recommendations", [])
        if llm_findings:
            state["key_findings"] = llm_findings
        if llm_recommendations:
            state["recommendations"] = llm_recommendations
    except json.JSONDecodeError:
        state["errors"].append("LLM narrative response not valid JSON; using deterministic findings")
    except Exception as e:
        state["errors"].append(f"Narrative generation failed: {str(e)}")
    return state

def route_result(state: OnboardingState) -> OnboardingState:
    risk = state.get("risk_score", 5)
    if risk >= 7:
        try:
            result = create_patient_alert.invoke({
                "patient_id": state["patient_id"],
                "priority": "CRITICAL" if risk >= 9 else "URGENT",
                "title": f"High-Risk Onboarding: Risk {risk}/10",
                "description": "; ".join(state.get("key_findings", ["Elevated risk"])),
                "recommended_action": "; ".join(state.get("recommendations", ["Review"])),
            })
            result_data = json.loads(result)
            if result_data.get("status") == "created":
                state["alert_created"] = True
            else:
                state["errors"].append(f"Alert failed: {result_data.get('error', 'unknown')}")
                state["alert_created"] = False
        except Exception as e:
            state["errors"].append(f"Alert failed: {str(e)}")
            state["alert_created"] = False
    else:
        state["alert_created"] = False
    demo = state.get("demographics", {})
    name = f"{demo.get('first_name', 'Unknown')} {demo.get('last_name', '')}"
    state["summary"] = (
        f"Patient {name} (ID: {state['patient_id']}) onboarded. "
        f"Risk: {state.get('risk_score','N/A')}/10 ({state.get('risk_level','N/A')}). "
        f"Scoring policy: {state.get('scoring_policy_version', 'unknown')}. "
        f"Findings: {'; '.join(state.get('key_findings',['None']))}. "
        f"Labs: {len(state.get('labs',[]))} results, Meds: {len(state.get('medications',[]))} active."
    )
    steps = []
    if risk >= 7:
        steps.append("URGENT: Review within 24 hours")
    steps.extend(state.get("recommendations", []))
    if state.get("errors"):
        steps.append(f"Data gaps: {'; '.join(state['errors'])}")
    steps.append("Schedule initial care plan review")
    state["next_steps"] = steps
    return state

def build_onboarding_graph():
    wf = StateGraph(OnboardingState)
    wf.add_node("fetch_demographics", fetch_demographics)
    wf.add_node("fetch_labs", fetch_labs)
    wf.add_node("fetch_medications", fetch_medications)
    wf.add_node("search_guidelines", search_guidelines_node)
    wf.add_node("assess_risk", assess_risk)
    wf.add_node("route_result", route_result)
    wf.set_entry_point("fetch_demographics")
    wf.add_edge("fetch_demographics", "fetch_labs")
    wf.add_edge("fetch_labs", "fetch_medications")
    wf.add_edge("fetch_medications", "search_guidelines")
    wf.add_edge("search_guidelines", "assess_risk")
    wf.add_edge("assess_risk", "route_result")
    wf.add_edge("route_result", END)
    return wf.compile()

_graph = None
def get_onboarding_graph():
    global _graph
    if _graph is None:
        _graph = build_onboarding_graph()
    return _graph

async def run_patient_onboarding(patient_id: str, coordinator_id: str) -> dict:
    start = time.time()
    request_id = str(uuid.uuid4())
    initial: OnboardingState = {
        "patient_id": patient_id, "request_id": request_id,
        "coordinator_id": coordinator_id, "demographics": {},
        "labs": [], "medications": [], "guidelines": [],
        "risk_score": 0, "risk_level": "", "condition_assessments": [],
        "key_findings": [], "recommendations": [], "summary": "",
        "alert_created": False, "next_steps": [], "errors": [],
        "scoring_factors": [], "scoring_policy_version": "",
        "processing_time_ms": 0,
    }
    graph = get_onboarding_graph()
    result = graph.invoke(initial)
    result["processing_time_ms"] = int((time.time() - start) * 1000)
    result["request_id"] = request_id
    return result
