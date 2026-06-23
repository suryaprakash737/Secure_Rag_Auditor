from sqlmodel import SQLModel

from app.db.session import engine
from app.models.audit_log import AuditLog
from app.models.user import User


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
