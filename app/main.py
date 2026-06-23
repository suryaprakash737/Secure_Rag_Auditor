from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
import time
import uuid

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.requests import Request

from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.logs import router as logs_router
from app.api.routes.search import router as search_router
from app.core.logging import configure_logging, get_logger
from app.db.chroma import add_log_to_db, collection
from app.db.init_db import init_db

configure_logging()
logger = get_logger(__name__)

SEED_LOGS = [
    {
        "content": "Failed SSH login attempt from IP 192.168.1.105 on server prod-db-01. 47 attempts in 2 minutes.",
        "source_device": "prod-db-01",
        "security_level": 2
    },
    {
        "content": "Unauthorized access attempt to classified document store. User ID 3342 clearance level mismatch.",
        "source_device": "file-server-02",
        "security_level": 4
    },
    {
        "content": "Malware signature detected on endpoint DESKTOP-447. Process name: svchost_fake.exe attempting outbound connection.",
        "source_device": "DESKTOP-447",
        "security_level": 3
    },
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    if collection.count() == 0:
        for log in SEED_LOGS:
            log_id = str(uuid.uuid4())
            metadata = {
                "source_device": log["source_device"],
                "security_level": log["security_level"],
            }
            add_log_to_db(log_id, log["content"], metadata)
    yield

app = FastAPI(title="Secure RAG Auditor", lifespan=lifespan)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "%s %s %s %.2fms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception for %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(health_router)
app.include_router(logs_router)
app.include_router(search_router)
