import os
import json
from groq import Groq

_client = None

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
    try:
        response = _get_client().chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": _SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            temperature=0.1,
            max_tokens=512
        )

        text = response.choices[0].message.content.strip()

        if "```" in text:
            text = text.split("```")[1]

            if text.startswith("json"):
                text = text[4:].strip()

        result = json.loads(text)

        if result.get("risk_level") not in _VALID_RISK_LEVELS:
            result["risk_level"] = "Unknown"

        return result

    except Exception as exc:
        return {
            "summary": f"LLM unavailable: {exc}",
            "risk_level": "Unknown",
            "key_findings": [],
            "recommendation": "Check GROQ_API_KEY and retry."
        }
