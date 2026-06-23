import asyncio
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from app.db.chroma import secure_retrieval
from app.services.injection_detector import check_query
from app.services.llm_service import generate_security_summary
from app.services.threat_intel_service import enrich_detected_ips


_VALID_RISK_LEVELS = {"Critical", "High", "Medium", "Low", "Safe", "Blocked", "Unknown"}


class IncidentState(TypedDict, total=False):
    query: str
    clearance_level: int
    is_blocked: bool
    block_reason: str
    raw_results: dict
    docs: list[str]
    metadata: list[dict]
    threat_intel_findings: list[dict]
    summary: dict
    result: dict


def validate_query(state: IncidentState) -> IncidentState:
    is_malicious, reason = check_query(state["query"])
    if is_malicious:
        state["is_blocked"] = True
        state["block_reason"] = reason
        state["result"] = {
            "answer": f"Query blocked: {reason}",
            "key_findings": [],
            "recommendation": "Revise the query and avoid prompt injection patterns.",
            "sources": [],
            "risk_level": "Blocked",
            "log_count": 0,
            "was_blocked": True,
        }
    else:
        state["is_blocked"] = False
        state["block_reason"] = ""
    return state


def retrieve_logs(state: IncidentState) -> IncidentState:
    raw_results = secure_retrieval(state["query"], state["clearance_level"])
    state["raw_results"] = raw_results

    if not raw_results["documents"] or not raw_results["documents"][0]:
        state["docs"] = []
        state["metadata"] = []
        state["result"] = {
            "answer": "No logs found within your clearance level for this query.",
            "key_findings": [],
            "recommendation": "Verify your clearance level or refine your query.",
            "sources": [],
            "risk_level": "Safe",
            "log_count": 0,
            "was_blocked": False,
        }
        return state

    state["docs"] = raw_results["documents"][0]
    state["metadata"] = raw_results["metadatas"][0]
    return state


def enrich_threat_intel(state: IncidentState) -> IncidentState:
    state["threat_intel_findings"] = enrich_detected_ips(
        state.get("docs", []),
        state.get("metadata", []),
    )
    return state


def generate_summary(state: IncidentState) -> IncidentState:
    state["summary"] = asyncio.run(
        generate_security_summary(
            state["query"],
            state.get("docs", []),
            state.get("metadata", []),
            state.get("threat_intel_findings", []),
        )
    )
    return state


def validate_response(state: IncidentState) -> IncidentState:
    summary = state.get("summary", {})
    risk_level = summary.get("risk_level", "Unknown")
    if risk_level not in _VALID_RISK_LEVELS:
        risk_level = "Unknown"

    state["result"] = {
        "answer": summary.get("summary", "Analysis unavailable."),
        "key_findings": summary.get("key_findings", []),
        "recommendation": summary.get("recommendation", "No recommendation available."),
        "sources": state.get("metadata", []),
        "risk_level": risk_level,
        "log_count": len(state.get("docs", [])),
        "was_blocked": False,
        "threat_intel_findings": state.get("threat_intel_findings", []),
    }
    return state


def _route_after_validate(state: IncidentState) -> str:
    return "blocked" if state.get("is_blocked") else "retrieve"


def _route_after_retrieval(state: IncidentState) -> str:
    return "no_logs" if state.get("result") else "enrich"


def _build_workflow():
    workflow = StateGraph(IncidentState)
    workflow.add_node("validate_query", validate_query)
    workflow.add_node("retrieve_logs", retrieve_logs)
    workflow.add_node("enrich_threat_intel", enrich_threat_intel)
    workflow.add_node("generate_summary", generate_summary)
    workflow.add_node("validate_response", validate_response)

    workflow.add_edge(START, "validate_query")
    workflow.add_conditional_edges(
        "validate_query",
        _route_after_validate,
        {
            "blocked": END,
            "retrieve": "retrieve_logs",
        },
    )
    workflow.add_conditional_edges(
        "retrieve_logs",
        _route_after_retrieval,
        {
            "no_logs": END,
            "enrich": "enrich_threat_intel",
        },
    )
    workflow.add_edge("enrich_threat_intel", "generate_summary")
    workflow.add_edge("generate_summary", "validate_response")
    workflow.add_edge("validate_response", END)
    return workflow.compile()


incident_workflow = _build_workflow()


def analyze_incident(query: str, clearance_level: int) -> dict[str, Any]:
    final_state = incident_workflow.invoke(
        {
            "query": query,
            "clearance_level": clearance_level,
        }
    )
    return final_state["result"]
