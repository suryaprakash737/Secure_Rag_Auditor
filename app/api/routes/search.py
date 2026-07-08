from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies.auth import get_current_user
from app.db.chroma import secure_retrieval
from app.models.user import User
from app.schemas.requests import AuditResponse, QueryRequest
from app.services.audit_service import log_search
from app.services.injection_detector import check_query
from app.services.llm_service import generate_security_summary
from app.services.threat_intel_service import enrich_detected_ips

router = APIRouter()


def _is_authorized_metadata(metadata: dict, user_clearance: int) -> bool:
    try:
        return int(metadata.get("security_level")) <= user_clearance
    except (TypeError, ValueError):
        return False


def _filter_authorized_results(
    docs: list[str],
    meta: list[dict],
    user_clearance: int,
) -> tuple[list[str], list[dict]]:
    authorized_pairs = [
        (doc, metadata)
        for doc, metadata in zip(docs, meta)
        if _is_authorized_metadata(metadata, user_clearance)
    ]
    if not authorized_pairs:
        return [], []

    authorized_docs, authorized_meta = zip(*authorized_pairs)
    return list(authorized_docs), list(authorized_meta)


@router.post("/search", response_model=AuditResponse)
async def search_logs(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
):
    # Clearance is derived from authenticated user, not request body.
    user_clearance = current_user.clearance_level

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
    docs, meta = _filter_authorized_results(docs, meta, user_clearance)
    if not docs:
        log_search(request.query, user_clearance, "Safe", 0, False)
        return AuditResponse(
            answer="No logs found within your clearance level for this query.",
            key_findings=[],
            recommendation="Verify your clearance level or refine your query.",
            sources=[],
            risk_level="Safe",
            log_count=0,
        )

    threat_intel_findings = enrich_detected_ips(docs, meta)
    llm_result = await generate_security_summary(
        request.query,
        docs,
        meta,
        threat_intel_findings,
    )
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
