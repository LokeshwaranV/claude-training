# Architecture

## Pipeline

```
ingestion/seed_data.py  →  retrieval/engine.py  →  retrieval/answer.py  →  schema-valid response
   (7 seed docs,             (allowlist filter        (extractive
    mixed approved/           BEFORE ranking,           generation,
    unapproved, all 4         then BM25 + TF-IDF         grounded
    source_types)             cosine hybrid)             citations)
```

Two entry points sit on top of the same pipeline functions — no duplicated
logic, confirmed at each review:

- **HTTP** (`main.py`) — `/query` (POST) and `/browse` (GET), FastAPI.
- **MCP** (`mcp/server.py`, added Step 14) — `query` and `browse` tools,
  calling `retrieval/answer.py::answer_query` and
  `retrieval/browse.py::browse_documents` directly.

Both paths are instrumented identically since Step 15 (see
[[Observability and Load Testing]]) — counters/spans live in the shared
`retrieval/` layer, not duplicated per entry point.

## Why allowlist-filter-then-rank, not rank-then-filter

Filtering to `approved: true` *before* scoring means an unapproved
high-relevance document can never leak into the candidate set, even
indirectly (e.g. via a tied score or a ranking bug). See
[[Allowlist Policy]] and [[Governing Rules]].

## Why extractive generation, not an LLM call

No LLM API key exists in this environment. `retrieval/answer.py` stitches
the top 1-2 allowlisted chunks into an answer (2nd only if within 80% of
the top score), with citations built directly from the retrieved chunks —
grounding is structural (the citation *is* the source of the text), not a
post-hoc check bolted onto free-text generation.

## Related

[[Governing Rules]] · [[Allowlist Policy]] · [[MCP Server Strategy]]
