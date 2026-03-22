"""
LangChain tools for AI agents.
Each tool wraps an external data source or action.
Agents call these during the ReAct loop (Think -> Act -> Observe).
"""
import httpx
import json
import hashlib
from datetime import datetime
from typing import Optional
from langchain_core.tools import tool
from app.config import get_settings
from app.rag.retrieval import retrieve_guidelines

settings = get_settings()


@tool
def get_patient_demographics(patient_id: str) -> str:
    """Fetch patient demographics from the patient service.
    Returns: name, DOB, gender, conditions, insurance, coordinator.
    Use this when you need basic patient information."""
    try:
        resp = httpx.get(
            f"{settings.patient_service_url}/api/v1/patients/{patient_id}",
            timeout=10.0,
        )
        resp.raise_for_status()
        payload = resp.json()
        normalized = {
            "patient_id": payload.get("patientId", patient_id),
            "first_name": payload.get("firstName", ""),
            "last_name": payload.get("lastName", ""),
            "date_of_birth": payload.get("dateOfBirth"),
            "gender": payload.get("gender"),
            "primary_condition": payload.get("primaryCondition"),
            "conditions": payload.get("conditions", []),
            "insurance_plan": payload.get("insurancePlan"),
            "assigned_coordinator": payload.get("assignedCoordinator"),
        }
        return json.dumps(normalized, indent=2)
    except httpx.HTTPStatusError as e:
        return json.dumps({"error": f"Patient not found: {e.response.status_code}"})
    except httpx.ConnectError:
        return json.dumps({"error": "Patient service unavailable"})


@tool
def get_patient_labs(patient_id: str, limit: int = 10) -> str:
    """Fetch recent lab results for a patient.
    Returns: test name, value, unit, reference range, abnormal flag, date.
    Use this to assess a patient's recent lab trends."""
    try:
        resp = httpx.get(
            f"{settings.lab_service_url}/api/v1/labs/{patient_id}",
            params={"limit": limit, "sort": "collected_date:desc"},
            timeout=10.0,
        )
        resp.raise_for_status()
        return json.dumps(resp.json(), indent=2)
    except httpx.HTTPStatusError as e:
        return json.dumps({"error": f"Labs not found: {e.response.status_code}"})
    except httpx.ConnectError:
        return json.dumps({"error": "Lab service unavailable"})


@tool
def get_patient_medications(patient_id: str) -> str:
    """Fetch active medications for a patient.
    Returns: drug name, dosage, frequency, prescriber, start date.
    Use this to check current medications or drug interactions."""
    try:
        resp = httpx.get(
            f"{settings.medication_service_url}/api/v1/medications/{patient_id}",
            params={"active_only": True},
            timeout=10.0,
        )
        resp.raise_for_status()
        return json.dumps(resp.json(), indent=2)
    except httpx.HTTPStatusError as e:
        return json.dumps({"error": f"Medications not found: {e.response.status_code}"})
    except httpx.ConnectError:
        return json.dumps({"error": "Medication service unavailable"})


@tool
def search_clinical_guidelines(query: str, condition: Optional[str] = None) -> str:
    """Search clinical guidelines using RAG (Pinecone vector search).
    Returns relevant guideline excerpts with similarity scores.
    Use this when you need clinical protocols for a condition.
    Args:
        query: The clinical question or topic.
        condition: Optional filter (e.g., 'CKD', 'diabetes')."""
    try:
        results = retrieve_guidelines(
            query=query,
            condition_filter=condition,
            top_k=settings.retrieval_top_k,
        )
    except Exception:
        # Guideline search is optional for onboarding; fail soft and continue deterministic scoring.
        return json.dumps({"message": "Guidelines temporarily unavailable."})
    if not results:
        return json.dumps({"message": "No relevant guidelines found."})
    formatted = []
    for r in results:
        formatted.append({
            "content": r.content,
            "source": r.metadata.get("document_title", "Unknown"),
            "condition": r.metadata.get("condition", "General"),
            "relevance_score": round(r.score, 3),
        })
    return json.dumps(formatted, indent=2)


@tool
def create_patient_alert(
    patient_id: str, priority: str, title: str,
    description: str, recommended_action: str,
) -> str:
    """Create a clinical alert for a care coordinator.
    Use when risk assessment indicates HIGH or CRITICAL risk.
    Args:
        patient_id: The patient ID.
        priority: ROUTINE, URGENT, or CRITICAL.
        title: Short alert title.
        description: Detailed alert description.
        recommended_action: What the coordinator should do."""
    alert = {
        "alertId": hashlib.md5(
            f"{patient_id}-{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:12],
        "patientId": patient_id,
        "priority": priority,
        "title": title,
        "description": description,
        "recommendedAction": recommended_action,
        "status": "OPEN",
        "createdAt": datetime.utcnow().isoformat(),
    }
    try:
        resp = httpx.post(
            f"{settings.patient_service_url}/api/v1/alerts",
            json=alert, timeout=10.0,
        )
        resp.raise_for_status()
        return json.dumps({"status": "created", "alert": alert})
    except Exception as e:
        return json.dumps({"status": "failed", "error": str(e)})


@tool
def log_agent_action(request_id: str, patient_id: str, action: str, details: str) -> str:
    """Log an agent action for HIPAA audit compliance."""
    entry = {
        "request_id": request_id,
        "patient_id": patient_id,
        "action": action,
        "details": details,
        "timestamp": datetime.utcnow().isoformat(),
    }
    return json.dumps({"status": "logged", "entry": entry})


# Tool registries for different agent types
ALL_TOOLS = [
    get_patient_demographics, get_patient_labs, get_patient_medications,
    search_clinical_guidelines, create_patient_alert, log_agent_action,
]
ONBOARDING_TOOLS = [
    get_patient_demographics, get_patient_labs, get_patient_medications,
    search_clinical_guidelines, create_patient_alert,
]
RISK_ASSESSMENT_TOOLS = [
    get_patient_labs, get_patient_medications, search_clinical_guidelines,
]
