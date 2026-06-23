from datetime import datetime

from sqlmodel import Field, SQLModel


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_log"

    id: int | None = Field(default=None, primary_key=True)
    timestamp: datetime
    query_text: str
    user_clearance: int
    risk_level: str
    log_count: int
    was_blocked: bool
