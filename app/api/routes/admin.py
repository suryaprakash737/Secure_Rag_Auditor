from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlmodel import Session, select

from app.api.dependencies.auth import require_role
from app.db.session import get_session
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.admin import AdminStatsResponse, AuditLogResponse

router = APIRouter(prefix="/admin")


def _count_audits(session: Session, *conditions) -> int:
    statement = select(func.count(AuditLog.id))
    for condition in conditions:
        statement = statement.where(condition)
    return session.exec(statement).one()


@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(
    current_user: User = Depends(require_role(["admin"])),
    session: Session = Depends(get_session),
):
    total_queries = _count_audits(session)
    blocked_queries = _count_audits(session, AuditLog.was_blocked == True)

    return AdminStatsResponse(
        total_queries=total_queries,
        blocked_queries=blocked_queries,
        allowed_queries=total_queries - blocked_queries,
        critical_queries=_count_audits(session, AuditLog.risk_level == "Critical"),
        high_queries=_count_audits(session, AuditLog.risk_level == "High"),
        medium_queries=_count_audits(session, AuditLog.risk_level == "Medium"),
        low_queries=_count_audits(session, AuditLog.risk_level == "Low"),
    )


@router.get("/recent-audits", response_model=list[AuditLogResponse])
def get_recent_audits(
    limit: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(require_role(["admin"])),
    session: Session = Depends(get_session),
):
    statement = (
        select(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .limit(limit)
    )
    return session.exec(statement).all()
