import os


DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://postgres:postgres@localhost:5432/secure_rag_auditor"
)
DEFAULT_SECRET_KEY = "dev-secret-key-change-me"


def _env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _normalize_database_url(url: str) -> str:
    """Hosted Postgres providers (e.g. Render) hand out postgres:// or
    postgresql:// URLs. SQLAlchemy rejects postgres:// and maps postgresql://
    to psycopg2, which isn't installed — force the psycopg (v3) driver."""
    url = url.strip()
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


class Settings:
    def __init__(self) -> None:
        self.DATABASE_URL = _normalize_database_url(
            os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
        )
        self.SECRET_KEY = os.getenv("SECRET_KEY", DEFAULT_SECRET_KEY)
        self.APP_ENV = os.getenv("APP_ENV", os.getenv("ENV", "development")).lower()
        self.ENABLE_DEMO = _env_flag("ENABLE_DEMO", self.APP_ENV != "production")
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30

        if self.APP_ENV == "production" and self.SECRET_KEY == DEFAULT_SECRET_KEY:
            raise RuntimeError("SECRET_KEY must be set to a non-default value in production")


settings = Settings()
