# Secure RAG Auditor

An AI-powered security log analysis platform designed to securely analyze security events using Retrieval-Augmented Generation (RAG), prompt injection defense, role-based access control, threat intelligence enrichment, and audit logging.

Secure RAG Auditor demonstrates how modern AI systems can be deployed in security-sensitive environments while enforcing authentication, authorization, prompt safety, and complete auditability.

---

## Features

### AI-Powered Security Analysis

* Retrieves relevant security logs using ChromaDB vector search.
* Generates structured security summaries using Groq LLM (Llama 3.1).
* Produces actionable recommendations and risk assessments.

### Prompt Injection Defense

Detects and blocks malicious prompts before they reach the LLM.

Supported attack categories:

* Instruction Override
* Persona Hijacking
* Prompt Extraction
* Jailbreak Attempts

### Authentication & Authorization

* JWT Authentication
* Role-Based Access Control (RBAC)
* Server-side clearance enforcement
* Protected administrative endpoints

### Threat Intelligence Enrichment

* IP reputation enrichment
* Domain reputation enrichment
* File hash enrichment
* Security context added before LLM analysis

### LangGraph Incident Workflow

Multi-step incident analysis pipeline:

* Query Validation
* Security Log Retrieval
* Threat Intelligence Enrichment
* AI Analysis
* Response Validation

### Audit Logging

Every query is recorded in PostgreSQL with:

* Timestamp
* User Clearance
* Risk Level
* Log Count
* Blocked Status

### DevOps & Reliability

* Docker Compose
* PostgreSQL
* GitHub Actions CI
* Structured Logging
* Global Error Handling
* Automated Tests

---

# Architecture

```text
                        +-------------------+
                        |      User         |
                        +---------+---------+
                                  |
                                  v
                     +-----------------------+
                     | JWT Authentication    |
                     +-----------+-----------+
                                 |
                                 v
                     +-----------------------+
                     | RBAC Authorization    |
                     +-----------+-----------+
                                 |
                                 v
                     +-----------------------+
                     | Prompt Injection      |
                     | Detection             |
                     +-----------+-----------+
                                 |
                                 v
                     +-----------------------+
                     | ChromaDB Retrieval    |
                     +-----------+-----------+
                                 |
                                 v
                     +-----------------------+
                     | Threat Intelligence   |
                     | Enrichment            |
                     +-----------+-----------+
                                 |
                                 v
                     +-----------------------+
                     | LangGraph Workflow    |
                     +-----------+-----------+
                                 |
                                 v
                     +-----------------------+
                     | Groq LLM Analysis     |
                     +-----------+-----------+
                                 |
                                 v
                     +-----------------------+
                     | PostgreSQL Audit Log  |
                     +-----------------------+
```

---

# Security Features

## Prompt Injection Protection

The system blocks known prompt injection patterns before they reach the LLM.

Examples:

* "Ignore previous instructions"
* "Reveal your system prompt"
* "Enable developer mode"
* "Act as a different assistant"

Blocked requests are recorded in the audit log.

---

## Role-Based Access Control

### Analyst

* Search security logs
* View AI-generated analysis

### Admin

* Ingest security logs
* Access audit reporting APIs
* View system-wide statistics

---

## Clearance Enforcement

Users can only retrieve logs that match their authorized clearance level.

Clearance is derived from authenticated user records stored in PostgreSQL.

Client-provided clearance values are ignored.

---

# Threat Intelligence Enrichment

Before AI analysis, the platform identifies indicators such as:

* IP Addresses
* Domains
* File Hashes

Indicators are enriched using local threat intelligence data and passed into the analysis workflow.

Example:

```json
{
  "indicator": "192.168.1.105",
  "reputation": "malicious",
  "threat_type": "brute_force"
}
```

---

# LangGraph Incident Workflow

Secure RAG Auditor includes a multi-step incident response workflow.

Workflow stages:

```text
Validate Query
      ↓
Retrieve Logs
      ↓
Threat Intelligence Enrichment
      ↓
Generate Security Summary
      ↓
Validate Response
```

