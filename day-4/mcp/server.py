"""Custom MCP server wrapping the RAG engine (Step 14, docs/AIDLC_PLAN.md).

Decision context: `docs/PLUGINS.md` (Step 10) deferred wrapping
retrieve/ground/cite as MCP tools until the RAG engine existed;
`docs/MCP_EVALUATION.md` (Step 13) confirmed no external infra-level MCP
server (filesystem/Postgres/web-search) is needed for this in-memory,
offline POC. This module is the custom server Step 14 builds instead.

It does NOT reimplement retrieval, grounding, or browse logic — it wraps
the same Python functions the FastAPI app in `main.py` calls
(`retrieval.answer.answer_query`, `retrieval.browse.browse_documents`), so
there is exactly one implementation of each behavior and the MCP tools and
HTTP endpoints can never drift apart.

Two tools are exposed:
- `query(question)` — allowlist-filtered hybrid retrieval + extractive
  grounded answer, fixed QueryResponse schema, refusal on low relevance
  (commitments 1-4, SKILLS.md).
- `browse(source_type=None)` — allowlist-filtered, optionally
  source_type-scoped listing, no generation (commitment 5, SKILLS.md).

Uses the `mcp` package (Python MCP SDK), already present in this
environment (v2.x: `MCPServer`, the successor to the v1 `FastMCP` name).
Runs over stdio by default, consistent with the project's "POC, offline,
no LLM API key, no extra network dependency" constraints from Step 11.
"""

from __future__ import annotations

from mcp.server.mcpserver import MCPServer

from retrieval.answer import answer_query
from retrieval.browse import browse_documents
from retrieval.open_research import answer_open_research
from retrieval.schema import BrowseItem, OpenResearchResponse, QueryResponse, SourceType

mcp = MCPServer(
    name="agentic-rag",
    instructions=(
        "Pharma literature RAG tools: `query` answers a question with "
        "allowlist-filtered, claim-grounded citations (or refuses below "
        "the relevance floor); `browse` lists allowlisted documents, "
        "optionally filtered by source_type, with no generation; "
        "`open_research_query` is a separate, explicitly opt-in, "
        "ungrounded/uncited mode that answers from general model "
        "knowledge with no corpus retrieval and no allowlist filtering — "
        "distinct from `query` and never a substitute for it."
    ),
)


@mcp.tool()
def query(question: str) -> QueryResponse:
    """Answer a question via allowlist-filtered hybrid retrieval and
    extractive grounded generation. Returns the fixed QueryResponse schema
    (answer, confidence, citations[], caveats[], status) and refuses rather
    than fabricates when no allowlisted evidence clears the relevance
    floor. Wraps retrieval.answer.answer_query — the same function
    main.py's POST /query calls.
    """
    return answer_query(question)


@mcp.tool()
def browse(source_type: SourceType | None = None) -> list[BrowseItem]:
    """List allowlisted documents, optionally filtered by source_type
    (literature, patent, clinical_trial, internal_report). List-only, no
    generation, no citation synthesis. Wraps retrieval.browse.browse_documents
    — the same function main.py's GET /browse calls.
    """
    return browse_documents(source_type)


@mcp.tool()
def open_research_query(question: str) -> OpenResearchResponse:
    """Explicit, opt-in open-research (ungrounded) mode. Answers from the
    model's general knowledge with no retrieval, no allowlist filtering,
    and no citations — a distinct response shape from QueryResponse so it
    can never be mistaken for a citation-backed answer. Raises if
    AGENTIC_RAG_GROQ_API_KEY is not configured. Wraps
    retrieval.open_research.answer_open_research — the same function
    main.py's POST /query/open-research calls.
    """
    return answer_open_research(question)


if __name__ == "__main__":
    mcp.run()
