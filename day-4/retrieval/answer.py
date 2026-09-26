"""Extractive answer synthesis + grounding for the Agentic RAG POC (Step 11).

No LLM call — there's no API key in this environment and this is a POC.
Generation here is purely extractive: the top-scoring allowlisted chunk(s)
are stitched into a short answer, and every citation is guaranteed to
resolve to a (document_id, chunk_id) pair that came from the allowlist
(commitment 2, claim-level grounding) because it is only ever built from
`retrieve()`'s output, which is itself filtered to `approved: True`
documents before scoring (commitment 1).
"""

from __future__ import annotations

import re

from retrieval import groq_client
from retrieval.engine import MIN_RELEVANCE, confidence_for, retrieve
from retrieval.schema import Citation, Confidence, QueryResponse, SourceType, Status
from retrieval.telemetry import (
    record_grounding_failure,
    record_groq_synthesis_failure,
    record_query_request,
)

_MARKER_RE = re.compile(r"\[(\d+)\]")
_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "if",
    "in", "into", "is", "it", "no", "not", "of", "on", "or", "such", "that",
    "the", "to", "was", "will", "with", "from", "this", "these", "those",
}


def _content_overlap_ratio(sentence: str, chunk_text: str) -> float:
    """Calculate semantic overlap: % of non-stopword tokens from sentence
    that appear in chunk_text. Returns [0, 1]."""
    sentence_words = set(w.lower() for w in re.findall(r"\b\w+\b", sentence))
    chunk_words = set(w.lower() for w in re.findall(r"\b\w+\b", chunk_text))
    content_words = sentence_words - _STOPWORDS
    if not content_words:
        return 1.0  # All stopwords, trivially overlaps
    overlap = len(content_words & chunk_words)
    return overlap / len(content_words)


def _passes_grounding_check(text: str, chunks: list) -> bool:
    """Post-hoc semantic grounding check on Groq-synthesized answer:
    (1) every sentence must have at least one [n] bracket marker in range,
    (2) at least 40% of content words in each sentence must appear in the
    cited chunk(s) — ensures facts are grounded in chunk vocabulary, not
    hallucinated.

    Args:
        text: synthesized answer text
        chunks: list of RetrievalResult with .text field, indexed 1..n

    Returns:
        True if all sentences pass both syntactic and semantic checks.
    """
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if not sentences:
        return False

    chunk_texts = {i: chunk.text for i, chunk in enumerate(chunks, start=1)}

    for sentence in sentences:
        markers = _MARKER_RE.findall(sentence)
        if not markers:
            # No marker at all
            return False
        marker_ints = [int(m) for m in markers]
        if not any(1 <= m <= len(chunks) for m in marker_ints):
            # All markers out of range
            return False

        # Semantic check: sentence must have meaningful content overlap
        # with at least one of its cited chunks.
        valid_markers = [m for m in marker_ints if 1 <= m <= len(chunks)]
        overlaps = [_content_overlap_ratio(sentence, chunk_texts[m]) for m in valid_markers]
        max_overlap = max(overlaps) if overlaps else 0.0

        if max_overlap < 0.4:
            # Sentence's content words don't match the cited chunks
            return False

    return True


def answer_query(question: str) -> QueryResponse:
    record_query_request()
    results = retrieve(question)

    if not results or results[0].score < MIN_RELEVANCE:
        # Grounding failure (Step 15): no allowlisted chunk cleared
        # MIN_RELEVANCE, so we refuse rather than fabricate (commitment 4).
        record_grounding_failure()
        return QueryResponse(
            answer=None,
            confidence=Confidence.low,
            citations=[],
            caveats=[
                "No allowlisted source cleared the minimum relevance "
                "threshold for this question. Refusing rather than "
                "fabricating an answer."
            ],
            status=Status.refused,
        )

    # Take the top chunk plus any other chunk within 80% of its score,
    # capped at 2, to keep the extractive answer tight and grounded.
    top_score = results[0].score
    top_chunks = [results[0]]
    for chunk in results[1:]:
        if len(top_chunks) >= 2:
            break
        if chunk.score >= 0.8 * top_score:
            top_chunks.append(chunk)

    if groq_client.is_configured():
        try:
            groq_answer = groq_client.synthesize_grounded(question, top_chunks)
        except Exception:
            groq_answer = None
        if groq_answer is not None and _passes_grounding_check(groq_answer, top_chunks):
            answer = groq_answer
        else:
            record_groq_synthesis_failure()
            return QueryResponse(
                answer=None,
                confidence=Confidence.low,
                citations=[],
                caveats=[
                    "Groq synthesis failed grounding check or timed out; "
                    "escalated for review."
                ],
                status=Status.escalated,
            )
    else:
        answer = " ".join(chunk.text for chunk in top_chunks)

    citations = [
        Citation(
            document_id=chunk.document_id,
            chunk_id=chunk.chunk_id,
            source_type=SourceType(chunk.source_type),
        )
        for chunk in top_chunks
    ]

    confidence = Confidence(confidence_for(top_score))
    caveats = []
    if confidence == Confidence.low:
        caveats.append(
            "Retrieved evidence cleared the relevance floor but scored low "
            "confidence; treat this answer as provisional."
        )

    return QueryResponse(
        answer=answer,
        confidence=confidence,
        citations=citations,
        caveats=caveats,
        status=Status.answered,
    )
