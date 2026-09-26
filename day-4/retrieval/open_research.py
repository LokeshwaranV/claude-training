"""Open-research (ungrounded) answering mode — SKILLS.md commitment 6.

Deliberately separate from `retrieval/answer.py`'s grounded query path: no
retrieval, no allowlist filter, no citations. Must be explicitly requested
by the caller (a mode switch), never triggered as a fallback inside the
grounded path.
"""

from __future__ import annotations

import os

from retrieval import groq_client
from retrieval.schema import OpenResearchResponse
from retrieval.telemetry import record_open_research_request


def answer_open_research(question: str) -> OpenResearchResponse:
    if not groq_client.is_configured():
        raise RuntimeError(
            "Open research mode requires AGENTIC_RAG_GROQ_API_KEY to be set"
        )

    text = groq_client.synthesize_open_research(question)
    record_open_research_request()

    simulated = groq_client.is_simulated()
    if simulated:
        # DEMO/POC: honesty signal for the UI's "Answered by {model}" slot
        # — never claim a real model produced this text.
        model = "simulated"
        disclaimer = (
            OpenResearchResponse.model_fields["disclaimer"].default
            + " (SIMULATED — no live model configured.)"
        )
        return OpenResearchResponse(answer=text, model=model, disclaimer=disclaimer)

    return OpenResearchResponse(
        answer=text,
        model=os.environ.get("AGENTIC_RAG_GROQ_MODEL", "llama-3.3-70b-versatile"),
    )
