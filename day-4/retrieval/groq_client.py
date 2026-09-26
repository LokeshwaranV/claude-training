"""Groq client wiring for the Agentic RAG backend (SKILLS.md commitment 6 +
grounded-answer upgrade).

`AGENTIC_RAG_GROQ_API_KEY` is read lazily (inside function bodies, never at
module import time) so this module can always be imported even when no key
is set — the app must never hard-fail just because Groq isn't configured
(graceful degradation to the existing extractive/refuse behavior).
"""

from __future__ import annotations

import os
import re

import groq

_ENV_KEY = "AGENTIC_RAG_GROQ_API_KEY"
_SIMULATE_ENV_KEY = "AGENTIC_RAG_GROQ_SIMULATE"


def is_simulated() -> bool:
    """Whether simulation mode is enabled via AGENTIC_RAG_GROQ_SIMULATE.

    DEMO/POC ONLY: this flag never causes a real Groq/LLM call. It exists so
    the Groq-backed grounded synthesis and Open Research mode can be
    demoed end-to-end in an environment with no real API key. Callers must
    remain honest about this — see `synthesize_grounded`/
    `synthesize_open_research` below and `retrieval/open_research.py`'s
    `model="simulated"` override.
    """
    return os.environ.get(_SIMULATE_ENV_KEY, "").lower() in ("1", "true", "yes")


def is_configured() -> bool:
    """Whether Groq is usable: either a real API key is present, or
    simulation mode is on. Callers gating on this naturally pick up
    simulation mode without checking both. `synthesize_grounded`/
    `synthesize_open_research` check `is_simulated()` themselves to branch
    into the (honest, non-LLM) simulated path before touching
    `get_client()`."""
    return bool(os.environ.get(_ENV_KEY)) or is_simulated()


def get_client() -> "groq.Groq":
    """Lazily build a Groq client from the environment. Raises RuntimeError
    (not at import time) if the key isn't set."""
    api_key = os.environ.get(_ENV_KEY)
    if not api_key:
        raise RuntimeError(f"{_ENV_KEY} not set")
    return groq.Groq(api_key=api_key)


def _model() -> str:
    return os.environ.get("AGENTIC_RAG_GROQ_MODEL", "llama-3.3-70b-versatile")


def _timeout_s() -> float:
    return float(os.environ.get("AGENTIC_RAG_GROQ_TIMEOUT_S", "8"))


def _split_sentences(text: str) -> list:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def _simulate_grounded(chunks: list) -> str:
    """DEMO/POC SIMULATION — not a real LLM call.

    Builds a "template synthesis" instead of calling Groq: splits each
    chunk's text into sentences, drops sentences that are exact duplicates
    (after whitespace-strip) of a sentence already kept from an earlier
    chunk, and appends the same bracket citation marker format the real
    prompt asks Groq to produce (`[i]` after each sentence, `i` being the
    1-based excerpt index) so `answer.py::_passes_grounding_check()` still
    passes unchanged. Every kept sentence gets a marker — none are left
    untagged, since that's exactly what the grounding check rejects.
    """
    seen = set()
    out_sentences = []
    for i, chunk in enumerate(chunks, start=1):
        for sentence in _split_sentences(chunk.text):
            key = sentence.strip().lower()
            if key in seen:
                continue
            seen.add(key)
            # _passes_grounding_check (answer.py) splits on `(?<=[.!?])\s+`,
            # i.e. right after the closing punctuation. A marker placed
            # *after* the punctuation ("sentence. [1]") lands in the next
            # split segment instead of this one, so the marker must go
            # *before* the trailing punctuation ("sentence [1].") to stay
            # attached to its own sentence.
            match = re.match(r"^(.*?)([.!?]+)$", sentence, re.DOTALL)
            if match:
                body, punct = match.group(1), match.group(2)
                out_sentences.append(f"{body} [{i}]{punct}")
            else:
                out_sentences.append(f"{sentence} [{i}].")
    if not out_sentences:
        # No sentences at all (e.g. empty chunk text) — still must satisfy
        # the grounding check, so fall back to a single tagged sentence
        # rather than emitting nothing.
        out_sentences = [
            "The provided excerpts did not contain any extractable "
            "sentences [1]."
        ]
    return " ".join(out_sentences)


def _simulate_open_research(question: str) -> str:
    """DEMO/POC SIMULATION — not a real LLM call, and does not fabricate
    any domain content. Returns a fixed, honest notice instead."""
    return (
        "This is a simulated Open Research response — no live Groq/LLM "
        "model is configured. A real model would attempt a detailed, "
        f'general-knowledge answer to: "{question}". Set '
        "AGENTIC_RAG_GROQ_API_KEY to enable real answers."
    )


def synthesize_grounded(question: str, chunks: list) -> str:
    """Synthesize a grounded answer from the given (already allowlist-
    filtered) chunks only. Instructs the model to cite the bracket index of
    every excerpt it draws a fact from, inline after the sentence, and to
    say plainly if the excerpts are insufficient. Exceptions propagate to
    the caller (retrieval/answer.py), which treats any failure as an
    escalation rather than falling back silently.

    In simulation mode (AGENTIC_RAG_GROQ_SIMULATE), no real Groq call is
    made at all — see `_simulate_grounded` above."""
    if is_simulated():
        return _simulate_grounded(chunks)

    client = get_client()

    excerpt_lines = []
    for i, chunk in enumerate(chunks, start=1):
        excerpt_lines.append(f"[{i}] (document_id={chunk.document_id}, chunk_id={chunk.chunk_id}): {chunk.text}")
    excerpts_block = "\n".join(excerpt_lines)

    system_prompt = (
        "You are a pharma literature assistant. Answer the user's question "
        "using ONLY the numbered excerpts provided below — do not use any "
        "outside knowledge. After every sentence that uses a fact from an "
        "excerpt, cite that excerpt's bracket index inline, e.g. '[1]'. If "
        "a sentence combines facts from multiple excerpts, cite all of "
        "them, e.g. '[1][2]'. If the excerpts are insufficient to answer "
        "the question, say so explicitly instead of guessing."
    )
    user_prompt = f"Excerpts:\n{excerpts_block}\n\nQuestion: {question}"

    response = client.chat.completions.create(
        model=_model(),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        timeout=_timeout_s(),
    )
    return response.choices[0].message.content


def synthesize_open_research(question: str) -> str:
    """Free-form, ungrounded answer from the model's general knowledge — no
    corpus/chunk context at all. Used only by the explicit open-research
    mode (SKILLS.md commitment 6), never as a fallback inside the grounded
    query path. Exceptions propagate to the caller.

    In simulation mode (AGENTIC_RAG_GROQ_SIMULATE), no real Groq call is
    made at all — see `_simulate_open_research` above."""
    if is_simulated():
        return _simulate_open_research(question)

    client = get_client()

    system_prompt = (
        "You are answering in 'open research' mode: general-knowledge "
        "mode with no access to any proprietary or curated corpus, no "
        "retrieval, and no citations. Answer from your own general "
        "training knowledge. Be clear about uncertainty where relevant."
    )

    response = client.chat.completions.create(
        model=_model(),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        timeout=_timeout_s(),
    )
    return response.choices[0].message.content
