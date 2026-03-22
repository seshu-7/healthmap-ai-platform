"""RAG Retrieval — queries Pinecone for semantically similar clinical guidelines."""
from dataclasses import dataclass
from typing import Optional
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import get_settings

settings = get_settings()

@dataclass
class RetrievalResult:
    chunk_id: str
    content: str
    score: float
    metadata: dict

def get_embedding(text: str) -> list[float]:
    embeddings = GoogleGenerativeAIEmbeddings(model=settings.embedding_model, google_api_key=settings.google_api_key)
    return embeddings.embed_query(text)

def retrieve_guidelines(query: str, condition_filter: Optional[str] = None, top_k: int = None) -> list[RetrievalResult]:
    """Search Pinecone for relevant clinical guidelines.
    Args:
        query: Clinical question to search for.
        condition_filter: Optional condition to filter by (e.g., 'ckd').
        top_k: Number of results.
    Returns: List of RetrievalResult sorted by relevance."""
    top_k = top_k or settings.retrieval_top_k
    query_embedding = get_embedding(query)
    from pinecone import Pinecone
    pc = Pinecone(api_key=settings.pinecone_api_key)
    index = pc.Index(settings.pinecone_index_name)
    query_params = {"vector": query_embedding, "top_k": top_k, "include_metadata": True}
    if condition_filter:
        query_params["filter"] = {"condition": {"$eq": condition_filter.lower()}}
    results = index.query(**query_params)
    retrieval_results = []
    for match in results.get("matches", []):
        retrieval_results.append(RetrievalResult(
            chunk_id=match["id"],
            content=match["metadata"].get("text", ""),
            score=match["score"],
            metadata={k: v for k, v in match["metadata"].items() if k != "text"},
        ))
    return retrieval_results

def retrieve_with_reranking(query: str, condition_filter: Optional[str] = None,
                            initial_k: int = 15, final_k: int = 5) -> list[RetrievalResult]:
    """Two-stage retrieval: broad fetch then rerank by relevance + metadata boost."""
    initial = retrieve_guidelines(query=query, condition_filter=condition_filter, top_k=initial_k)
    if len(initial) <= final_k:
        return initial
    scored = []
    for r in initial:
        s = r.score
        if condition_filter and r.metadata.get("condition", "").lower() == condition_filter.lower():
            s *= 1.1
        if r.metadata.get("document_type") == "guideline":
            s *= 1.05
        scored.append((s, r))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored[:final_k]]
