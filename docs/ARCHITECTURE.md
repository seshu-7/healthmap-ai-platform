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
PDF Guidelines -> chunk (500 tokens, 50 overlap) -> embed (OpenAI ada-002) -> Pinecone
Query -> embed -> Pinecone search (with metadata filter) -> top-5 chunks -> inject into LLM prompt
```

## Security
- JWT auth at gateway level (downstream services trust gateway)
- HIPAA audit logging to Supabase
- Prompt sanitization before external LLM calls
- CI/CD security scan for secrets in prompt templates
