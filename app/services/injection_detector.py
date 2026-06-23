import re

# Each tuple: (compiled pattern, human-readable label shown in the blocked response)
_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"ignore\s+(all\s+)?(the\s+)?previous\s+instructions?", re.I), "instruction override"),
    (re.compile(r"disregard\s+(all\s+)?(the\s+)?(previous|above)\s+instructions?", re.I), "instruction override"),
    (re.compile(r"forget\s+(all\s+)?(your|the)\s+(previous\s+)?instructions?", re.I), "instruction override"),
    (re.compile(r"override\s+(all\s+)?(your\s+)?(previous\s+)?instructions?", re.I), "instruction override"),
    (re.compile(r"do\s+not\s+follow\s+(your|the|any)\s+instructions?", re.I), "instruction override"),
    (re.compile(r"you\s+are\s+now\s+a(n)?\s+\w+", re.I), "persona hijack"),
    (re.compile(r"act\s+as\s+(a|an|the)\s+\w+", re.I), "persona hijack"),
    (re.compile(r"pretend\s+(you\s+are|to\s+be)", re.I), "persona hijack"),
    (re.compile(r"role[\s\-]?play\s+as", re.I), "persona hijack"),
    (re.compile(r"your\s+(real|true|actual|original)\s+(instructions?|prompt|system)", re.I), "prompt extraction"),
    (re.compile(r"reveal\s+(your|the)\s+(instructions?|system\s+prompt|prompt)", re.I), "prompt extraction"),
    (re.compile(r"what\s+(are|were)\s+your\s+(instructions?|prompt)", re.I), "prompt extraction"),
    (re.compile(r"print\s+(your|the)\s+(instructions?|system\s+prompt)", re.I), "prompt extraction"),
    (re.compile(r"(bypass|circumvent)\s+(your\s+)?(restrictions?|guidelines?|rules?|safety)", re.I), "restriction bypass"),
    (re.compile(r"jailbreak", re.I), "jailbreak attempt"),
    (re.compile(r"\bdan\s+mode\b", re.I), "jailbreak attempt"),
    (re.compile(r"developer\s+mode\s+(enabled|on|activate)", re.I), "jailbreak attempt"),
    (re.compile(r"new\s+(system\s+)?instructions?\s*:", re.I), "system prompt injection"),
    (re.compile(r"\[system\]|\[instructions?\]|\[prompt\]", re.I), "system prompt injection"),
]


def check_query(query: str) -> tuple[bool, str]:
    """
    Returns (is_malicious, reason).
    reason is an empty string when the query is clean.
    """
    for pattern, label in _PATTERNS:
        if pattern.search(query):
            return True, label
    return False, ""
