import os
import json
from openai import AsyncOpenAI

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    return _client

# Keep each retrieved chunk under this character limit to avoid blowing the context window.
# ~800 chars ≈ ~200 tokens, safe for 3 chunks inside a 4k-token prompt.
_MAX_CHARS_PER_DOC = 800
_MAX_TOTAL_CHARS = 3200

_VALID_RISK_LEVELS = {"Critical", "High", "Medium", "Low", "Safe"}

_SYSTEM_PROMPT = (
    "You are a Secure Intelligence Analyst. "
    "Your job is to read retrieved security log entries and produce a structured Security Summary Report. "
    "Rules:\n"
    "1. Draw conclusions ONLY from the provided log context — never fabricate details.\n"
    "2. Risk level must be exactly one of: Critical, High, Medium, Low, Safe.\n"
    "3. If the logs are insufficient to answer, state that explicitly in your summary.\n"
    "4. Be concise and precise — this is an operational environment."
)


def _build_log_context(docs: list, meta: list) -> str:
    parts = []
    total = 0
    for i, (doc, m) in enumerate(zip(docs, meta)):
        chunk = doc[:_MAX_CHARS_PER_DOC]
        entry = (
            f"[LOG {i + 1}] "
            f"Source: {m.get('source_device', 'unknown')} | "
            f"Clearance Level: {m.get('security_level', '?')}\n"
            f"{chunk}"
        )
        if total + len(entry) > _MAX_TOTAL_CHARS:
            break
        parts.append(entry)
        total += len(entry)
    return "\n\n".join(parts)


async def generate_security_summary(query: str, docs: list, meta: list) -> dict:
    """
    Calls GPT-4o-mini with the retrieved log context and returns a structured report dict.
    Falls back to a safe default if the LLM call fails.
    """
    log_context = _build_log_context(docs, meta)

    user_message = (
        f"ANALYST QUERY: {query}\n\n"
        f"RETRIEVED SECURITY LOGS ({len(docs)} document(s)):\n"
        f"{log_context}\n\n"
        "Respond with a JSON object using exactly these keys:\n"
        "{\n"
        '  "summary": "2-3 sentence operational answer to the query",\n'
        '  "risk_level": "Critical | High | Medium | Low | Safe",\n'
        '  "key_findings": ["finding 1", "finding 2"],\n'
        '  "recommendation": "one clear action item"\n'
        "}"
    )

    try:
        response = await _get_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=512,
        )
        result = json.loads(response.choices[0].message.content)

        # Normalise risk_level in case the LLM drifts from the allowed set
        if result.get("risk_level") not in _VALID_RISK_LEVELS:
            result["risk_level"] = "Unknown"

        return result

    except Exception as exc:
        return {
            "summary": f"LLM analysis unavailable: {exc}",
            "risk_level": "Unknown",
            "key_findings": [],
            "recommendation": "Check OPENAI_API_KEY and retry.",
        }
