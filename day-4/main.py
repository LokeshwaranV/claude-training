from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from retrieval.answer import answer_query
from retrieval.browse import browse_documents
from retrieval.open_research import answer_open_research
from retrieval.schema import BrowseItem, OpenResearchResponse, QueryResponse, SourceType
from retrieval.telemetry import http_span

app = FastAPI(title="Agentic RAG — Pharma Literature Review")

# Local dev POC: the Next.js frontend (localhost:3000) calls this API
# directly from the browser, so it needs CORS enabled. Explicit origin
# list (not "*") since browsers treat localhost/127.0.0.1 as distinct
# origins and this app has no cookies/credentials to protect.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/browse", response_model=list[BrowseItem])
def browse(source_type: SourceType | None = None) -> list[BrowseItem]:
    """List-only, allowlist-filtered browse across source types. No generation."""
    with http_span("http.browse"):
        return browse_documents(source_type)


@app.post("/query", response_model=QueryResponse)
def query(question: str) -> QueryResponse:
    """Hybrid-retrieval RAG: allowlist-filtered BM25 + TF-IDF cosine, extractive
    answer synthesis, and claim-level grounding (Step 11 — see docs/AIDLC_PLAN.md).

    Step 15: wrapped in a thin `http.query` span for request-level tracing;
    the actual retrieval-latency histogram and grounding-failure/query-total
    counters live in `retrieval/engine.py` and `retrieval/answer.py` (the
    shared layer both this endpoint and mcp/server.py's `query` tool call),
    so they aren't duplicated here.
    """
    with http_span("http.query"):
        return answer_query(question)


@app.post("/query/open-research", response_model=OpenResearchResponse)
def query_open_research(question: str) -> OpenResearchResponse:
    """Explicit, opt-in open-research (ungrounded) mode (SKILLS.md
    commitment 6): general-model-knowledge answer, no retrieval, no
    allowlist filter, no citations. Distinct response shape from
    QueryResponse so it can never be confused with a grounded answer.
    Returns 503 if AGENTIC_RAG_GROQ_API_KEY is not configured.
    """
    with http_span("http.query_open_research"):
        try:
            return answer_open_research(question)
        except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e))
