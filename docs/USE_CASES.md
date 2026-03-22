# Use Cases & Workflows

## UC1: Patient Onboarding (LangGraph)
Coordinator clicks "Onboard" -> Nest.js validates JWT -> Python LangGraph agent runs 6 nodes:
fetch_demographics -> fetch_labs -> fetch_medications -> search_guidelines (Pinecone RAG) -> assess_risk (LLM) -> route_result (alert if risk >= 7).
Time: 45 min manual -> ~10 sec AI + 2-5 min review.

## UC2: Complex Assessment (CrewAI)
For multi-morbidity patients (CKD + diabetes + HF). 3 agents:
Data Gatherer -> Clinical Analyst (condition-by-condition + interactions) -> Summary Writer (200-word actionable summary + alert).

## UC3: Guideline Search (RAG)
Coordinator asks clinical question -> embed query -> Pinecone search with condition metadata filter -> top-5 chunks returned with citations.

## UC4: Automated Alerts
Risk >= 9 = CRITICAL, 7-8 = URGENT. Agent auto-creates alert via create_patient_alert tool. Coordinator notified.

## UC5: AI Quality Monitoring (Evals)
5 test scenarios in CI/CD. Scores: correctness, completeness, hallucination, format. Blocks deployment if accuracy < 80%.

## UC6: MCP Tool Discovery
New data source = new MCP server file. Agents auto-discover tools. No agent code changes needed.
