from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends
import uuid
from app.schemas import LogIngest, QueryRequest, AuditResponse
from app.database import add_log_to_db, secure_retrieval
from app.rag import generate_security_summary
from app.auditor import check_query
from app.ledger import log_search
from app.auth import get_clearance

app = FastAPI(title="Secure RAG Auditor")

@app.get("/")
def home():
    return {"status": "The Secure Vault is Online"}

@app.post("/ingest")
def ingest_log(log: LogIngest):
    """Stores a log entry in ChromaDB with security-level metadata."""
    log_id = str(uuid.uuid4())
    metadata = {
        "source_device": log.source_device,
        "security_level": log.security_level,
    }
    add_log_to_db(log_id, log.content, metadata)
    return {"message": "Log Secured", "id": log_id}

@app.post("/search", response_model=AuditResponse)
async def search_logs(
    request: QueryRequest,
    user_clearance: int = Depends(get_clearance)  # clearance from API key, not user input
):
    is_malicious, reason = check_query(request.query)
    if is_malicious:
        log_search(request.query, user_clearance, "Blocked", 0, True)
        raise HTTPException(status_code=400, detail=f"Query blocked: {reason}")

    raw_results = secure_retrieval(request.query, user_clearance)
    if not raw_results["documents"] or not raw_results["documents"][0]:
        log_search(request.query, user_clearance, "Safe", 0, False)
        return AuditResponse(
            answer="No logs found within your clearance level for this query.",
            key_findings=[],
            recommendation="Verify your clearance level or refine your query.",
            sources=[],
            risk_level="Safe",
            log_count=0,
        )

    docs = raw_results["documents"][0]
    meta = raw_results["metadatas"][0]
    llm_result = await generate_security_summary(request.query, docs, meta)
    risk_level = llm_result.get("risk_level", "Unknown")
    log_search(request.query, user_clearance, risk_level, len(docs), False)

    return AuditResponse(
        answer=llm_result.get("summary", "Analysis unavailable."),
        key_findings=llm_result.get("key_findings", []),
        recommendation=llm_result.get("recommendation", "No recommendation available."),
        sources=meta,
        risk_level=risk_level,
        log_count=len(docs),
    )