This design separates incident analysis into deterministic security stages rather than relying solely on a single LLM call.

---

# Tech Stack

## Backend

* FastAPI
* Python

## AI & Retrieval

* Groq LLM (Llama 3.1)
* ChromaDB
* LangGraph

## Database

* PostgreSQL
* SQLModel

## Security

* JWT Authentication
* RBAC
* Prompt Injection Detection

## DevOps

* Docker Compose
* GitHub Actions

## Testing

* Pytest

---

# API Endpoints

| Method | Endpoint               | Description                        |
| ------ | ---------------------- | ---------------------------------- |
| POST   | `/register`            | Register a new user                |
| POST   | `/login`               | Authenticate and obtain JWT        |
| POST   | `/ingest`              | Ingest security logs (Admin Only)  |
| POST   | `/search`              | Analyze security logs              |
| GET    | `/admin/stats`         | Audit statistics (Admin Only)      |
| GET    | `/admin/recent-audits` | Recent audit activity (Admin Only) |

---

# Local Development

## Clone Repository

```bash
git clone https://github.com/suryaprakash737/Secure_Rag_Auditor.git

cd Secure_Rag_Auditor
```

## Create Virtual Environment

### Windows

```powershell
python -m venv secureRag_Environment

.\secureRag_Environment\Scripts\Activate.ps1
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

```env
GROQ_API_KEY=your_groq_api_key

SECRET_KEY=your_secret_key

DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/secure_rag_auditor
```

---

# Run Locally

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000/docs
```

---

# Docker Deployment

Build and start the complete stack:

```bash
docker compose up --build
```

Services:

* FastAPI
* PostgreSQL
* ChromaDB Persistence

Open:

```text
http://localhost:8000/docs
```

---

# Testing

Run all tests:

```bash
pytest -q
```

Current Coverage:

```text
23 tests passing
```

Test categories:

* Prompt Injection Detection
* JWT Authentication
* RBAC Authorization
* Threat Intelligence
* LangGraph Workflow
* Admin Reporting

---

# CI/CD

GitHub Actions automatically:

* Installs dependencies
* Compiles application code
* Runs automated tests
* Validates Docker configuration
* Builds Docker image

Workflow:

```text
Push / Pull Request
          ↓
GitHub Actions
          ↓
Compile
          ↓
Test
          ↓
Docker Validation
          ↓
Build
```

---

# Screenshots

## Swagger UI

```text
docs/images/swagger-ui.png
```

## Admin Reporting

```text
docs/images/admin-stats.png
```

## GitHub Actions

```text
docs/images/github-actions.png
```

## Docker Deployment

```text
docs/images/docker-compose.png
```

---

# Interview Talking Points

### Why PostgreSQL?

SQLite was suitable for prototyping but lacked production-grade concurrency and scalability.

PostgreSQL provides:

* Better reliability
* Concurrent access
* Production-ready audit storage

### Why JWT Authentication?

Prevents anonymous access and enables user identity propagation across the system.

### Why RBAC?

Different users require different permissions.

Analysts should not ingest data or access audit telemetry.

### Why Threat Intelligence Enrichment?

Raw log retrieval alone lacks security context.

Enrichment adds reputation and threat classification before analysis.

### Why LangGraph?

Security investigations are multi-step workflows.

LangGraph enables deterministic orchestration rather than a single LLM call.

### Why Docker Compose?

Provides reproducible deployments and consistent local development environments.

---

# Future Improvements

* Real-time threat intelligence integrations
* SIEM integrations
* SOC dashboard UI
* Multi-tenant support
* Kubernetes deployment
* OpenTelemetry observability
* Automated incident response workflows

---

# Live Demo

https://secure-rag-auditor.onrender.com

Swagger Documentation:

https://secure-rag-auditor.onrender.com/docs

---

# Author

**Suryaprakash Uppalapati**

M.S. Computer Science
George Mason University
