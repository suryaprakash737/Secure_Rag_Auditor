from datetime import datetime, timezone

from sqlmodel import Session

from app.db.session import engine
from app.models.audit_log import AuditLog


def log_search(
    query_text: str,
    user_clearance: int,
    risk_level: str,
    log_count: int,
    was_blocked: bool,
) -> None:
    """Write one audit row. Opens and closes its own session."""
    audit_log = AuditLog(
        timestamp=datetime.now(timezone.utc),
        query_text=query_text,
        user_clearance=user_clearance,
        risk_level=risk_level,
        log_count=log_count,
        was_blocked=was_blocked,
    )

    with Session(engine) as session:
        session.add(audit_log)
        session.commit()
