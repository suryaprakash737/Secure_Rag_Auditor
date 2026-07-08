import pytest

from app.core.config import DEFAULT_SECRET_KEY, Settings


def test_local_development_allows_default_secret(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("ENV", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)

    settings = Settings()

    assert settings.SECRET_KEY == DEFAULT_SECRET_KEY
    assert settings.ENABLE_DEMO is True


def test_app_refuses_to_start_in_production_with_default_secret(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("ENV", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)

    with pytest.raises(RuntimeError, match="SECRET_KEY must be set"):
        Settings()
