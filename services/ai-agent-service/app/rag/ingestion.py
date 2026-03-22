"""RAG Ingestion Pipeline: PDF -> chunk -> embed -> Pinecone."""
import hashlib, json, argparse
from typing import Optional
from pathlib import Path
import tiktoken
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import get_settings

settings = get_settings()

def _count_tokens(text: str) -> int:
    encoding = tiktoken.encoding_for_model("gpt-4")
    return len(encoding.encode(text))

def create_text_splitter(chunk_size=None, chunk_overlap=None):
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or settings.chunk_size,
        chunk_overlap=chunk_overlap or settings.chunk_overlap,
        length_function=_count_tokens,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

def chunk_document(text, document_id, document_title, condition, document_type="guideline"):
    splitter = create_text_splitter()
    chunks = splitter.split_text(text)
    result = []
    for i, chunk_text in enumerate(chunks):
        chunk_id = hashlib.md5(f"{document_id}-{i}".encode()).hexdigest()
        result.append({
            "id": chunk_id, "text": chunk_text,
            "metadata": {
                "document_id": document_id, "document_title": document_title,
                "condition": condition.lower(), "document_type": document_type,
                "chunk_index": i, "total_chunks": len(chunks),
                "token_count": _count_tokens(chunk_text),
            },
        })
    return result

def get_embeddings_model():
    return GoogleGenerativeAIEmbeddings(model=settings.embedding_model, google_api_key=settings.google_api_key)

def embed_chunks(chunks):
    model = get_embeddings_model()
    texts = [c["text"] for c in chunks]
    embeddings = model.embed_documents(texts)
    for chunk, emb in zip(chunks, embeddings):
        chunk["embedding"] = emb
    return chunks

def get_pinecone_index():
    from pinecone import Pinecone
    pc = Pinecone(api_key=settings.pinecone_api_key)
    return pc.Index(settings.pinecone_index_name)

def store_in_pinecone(chunks):
    index = get_pinecone_index()
    vectors = [{"id": c["id"], "values": c["embedding"], "metadata": {**c["metadata"], "text": c["text"]}} for c in chunks]
    batch_size = 100
    total = 0
    for i in range(0, len(vectors), batch_size):
        index.upsert(vectors=vectors[i:i+batch_size])
        total += len(vectors[i:i+batch_size])
    return total

def ingest_document(text, document_id, document_title, condition, document_type="guideline"):
    chunks = chunk_document(text, document_id, document_title, condition, document_type)
    chunks = embed_chunks(chunks)
    count = store_in_pinecone(chunks)
    return {
        "document_id": document_id, "document_title": document_title,
        "condition": condition, "chunks_created": len(chunks), "vectors_stored": count,
        "avg_chunk_tokens": sum(c["metadata"]["token_count"] for c in chunks) // max(len(chunks),1),
    }

def ingest_pdf(pdf_path, condition, document_type="guideline"):
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    text = "\n".join(page.extract_text() for page in reader.pages)
    doc_id = hashlib.md5(pdf_path.encode()).hexdigest()[:12]
    doc_title = Path(pdf_path).stem.replace("_", " ").replace("-", " ").title()
    return ingest_document(text, doc_id, doc_title, condition, document_type)

SAMPLE_GUIDELINES = [
    {"id": "ckd-001", "title": "CKD Stage 3-5 Care Management Protocol", "condition": "ckd",
     "text": """Chronic Kidney Disease Care Guidelines - Stage 3 to 5
1. MONITORING: eGFR every 3 months (Stage 3), monthly (Stage 4-5). uACR every 6 months. Serum potassium/phosphorus every 3 months. BP target < 130/80. Hemoglobin every 3 months.
2. MEDICATIONS: ACE/ARBs first-line for proteinuria. SGLT2 inhibitors for eGFR 20-45. Avoid NSAIDs. Phosphate binders when phosphorus > 4.5. ESAs when Hgb < 10.
3. RISK: HIGH = eGFR decline > 5/year or uACR > 300. MODERATE = eGFR decline 3-5/year. LOW = stable eGFR.
4. ESCALATION: eGFR < 15 = nephrology referral for dialysis planning. Potassium > 5.5 = urgent medication review. Uncontrolled BP on 3+ meds = specialist.
5. EDUCATION: Sodium < 2000 mg/day. Protein guidance by stage. Medication adherence. Self-monitoring BP."""},
    {"id": "diabetes-001", "title": "Type 2 Diabetes Care Management Protocol", "condition": "diabetes",
     "text": """Type 2 Diabetes Mellitus Care Guidelines
1. MONITORING: HbA1c every 3 months (not at goal) or 6 months (stable). Target < 7.0% most adults, < 8.0% elderly. Fasting glucose 80-130. Post-prandial < 180.
2. MEDICATIONS: Metformin first-line (unless eGFR < 30). SGLT2 second-line especially with CKD/HF. GLP-1 agonists for CVD/obesity. Insulin when HbA1c > 10%.
3. SCREENING: Annual eye exam, annual uACR+eGFR, annual foot exam, annual lipids.
4. RISK: HIGH = HbA1c > 9% or recurrent hypoglycemia. MODERATE = HbA1c 7-9%. LOW = HbA1c < 7%.
5. REFERRALS: Endocrinology if HbA1c > 9% despite dual therapy. Nutritionist at diagnosis. Podiatry every 6-12 months."""},
    {"id": "hf-001", "title": "Heart Failure Care Management Protocol", "condition": "heart_failure",
     "text": """Heart Failure Care Guidelines - NYHA Class I-IV
1. MONITORING: Daily weight (report > 3 lb/24h). BNP at diagnosis and changes. Echo at diagnosis. Renal function every 3 months on diuretics.
2. MEDICATIONS (GDMT): ACEi/ARB/ARNI for all HFrEF. Beta-blocker (carvedilol, metoprolol). MRA for EF <= 35%. SGLT2 for all HF. Loop diuretics for volume overload.
3. RISK: HIGH = NYHA III-IV, EF < 25%, frequent hospitalizations. MODERATE = NYHA II, EF 25-40%. LOW = NYHA I, EF > 40%.
4. ESCALATION: Weight gain > 3 lb/24h = diuretic adjustment. New dyspnea at rest = urgent eval. SBP < 90 = hold ACEi, urgent cardiology.
5. EDUCATION: Fluid 1.5-2L/day. Sodium < 2000 mg/day. Daily weight technique. Symptom recognition."""},
]

def load_sample_data():
    results = []
    for doc in SAMPLE_GUIDELINES:
        r = ingest_document(text=doc["text"], document_id=doc["id"],
                           document_title=doc["title"], condition=doc["condition"])
        results.append(r)
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest clinical guidelines into RAG")
    parser.add_argument("--pdf", help="Path to PDF file")
    parser.add_argument("--condition", help="Clinical condition")
    parser.add_argument("--sample-data", action="store_true", help="Load sample data")
    args = parser.parse_args()
    if args.sample_data:
        for r in load_sample_data():
            print(f"Ingested: {r['document_title']} -> {r['chunks_created']} chunks")
    elif args.pdf and args.condition:
        r = ingest_pdf(args.pdf, args.condition)
        print(f"Ingested: {r['document_title']} -> {r['chunks_created']} chunks")
    else:
        parser.print_help()
