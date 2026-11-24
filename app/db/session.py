from collections.abc import Generator

from sqlmodel import Session, create_engine

from app.core.config import settings


# Serverless Postgres (e.g. Neon) drops idle connections and suspends compute,
# so check each pooled connection before use and recycle old ones.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
