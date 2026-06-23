import uuid

from fastapi import APIRouter, Depends

from app.api.dependencies.auth import require_role
from app.db.chroma import add_log_to_db
from app.models.user import User
from app.schemas.requests import LogIngest

router = APIRouter()


@router.post("/ingest")
def ingest_log(
    log: LogIngest,
    current_user: User = Depends(require_role(["admin"])),
):
    """Stores a log entry in ChromaDB with security-level metadata."""
    # Only admins can ingest new security logs.
    log_id = str(uuid.uuid4())
    metadata = {
        "source_device": log.source_device,
        "security_level": log.security_level,
    }
    add_log_to_db(log_id, log.content, metadata)
    return {"message": "Log Secured", "id": log_id}
