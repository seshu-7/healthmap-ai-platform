# Architecture Guide

## System Layers

| Layer | Tech | Owner |
|-------|------|-------|
| React Frontend | ReactJS, TypeScript, Chart.js | Frontend devs (you added AI components) |
| Nest.js Gateway | Nest.js, TypeScript, GraphQL | YOU built this |
| Python AI Agents | LangChain, LangGraph, CrewAI | YOU — primary owner |
| Spring Boot Backend | Java 17, Spring Boot | Tech Lead + mid-level devs (existing) |
| Pinecone Vector DB | Pinecone managed service | YOU set up and managed |
| Supabase Audit Logs | Supabase (pgvector) | YOU set up |
| AWS EKS | Docker, K8s, Terraform | DevOps engineer (you wrote Dockerfiles) |

## Agent Types

- **LangChain Agent (ReAct)**: Single agent + tools. Think-Act-Observe loop.
- **LangGraph (StateGraph)**: Multi-step workflow with conditional branching. Used for patient onboarding.
- **CrewAI Crew**: Multiple specialized agents collaborating sequentially. Used for complex multi-condition assessment.

## RAG Pipeline

```
PDF Guidelines -> chunk (500 tokens, 50 overlap) -> embed (gemini-embedding-001, 3072-dim) -> Pinecone
Query -> embed -> Pinecone search (with metadata filter) -> top-5 chunks -> inject into LLM prompt
```

## Risk Scoring System (healthmap-v1)

The platform uses a **deterministic, versioned risk scoring policy** separate from LLM narrative generation.

### Architecture
```
Patient Data (demographics, labs, medications)
         ↓
   Deterministic Scoring Engine (scoring.py)
         ↓
   Risk Score (1-10) + Risk Level (LOW/MODERATE/HIGH/CRITICAL)
   Scoring Factors (audit trail) + Data Gaps
         ↓
   LLM Enrichment (Gemini) — Narrative ONLY
         ↓
   Key Findings + Recommendations (clinically grounded)
```

### Key Components

**1. Scoring Policy Module** (`app/agents/scoring.py`)
- **Function**: `score_patient_risk(demographics, labs, medications, guidelines) → dict`
- **Version**: `healthmap-v1` (versioned for audit/compliance)
- **Returns**:
  - `risk_score`: Integer 1-10 (deterministic)
  - `risk_level`: Enum (LOW/MODERATE/HIGH/CRITICAL)
  - `scoring_factors`: List of applied rules (audit trail)
  - `scoring_policy_version`: Policy version used
  - `condition_assessments`: Per-condition breakdowns
  - `data_gaps`: Missing data that could change score
  - `key_findings`: LLM-enriched narrative
  - `recommendations`: LLM-enriched action items

**2. Lab-Based Scoring Rules**
```
eGFR ≤15 (CKD Stage 5D):        +4 points (CRITICAL)
eGFR ≤30 (CKD Stage 4):         +3 points (HIGH)
eGFR ≤45 (CKD Stage 3b):        +2 points (MODERATE)

Potassium ≥6.0 mEq/L:           +4 points (CRITICAL)
Potassium ≥5.5 mEq/L:           +3 points (HIGH)

Phosphorus >4.5 mg/dL:          +1 point
Hemoglobin <10 g/dL:            +1 point
Creatinine ≥3.0 mg/dL:          +1 point

RAAS medication + Hyperkalemia:  +1 point
Age ≥75 years:                   +1 point
```

**3. Score Mapping**
- Score 1-3: **LOW** risk
- Score 4-6: **MODERATE** risk
- Score 7-8: **HIGH** risk
- Score 9-10: **CRITICAL** risk

**4. LLM Integration**
- **Purpose**: Narrative enrichment only (not scoring)
- **Constraint**: Prompt explicitly forbids changing `risk_score` or `risk_level`
- **Fallback**: If LLM fails, deterministic findings + recommendations retained
- **Model**: Google Gemini 2.5-flash

### Alert Routing
- **Threshold**: `risk_score ≥ 7` triggers alert creation
- **Alert Level**: Maps to risk_level (HIGH → URGENT, CRITICAL → CRITICAL)
- **Storage**: Patient service database with versioned scoring metadata

### Workflow Integration (LangGraph Onboarding Agent)
```
1. fetch_demographics     ↓
2. fetch_labs            ↓
3. fetch_medications     ↓
4. search_guidelines     ↓
5. assess_risk_DETERMINISTIC  ← NEW: score_patient_risk() called here
                         ↓
                    (LLM enriches narrative, risk_score immutable)
                         ↓
6. route_result    ← Creates alert if risk_score ≥ 7
```

---

## Security
- JWT auth at gateway level (downstream services trust gateway)
- HIPAA audit logging to Supabase
- Prompt sanitization before external LLM calls
- CI/CD security scan for secrets in prompt templates
