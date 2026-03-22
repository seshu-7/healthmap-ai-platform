"""Multi-Agent Clinical Assessment using CrewAI.
3 specialized agents: Data Gatherer -> Clinical Analyst -> Summary Writer."""
import json, uuid, time
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import get_settings
from app.agents.tools import (
    get_patient_demographics, get_patient_labs,
    get_patient_medications, search_clinical_guidelines, create_patient_alert,
)

settings = get_settings()

def _llm():
    return ChatGoogleGenerativeAI(model=settings.llm_model, temperature=settings.llm_temperature, google_api_key=settings.google_api_key)

def create_data_gatherer():
    return Agent(
        role="Clinical Data Gatherer",
        goal="Collect comprehensive patient data from all sources. Organize clearly. Flag missing data.",
        backstory="Meticulous healthcare data specialist. Never misses a data source.",
        tools=[get_patient_demographics, get_patient_labs, get_patient_medications, search_clinical_guidelines],
        llm=_llm(), verbose=True, allow_delegation=False,
    )

def create_clinical_analyst():
    return Agent(
        role="Clinical Risk Analyst",
        goal="Perform condition-by-condition analysis. Identify risk factors, trends, interactions.",
        backstory="Experienced in multi-morbidity risk assessment. Always cites specific data points.",
        llm=_llm(), verbose=True, allow_delegation=False,
    )

def create_summary_writer():
    return Agent(
        role="Clinical Summary Writer",
        goal="Transform analysis into clear, actionable coordinator summary under 200 words.",
        backstory="Writes summaries busy coordinators can read in 2 minutes. Prioritizes actionable info.",
        tools=[create_patient_alert],
        llm=_llm(), verbose=True, allow_delegation=False,
    )

def build_clinical_crew(patient_id: str) -> Crew:
    gatherer, analyst, writer = create_data_gatherer(), create_clinical_analyst(), create_summary_writer()
    t1 = Task(
        description=f"Gather ALL data for patient {patient_id}: demographics, labs, medications, guidelines per condition. Flag gaps.",
        expected_output="Structured patient data: Demographics, Labs (abnormal flagged), Meds, Guidelines, Gaps.",
        agent=gatherer,
    )
    t2 = Task(
        description="Analyze each condition: severity, trend, medication appropriateness. Assess cross-condition interactions. Assign risk score 1-10.",
        expected_output="Per-condition assessments, interactions, risk score with justification.",
        agent=analyst, context=[t1],
    )
    t3 = Task(
        description=f"Create coordinator summary for {patient_id}: risk level, top 3 findings, numbered actions. If risk >= 7, create CRITICAL alert.",
        expected_output="Concise summary: risk, findings, actions, follow-up. Alert if high risk.",
        agent=writer, context=[t1, t2],
    )
    return Crew(agents=[gatherer, analyst, writer], tasks=[t1, t2, t3], process=Process.sequential, verbose=True)

async def run_clinical_assessment(patient_id: str, coordinator_id: str) -> dict:
    start = time.time()
    request_id = str(uuid.uuid4())
    crew = build_clinical_crew(patient_id)
    result = crew.kickoff()
    return {
        "request_id": request_id, "patient_id": patient_id,
        "coordinator_id": coordinator_id, "agent_type": "clinical_crew",
        "result": str(result), "processing_time_ms": int((time.time() - start) * 1000),
    }
