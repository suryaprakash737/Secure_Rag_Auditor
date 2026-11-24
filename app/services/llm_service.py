import asyncio
import json
import os

from groq import Groq

from app.core.logging import get_logger

logger = get_logger(__name__)

# Groq retires models over time; override with GROQ_MODEL instead of editing code.
DEFAULT_GROQ_MODEL = "openai/gpt-oss-20b"

_client = None


def _get_model() -> str:
    return os.environ.get("GROQ_MODEL", "").strip() or DEFAULT_GROQ_MODEL

def _get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    return _client

_MAX_CHARS_PER_DOC = 800
_MAX_TOTAL_CHARS = 3200
_VALID_RISK_LEVELS = {"Critical", "High", "Medium", "Low", "Safe"}

_SYSTEM_PROMPT = (
    "You are a Secure Intelligence Analyst. "
    "Your job is to read retrieved security log entries and produce a structured Security Summary Report. "
    "Rules:\n"
    "1. Draw conclusions ONLY from the provided log context — never fabricate details.\n"
    "2. Risk level must be exactly one of: Critical, High, Medium, Low, Safe.\n"
    "3. If the logs are insufficient to answer, state that explicitly.\n"
    "4. Be concise and precise."
)

def _build_log_context(docs, meta):
    parts = []
    total = 0
    for i, (doc, m) in enumerate(zip(docs, meta)):
        chunk = doc[:_MAX_CHARS_PER_DOC]
        entry = (
            f"[LOG {i+1}] "
            f"Source: {m.get('source_device', 'unknown')} | "
            f"Clearance: {m.get('security_level', '?')}\n{chunk}"
        )
        if total + len(entry) > _MAX_TOTAL_CHARS:
            break
        parts.append(entry)
        total += len(entry)
    return "\n\n".join(parts)

def _build_threat_intel_context(threat_intel_findings):
    if not threat_intel_findings:
        return ""

    lines = ["THREAT INTELLIGENCE FINDINGS:"]
    for finding in threat_intel_findings:
        lines.append(
            "- "
            f"Indicator: {finding['indicator']} | "
            f"Reputation: {finding['reputation']} | "
            f"Threat Type: {finding['threat_type']}"
        )
    return "\n".join(lines)

async def generate_security_summary(query, docs, meta, threat_intel_findings=None):
    log_context = _build_log_context(docs, meta)
    threat_intel_context = _build_threat_intel_context(threat_intel_findings)
    user_message = (
        f"ANALYST QUERY: {query}\n\n"
        f"RETRIEVED SECURITY LOGS ({len(docs)} documents):\n{log_context}\n\n"
        f"{threat_intel_context}\n\n"
        "Respond with JSON using exactly these keys:\n"
        '{"summary": "...", "risk_level": "Critical|High|Medium|Low|Safe", '
        '"key_findings": ["..."], "recommendation": "..."}'
    )
    model = _get_model()
    request_kwargs = {
        "model": model,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
        "response_format": {"type": "json_object"},
    }
    if model.startswith("openai/gpt-oss"):
        # Reasoning models: keep thinking short so the JSON answer fits the budget.
        request_kwargs["extra_body"] = {"reasoning_effort": "low"}

    try:
        # The Groq client is synchronous; run it off the event loop.
        response = await asyncio.to_thread(
            _get_client().chat.completions.create, **request_kwargs
        )

        text = (response.choices[0].message.content or "").strip()

        if "```" in text:
            text = text.split("```")[1]

            if text.startswith("json"):
                text = text[4:].strip()

        result = json.loads(text)

        if result.get("risk_level") not in _VALID_RISK_LEVELS:
            result["risk_level"] = "Unknown"

        return result

    except Exception:
        # Full details go to server logs only; never echo provider errors to clients.
        logger.exception("LLM summary failed (model=%s)", model)
        return {
            "summary": "AI analysis is temporarily unavailable. Retrieved logs and threat intelligence are shown below.",
            "risk_level": "Unknown",
            "key_findings": [],
            "recommendation": "Retry shortly. If this persists, check the server logs.",
        }
