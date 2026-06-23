import os


DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://postgres:postgres@localhost:5432/secure_rag_auditor"
)
DEFAULT_SECRET_KEY = "dev-secret-key-change-me"


class Settings:
    def __init__(self) -> None:
        self.DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
        self.SECRET_KEY = os.getenv("SECRET_KEY", DEFAULT_SECRET_KEY)
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30


settings = Settings()
