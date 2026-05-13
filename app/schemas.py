from pydantic import BaseModel
from typing import List


class LogIngest(BaseModel):
    content: str
    source_device: str
    security_level: int


class QueryRequest(BaseModel):
    query: str
    user_clearance: int


class AuditResponse(BaseModel):
    answer: str
    key_findings: List[str]
    recommendation: str
    sources: List[dict]
    risk_level: str
    log_count: int
