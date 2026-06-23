from datetime import datetime

from pydantic import BaseModel


class AdminStatsResponse(BaseModel):
    total_queries: int
    blocked_queries: int
    allowed_queries: int
    critical_queries: int
    high_queries: int
    medium_queries: int
    low_queries: int


class AuditLogResponse(BaseModel):
    id: int | None
    timestamp: datetime
    query_text: str
    user_clearance: int
    risk_level: str
    log_count: int
    was_blocked: bool
