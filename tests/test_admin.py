import pytest
from fastapi import HTTPException

from app.api.dependencies.auth import require_role
from app.api.routes.admin import get_admin_stats, get_recent_audits
from app.models.user import User


def _user_with_role(role: str) -> User:
    return User(
        username=f"{role}-user",
        hashed_password="hashed",
        role=role,
        clearance_level=1,
        is_active=True,
    )


def test_non_admin_denied():
    dependency = require_role(["admin"])

    with pytest.raises(HTTPException) as exc_info:
        dependency(_user_with_role("analyst"))

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Insufficient permissions"


def test_stats_endpoint_callable():
    assert callable(get_admin_stats)


def test_recent_audits_endpoint_callable():
    assert callable(get_recent_audits)
