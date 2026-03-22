"""Pydantic models for request/response schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AlertPriority(str, Enum):
    ROUTINE = "ROUTINE"
    URGENT = "URGENT"
    CRITICAL = "CRITICAL"

class AgentType(str, Enum):
    ONBOARDING = "onboarding"
    RISK_ASSESSMENT = "risk_assessment"
    CLINICAL_CREW = "clinical_crew"

class PatientDemographics(BaseModel):
    patient_id: str
    first_name: str
    last_name: str
    date_of_birth: str
    gender: str
    primary_condition: str
    conditions: list[str] = []
    insurance_plan: str = ""
    assigned_coordinator: str = ""

class LabResult(BaseModel):
    lab_id: str
    patient_id: str
    test_name: str
    value: float
    unit: str
    reference_range: str
    is_abnormal: bool
    collected_date: str

class Medication(BaseModel):
    medication_id: str
    patient_id: str
    drug_name: str
    dosage: str
    frequency: str
    prescriber: str
    start_date: str
    is_active: bool = True

class OnboardingRequest(BaseModel):
    patient_id: str
    coordinator_id: str
    notes: Optional[str] = None

class RiskAssessmentRequest(BaseModel):
    patient_id: str
    assessment_type: str = "comprehensive"
    include_recommendations: bool = True

class AgentResponse(BaseModel):
    request_id: str
    agent_type: AgentType
    patient_id: str
    status: str
    result: dict
    sources: list[str] = []
    confidence_score: float = Field(ge=0.0, le=1.0)
    processing_time_ms: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RiskAssessmentResult(BaseModel):
    patient_id: str
    overall_risk_score: int = Field(ge=1, le=10)
    risk_level: RiskLevel
    condition_assessments: list[dict]
    key_findings: list[str]
    recommendations: list[str]
    flags: list[str] = []
    sources_used: list[str] = []

class OnboardingResult(BaseModel):
    patient_id: str
    demographics_collected: bool
    labs_collected: bool
    medications_collected: bool
    guidelines_retrieved: bool
    risk_assessment: RiskAssessmentResult
    onboarding_summary: str
    next_steps: list[str]
    alert_created: bool = False
    alert_priority: Optional[AlertPriority] = None

class AgentAuditLog(BaseModel):
    log_id: str
    request_id: str
    agent_type: AgentType
    patient_id: str
    coordinator_id: str
    action: str
    tools_called: list[str]
    data_sources_accessed: list[str]
    prompt_hash: str
    response_summary: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    document_title: str
    content: str
    condition: str
    document_type: str
    page_number: int = 0
    token_count: int = 0

class RetrievalResult(BaseModel):
    chunk_id: str
    content: str
    score: float
    metadata: dict

class EvalScenario(BaseModel):
    scenario_id: str
    patient_data: dict
    expected_risk_range: tuple[int, int]
    must_mention: list[str]
    must_not_mention: list[str]
    expected_alert: bool

class EvalResult(BaseModel):
    scenario_id: str
    passed: bool
    correctness_score: float
    completeness_score: float
    hallucination_detected: bool
    format_valid: bool
    details: dict
