"""Hybrid retrieval + extractive grounding for the Agentic RAG POC (Step 11).

Deliberately dependency-light: rather than pulling in `rank_bm25` or
`scikit-learn` (neither is installed in this environment and this is a
POC), BM25 and TF-IDF cosine similarity are both implemented here in
~100 lines of pure Python/stdlib (`math`, `collections`). This keeps the
POC runnable with no extra deps and no network access, while still
illustrating a genuine hybrid (lexical + vector-ish) reranking step.

Commitment 1 (allowlist-only retrieval, SKILLS.md): `_approved_chunks()`
filters to `approved: True` documents BEFORE any scoring happens — no
unapproved chunk ever enters the BM25/TF-IDF index.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

from ingestion.seed_data import SEED_DOCUMENTS, Document
from retrieval.telemetry import retrieval_span

_TOKEN_RE = re.compile(r"[a-z0-9]+")

# Small stopword list so common function words (which appear in nearly
# every chunk and would otherwise dominate scores on a tiny corpus) don't
# make unrelated queries look relevant.
_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "does",
    "for", "from", "has", "have", "how", "in", "into", "is", "it", "its",
    "of", "on", "or", "over", "should", "that", "the", "there", "this",
    "to", "was", "were", "what", "when", "where", "which", "who", "will",
    "with",
}


def _tokenize(text: str) -> list[str]:
    return [t for t in _TOKEN_RE.findall(text.lower()) if t not in _STOPWORDS]


@dataclass
class ScoredChunk:
    document_id: str
    chunk_id: str
    source_type: str
    text: str
    score: float


def _approved_documents() -> list[Document]:
    """Allowlist filter — must run before any ranking (commitment 1)."""
    return [doc for doc in SEED_DOCUMENTS if doc["approved"]]


def _approved_chunks() -> list[dict]:
    flat = []
    for doc in _approved_documents():
        for chunk in doc["chunks"]:
            flat.append(
                {
                    "document_id": doc["document_id"],
                    "chunk_id": chunk["chunk_id"],
                    "source_type": doc["source_type"],
                    "text": chunk["text"],
                }
            )
    return flat


def _bm25_scores(query_tokens: list[str], chunk_tokens: list[list[str]]) -> list[float]:
    """Minimal BM25 (k1=1.5, b=0.75) over the approved chunk corpus."""
    k1, b = 1.5, 0.75
    n_docs = len(chunk_tokens)
    if n_docs == 0:
        return []
    avg_len = sum(len(t) for t in chunk_tokens) / n_docs
    df = Counter()
    for tokens in chunk_tokens:
        for term in set(tokens):
            df[term] += 1

    idf = {
        term: math.log(1 + (n_docs - freq + 0.5) / (freq + 0.5))
        for term, freq in df.items()
    }

    scores = []
    for tokens in chunk_tokens:
        tf = Counter(tokens)
        doc_len = len(tokens) or 1
        score = 0.0
        for term in query_tokens:
            if term not in tf:
                continue
            freq = tf[term]
            numerator = idf.get(term, 0.0) * freq * (k1 + 1)
            denominator = freq + k1 * (1 - b + b * doc_len / avg_len)
            score += numerator / denominator
        scores.append(score)
    return scores


def _tfidf_cosine_scores(query_tokens: list[str], chunk_tokens: list[list[str]]) -> list[float]:
    """Lightweight TF-IDF cosine similarity, standing in for embedding similarity."""
    n_docs = len(chunk_tokens)
    if n_docs == 0:
        return []
    df = Counter()
    for tokens in chunk_tokens:
        for term in set(tokens):
            df[term] += 1
    idf = {term: math.log((1 + n_docs) / (1 + freq)) + 1 for term, freq in df.items()}

    def vectorize(tokens: list[str]) -> dict[str, float]:
        tf = Counter(tokens)
        return {term: count * idf.get(term, 0.0) for term, count in tf.items()}

    query_vec = vectorize(query_tokens)
    query_norm = math.sqrt(sum(v * v for v in query_vec.values())) or 1.0

    scores = []
    for tokens in chunk_tokens:
        doc_vec = vectorize(tokens)
        doc_norm = math.sqrt(sum(v * v for v in doc_vec.values())) or 1.0
        dot = sum(query_vec.get(term, 0.0) * weight for term, weight in doc_vec.items())
        scores.append(dot / (query_norm * doc_norm))
    return scores


# Confidence bands on the normalized (0-1-ish) combined score.
# Chosen empirically against the seed corpus: a strong lexical+semantic
# match on a well-covered topic lands ~0.5-1.0+ (high); a partial/loose
# match ~0.15-0.5 (medium); anything below the MIN_RELEVANCE floor is
# treated as "no real match" and triggers a refusal.
MIN_RELEVANCE = 0.05
HIGH_CONFIDENCE_THRESHOLD = 0.5
MEDIUM_CONFIDENCE_THRESHOLD = 0.15


def retrieve(question: str, top_k: int = 3) -> list[ScoredChunk]:
    """Hybrid BM25 + TF-IDF cosine retrieval over the allowlisted corpus only.

    Wrapped in a `retrieval.retrieve` span + `retrieval_latency_seconds`
    histogram (Step 15) covering exactly the allowlist-filter + BM25/TF-IDF
    scoring work, so retrieval latency is observable from both the HTTP and
    MCP entry points without duplicating instrumentation in either.
    """
    with retrieval_span():
        chunks = _approved_chunks()
        if not chunks:
            return []

        query_tokens = _tokenize(question)
        chunk_tokens = [_tokenize(c["text"]) for c in chunks]

        bm25 = _bm25_scores(query_tokens, chunk_tokens)
        tfidf = _tfidf_cosine_scores(query_tokens, chunk_tokens)

        # Combine: normalize BM25 into a comparable range (max-scale) then
        # average with cosine similarity as a simple, transparent reranker.
        max_bm25 = max(bm25, default=0.0) or 1.0
        combined = [(0.5 * (b / max_bm25) + 0.5 * t) for b, t in zip(bm25, tfidf)]

        scored = [
            ScoredChunk(
                document_id=c["document_id"],
                chunk_id=c["chunk_id"],
                source_type=c["source_type"],
                text=c["text"],
                score=score,
            )
            for c, score in zip(chunks, combined)
        ]
        scored.sort(key=lambda s: s.score, reverse=True)
        return scored[:top_k]


def confidence_for(score: float) -> str:
    if score >= HIGH_CONFIDENCE_THRESHOLD:
        return "high"
    if score >= MEDIUM_CONFIDENCE_THRESHOLD:
        return "medium"
    return "low"
