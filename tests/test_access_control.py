import pytest
from fastapi import HTTPException

from app.api.dependencies.auth import require_role
from app.models.user import User


def _user_with_role(role: str) -> User:
    return User(
        username=f"{role}-user",
        hashed_password="hashed",
        role=role,
        clearance_level=1,
        is_active=True,
    )


def test_require_role_accepts_admin():
    dependency = require_role(["admin"])
    admin_user = _user_with_role("admin")

    assert dependency(admin_user) is admin_user


def test_require_role_rejects_analyst():
    dependency = require_role(["admin"])
    analyst_user = _user_with_role("analyst")

    with pytest.raises(HTTPException) as exc_info:
        dependency(analyst_user)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Insufficient permissions"
