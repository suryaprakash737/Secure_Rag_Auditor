# Secure RAG Auditor

An AI-powered security log analysis system with prompt injection defense and clearance-based access control.

## What it does

- Ingests security logs into a vector database with metadata
- Retrieves logs based on user clearance level
- Detects and blocks prompt injection attacks before they reach the LLM
- Generates structured security summaries using Groq LLM
- Records every query in a tamper-evident audit ledger

## Architecture

User Query → Prompt Injection Check → ChromaDB Retrieval → Groq LLM → Structured Response
                                            ↑
                                   Clearance Level Filter

## Security Features

- Prompt injection detection covering 4 attack categories:
  - Instruction override
  - Persona hijack
  - Prompt extraction
  - Jailbreak attempts
- Clearance-based access control — users only see logs within their security level
- Full audit trail of every query including blocked attempts
- LLM response validation against a risk level whitelist

## Tech Stack

- FastAPI
- ChromaDB
- Groq LLM (Llama 3.1)
- SQLite
- Pydantic
- Python

## Live Demo

Base URL: https://secure-rag-auditor.onrender.com

Interactive docs: https://secure-rag-auditor.onrender.com/docs

## API Endpoints

### POST /ingest
Stores a security log into ChromaDB.

```json
{
  "content": "Failed login attempt from IP 192.168.1.105 on port 22",
  "source_device": "firewall-01",
  "security_level": 2
}
```

### POST /search
Queries the system and returns a structured security analysis.

```json
{
  "query": "failed login attempts",
  "user_clearance": 2
}
```

## Setup

```bash
git clone https://github.com/suryaprakash737/Secure_Rag_Auditor
cd Secure_Rag_Auditor
python -m venv env
source env/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your GROQ_API_KEY to .env
uvicorn app.main:app --reload
```

## Environment Variables

```
GROQ_API_KEY=your-groq-api-key-here
```

## Docker

```bash
docker compose up --build
```

The API will be available at http://localhost:8000. Set `GROQ_API_KEY` and optionally `SECRET_KEY` in your environment before starting Compose.
