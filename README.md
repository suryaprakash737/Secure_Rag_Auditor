# Secure RAG Auditor

Secure RAG Auditor is an AI-powered security log analysis platform built with FastAPI, PostgreSQL, ChromaDB, LangGraph, Docker, and Groq Llama 3.1.

It demonstrates how to build a security-sensitive RAG system with authentication, RBAC, prompt injection defense, clearance-aware retrieval, threat intelligence enrichment, incident workflow orchestration, audit logging, CI validation, and containerized deployment.

![CI](https://github.com/suryaprakash737/Secure_Rag_Auditor/actions/workflows/ci.yml/badge.svg)

## Project Overview

The platform lets authenticated users search security logs and receive structured incident summaries. The system blocks prompt injection attempts, retrieves logs according to server-side user clearance, enriches detected indicators with threat intelligence, and records every search in PostgreSQL for audit reporting.

Admins can ingest logs and view dashboard-ready reporting APIs backed by PostgreSQL audit data.

## Features

- AI-powered security log analysis using Groq Llama 3.1.
- ChromaDB-backed retrieval with security-level metadata filtering.
- JWT authentication and role-based access control.
- Prompt injection detection before retrieval or LLM analysis.
- PostgreSQL audit logging with SQLModel.
- Threat intelligence enrichment for IPs, domains, and file hashes.
- LangGraph-style incident analysis workflow.
- Admin reporting APIs and read-only dashboard.
- Docker Compose runtime with PostgreSQL.
- GitHub Actions CI with compile, test, Compose validation, and Docker build checks.
- Pytest coverage for authentication, RBAC, prompt defense, threat intel, workflow, and admin routes.

## Security Controls

### JWT Authentication

Users register and log in to receive bearer tokens. Protected routes use token validation to retrieve the current user from PostgreSQL.

### RBAC

Roles are enforced with reusable FastAPI dependencies.

- `analyst`: can search security logs.
- `admin`: can ingest logs and access admin reporting.

### Clearance-Aware Retrieval

The `/search` route ignores client-provided clearance values and uses `current_user.clearance_level` from PostgreSQL.

### Prompt Injection Defense

The system blocks known prompt injection patterns such as instruction override, persona hijacking, prompt extraction, and jailbreak attempts.

### Audit Logging

Search activity is written to PostgreSQL with timestamp, query, user clearance, risk level, log count, and blocked status.

## Architecture Diagram

![Secure RAG Auditor Architecture](static/architecture.svg)

```text
User Query
  -> JWT Authentication
  -> Prompt Injection Defense
  -> Clearance-Aware Retrieval
  -> Threat Intelligence Enrichment
  -> LangGraph Incident Workflow
  -> Groq LLM Analysis
  -> PostgreSQL Audit Logging
```

## Screenshots

Use these pages after starting the app:

- Landing page: `http://localhost:8000/`
- API docs: `http://localhost:8000/docs`
- Admin dashboard: `http://localhost:8000/admin/dashboard`
- Architecture asset: `http://localhost:8000/static/architecture.svg`

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Professional landing page |
| `GET` | `/health` | Health check |
| `POST` | `/register` | Register a user |
| `POST` | `/login` | Issue JWT bearer token |
| `POST` | `/search` | Authenticated security log analysis |
| `POST` | `/ingest` | Admin-only log ingestion |
| `GET` | `/admin/stats` | Admin-only audit metrics |
| `GET` | `/admin/recent-audits` | Admin-only recent audit records |
| `GET` | `/admin/dashboard` | Admin-only read-only dashboard |

## Authentication Flow

1. Register with `/register`.
2. Log in with `/login`.
3. Copy the returned `access_token`.
4. Use `Authorization: Bearer <token>` for protected endpoints.
5. The API decodes the JWT, reads the `sub` claim, loads the user from PostgreSQL, and verifies the user is active.

## RBAC Flow

1. Protected routes call `get_current_user()`.
2. Admin-only routes call `require_role(["admin"])`.
3. If the user role is not allowed, the API returns `403 Insufficient permissions`.
4. `/search` remains available to authenticated users and derives clearance from the database user record.

## Docker Setup

Set environment variables:

```bash
export GROQ_API_KEY=your_groq_api_key
export SECRET_KEY=change_this_secret
```

Start the stack:

```bash
docker compose up --build
```

Services:

- FastAPI app on `http://localhost:8000`
- PostgreSQL 16
- ChromaDB persistence mounted at `./chroma_db:/app/chroma_db`

## Local Development

```bash
python -m venv secureRag_Environment
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Required environment variables:

```env
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=change_this_secret
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/secure_rag_auditor
```

## CI/CD Pipeline

GitHub Actions runs on push and pull request:

- Checkout repository.
- Set up Python 3.11.
- Install dependencies.
- Compile the app with `python -m compileall app`.
- Run import smoke test.
- Run `pytest -q`.
- Validate Docker Compose.
- Build the Docker image.

## Testing

Run:

```bash
pytest -q
```

Current test coverage includes:

- Prompt injection detection.
- JWT creation and decoding.
- Password hashing and verification.
- RBAC role checks.
- Threat intelligence enrichment.
- LangGraph incident workflow.
- Admin route callability and access-control behavior.

## Deployment

The project is container-ready through Docker Compose. For hosted deployment, provide:

- `DATABASE_URL`
- `SECRET_KEY`
- `GROQ_API_KEY`
- Persistent storage for ChromaDB
- PostgreSQL-compatible database

## Engineering Achievements

- Migrated audit logging from SQLite to PostgreSQL using SQLModel.
- Implemented JWT authentication and RBAC.
- Containerized the platform with Docker Compose.
- Added GitHub Actions CI validation.
- Built a prompt injection detection engine.
- Added a LangGraph-based incident analysis workflow.
- Integrated a deterministic threat-intelligence enrichment pipeline.
- Added structured logging and global error handling.
- Added dashboard-ready admin reporting APIs.

## Interview Talking Points

### Why PostgreSQL replaced SQLite

SQLite was useful for early prototyping, but PostgreSQL is a better fit for production audit logging because it supports concurrent access, managed deployment, stronger operational tooling, and scalable reporting.

### Why JWT was added

JWT authentication gives the API a portable identity layer. It allows protected endpoints to consistently resolve the current user and enforce server-side access decisions.

### Why RBAC was added

Security platforms need separation of duties. Analysts can search logs, while admins can ingest logs and review audit telemetry.

### Why Docker Compose was added

Docker Compose makes the app reproducible by running FastAPI and PostgreSQL together with consistent environment configuration.

### Why GitHub Actions was added

CI validates the codebase automatically through dependency installation, compilation, tests, Docker Compose validation, and Docker image build checks.

### Why LangGraph was added

Security investigations are multi-step workflows. LangGraph provides a structured way to model validation, retrieval, enrichment, analysis, and response validation as separate stages.

### Why Threat Intelligence Enrichment was added

Raw log retrieval is not enough for security analysis. Enrichment adds indicator reputation and threat classification before the LLM produces a summary.

## Future Improvements

- External threat intelligence integrations.
- SIEM export support.
- More detailed SOC dashboard views.
- Alembic migrations.
- OpenTelemetry tracing.
- Cloud deployment manifests.
- Multi-tenant organization support.
- Human approval workflows for incident response.

## Live Demo

Base URL:

```text
https://secure-rag-auditor.onrender.com
```

Swagger docs:

```text
https://secure-rag-auditor.onrender.com/docs
```
