# Prompt to resume this project in a new session

Copy the block below as your first message in a fresh session.

---

This is the Agentic RAG for Pharma Literature Review & Drug-Discovery
Intelligence project at `/home/labuser/Downloads/Agentic-RAG`. It's a 20-step
Claude-based AIDLC build. Before doing anything, read:
- `docs/AIDLC_PLAN.md` — full 20-step plan and tool/model mapping
- `SKILLS.md` — governing rules (allowlist-only retrieval, claim-level
  grounding, structured output, graceful refusal, cross-domain browsing by
  `source_type`)
- `docs/DELEGATION.md` — routing table and the "triage before commit" rule
- `docs/CONTEXT_TRIMMING.md` — how each sub-agent's state file is trimmed
- `docs/PLUGINS.md` — Step 10 plugin/tool strategy (external plugins adopted
  now vs. internal tools deferred to Step 14's MCP server)
- `.claude/state/backend.md`, `.claude/state/frontend.md`,
  `.claude/state/triage.md` — current per-agent summaries/history (these ARE
  the trimmed context — read them instead of replaying full git history)

**Harness note:** `.claude/agents/*.md` files are not auto-registered as
`Agent`-tool `subagent_type`s in this SDK-based environment. To delegate per
`docs/DELEGATION.md`, launch a `general-purpose` agent whose prompt tells it
to read and follow the target `.claude/agents/<name>.md` file as its role,
and restates that file's Isolation rules explicitly.

**Status:** Steps 1-17 of the AIDLC plan are complete and committed (see
`git log --oneline`). Frontend (Next.js) skeleton exists (query + browse UI).
Three sub-agents (backend, frontend, p3-triage-agent) are scoped and
isolated (Step 6), delegation policy is set (Step 7), context trimming is in
place (Step 8), Step 9 extracted the reusable scaffolding into
`templates/aidlc-poc/`, Step 10 (`docs/PLUGINS.md`) decided the plugin
strategy, Step 11 built the RAG engine end to end (`ingestion/seed_data.py`,
`retrieval/engine.py` — allowlist-filtered BM25+TF-IDF hybrid,
`retrieval/answer.py` — extractive grounded generation, `main.py`'s
`/query`+`/browse` wired to `retrieval/schema.py`), and Step 12 ran the
`code-review` skill on the Step 11 diff alongside triage's domain review —
combined report at `docs/reviews/STEP_11_REVIEW.md`. Two findings:
- `escalated` status is still never triggered — **deferred**, no cheap
  well-defined trigger for a 7-doc POC corpus (both reviews independently
  flagged it, same reasoning holds). Revisit once a real corpus exists or a
  concrete conflicting-evidence test case is added.
- `superseded_by` (required by SKILLS.md's source-registry expectations)
  was missing from `ingestion/seed_data.py`'s `Document` type/seed entries
  and `retrieval/schema.py`'s `BrowseItem` — **fixed**: added to both,
  wired through `main.py`'s `/browse`, `doc-ct-007.superseded_by =
  "doc-ct-003"` (matching its own title), all others `None`. Triage
  independently re-verified the fix via diff + a fresh `pytest` run (5
  passed) before this was committed.

Step 13 (`docs/MCP_EVALUATION.md`) evaluated the filesystem, Postgres, and
web-search MCP servers from mcpservers.org for reuse. None were adopted:
no filesystem-based corpus exists to wrap (ingestion is still in-memory
`ingestion/seed_data.py`), no database exists for a Postgres server to wrap
(`retrieval/engine.py` is fully in-memory), and web-search is already
scoped to authoring-time-only per `docs/PLUGINS.md` (Step 10), so a
dedicated MCP server for it would be redundant. No code changes; decision
doc only.

Step 14 built the custom MCP server (`mcp/server.py`) wrapping the RAG
pipeline as MCP tools: `query` (wraps `retrieval/answer.py::answer_query`)
and `browse` (wraps the newly-extracted `retrieval/browse.py::
browse_documents`, which `main.py`'s HTTP `/browse` now also calls, so
there's one shared implementation instead of duplicated filter logic).
`mcp` added to `requirements.txt` (unpinned — noted, not blocking).
`eval/test_mcp_server.py` adds 5 tests; `pytest eval/ -q` → 10 passed.
Triage-only review (small diff over already-reviewed Step 11 logic) —
**PASS**, no fixes required. Full report: `docs/reviews/STEP_14_REVIEW.md`.

Step 15 instrumented the backend with the OpenTelemetry SDK
(`retrieval/telemetry.py`): a `retrieval.retrieve` span + latency
histogram around `retrieval/engine.py::retrieve`, and
`query_requests_total`/`grounding_failures_total` counters in
`retrieval/answer.py::answer_query` (refusal rate = failures/requests).
Both `main.py`'s HTTP endpoints and `mcp/server.py`'s MCP tools call the
same instrumented functions, so nothing double-counts. Exporter is
env-var-selectable (`AGENTIC_RAG_OTEL_EXPORTER=otlp|console|none`,
defaulting to `otlp` targeting a Grafana-fed OTLP collector at
`http://localhost:4317`) and verified to no-op safely with no collector
running. `eval/test_telemetry.py` adds 4 tests; `pytest eval/ -q` → 14
passed. Triage-only review — **PASS**, no notes. Full report:
`docs/reviews/STEP_15_REVIEW.md`.

Step 16 did load testing against the query API. k6 (named in the plan)
isn't installed and would need a new APT repo (system change), so the user
chose **locust** instead (pip-installable, no system changes) —
`eval/loadtest.py` exercises `/health`, `/browse` (filtered/unfiltered),
and `/query` weighted heaviest (grounded questions matched to real seed-doc
content + a refusal-path question). Run against a locally-started backend
(`AGENTIC_RAG_OTEL_EXPORTER=console uvicorn main:app --host 127.0.0.1
--port 8000`): 478 requests over 30s/10 users, 0% failures, p50 4ms/p95
8ms, ~16.3 req/s overall (~11.9 req/s on `/query` alone). Step 15's
`grounding_failures_total` counter was confirmed moving under load via the
console exporter (no live Grafana/collector stood up — out of scope for
this step; that pairing is only needed if the plan revisits observability
end-to-end later). Results/rerun steps in `eval/LOADTEST.md`. Triage-only
review — **PASS**, no notes. Full report: `docs/reviews/STEP_16_REVIEW.md`.

Step 17 built the Obsidian knowledge vault at `docs/vault/` (plain
Markdown + `[[wikilink]]` cross-links — no Obsidian install/server needed
to create or read it, just open that folder as a vault in the Obsidian app
if you want the graph view). `Home.md` is the readme-mode index; other
notes cover `Architecture.md`, `Governing Rules.md`, `Allowlist Policy.md`,
and `decisions/` (Delegation, Context Trimming, Plugin Strategy, MCP
Server Strategy, Observability and Load Testing) — each mirrors an
existing `docs/*.md` file's decision but adds cross-links and "why"
framing. `Vault Maintenance.md` documents the update rule: edit the
relevant vault note (not just this file or agent state files) after any
step that changes architecture/policy/decisions. Docs-only, cross-cutting
change (`docs/DELEGATION.md`'s orchestrator-owned row) — no triage review
needed, no pipeline/schema/UI behavior touched.

Step 18 ran the `graphify` skill over the whole repo (code + docs) to build
a knowledge graph for architecture/traceability queries — AST extraction
for the 22 code files (no LLM/API key needed) plus 7 parallel
`general-purpose` subagents for semantic extraction of the 35 doc + 5
image files, merged into 274 nodes / 476 edges / 21 communities. Outputs
live in `graphify-out/`: `graph.json` (GraphRAG-ready), `graph.html`
(interactive viz, no server needed), `GRAPH_REPORT.md` (plain-language
summary with labeled communities, god nodes, surprising connections,
suggested questions). This is graphify's own artifact, separate from the
Step 17 `docs/vault/` (which stays the hand-authored Obsidian vault) —
`--obsidian` export was not requested so it wasn't run. Token-reduction
benchmark (Steps 6b-8) was skipped: corpus is ~16k words, under the
threshold where a graph pays for itself over reading the raw files
directly, and the report says so.

**Known issue, not fixed:** `diagnose_extraction` flagged a **GRAPH HEALTH
WARNING** — 29 dangling-endpoint edges, 26 collapsed (directed)/39
collapsed (undirected) edges. Inspected examples (e.g.
`mcp_server -> retrieval_answer` collapsing 3 edges with relations
`calls`/`imports_from`/`references`) look like AST and semantic extraction
both describing the same real relationship via different relation types,
not corruption — but this wasn't independently verified further. Revisit
if the graph is relied on for anything beyond a one-off report.

Local demo servers were started for Step 18's "and deploy" ask — no
hosted/cloud deployment exists or was requested (user picked "local demo
now" when asked what "deploy" meant): backend `uvicorn main:app` on
`http://127.0.0.1:8000` (`AGENTIC_RAG_OTEL_EXPORTER=console`), frontend
`npm run dev` on `http://localhost:3000` (`NEXT_PUBLIC_API_BASE` pointed at
the backend port — the frontend's own default, `8123`, doesn't match and
would need a code fix or an env var at every future launch, whichever this
project prefers long-term).

Since Step 18, a cross-cutting feature (not one of the 20 numbered steps,
requested directly by the user) added a Groq-backed synthesis layer, a
second "Open Research" (ungrounded) answering mode, corpus expansion, and
a restructured dashboard frontend:

- `SKILLS.md` gained **Commitment 6** (open-research mode is separate,
  opt-in, visibly labeled, never a fallback inside the grounded path).
- `retrieval/groq_client.py` (new) wraps the `groq` SDK, read lazily via
  `AGENTIC_RAG_GROQ_API_KEY`/`AGENTIC_RAG_GROQ_MODEL`/
  `AGENTIC_RAG_GROQ_TIMEOUT_S` env vars — the app boots and grounded query
  still works via extractive fallback with no key set.
- `retrieval/answer.py`'s grounded synthesis now calls Groq when configured
  and falls back to `Status.escalated` (first real use of that enum value)
  if the post-hoc grounding check fails, times out, or errors — citations
  still always come from `retrieve()`'s `top_chunks`, never from Groq's own
  markers.
- `retrieval/open_research.py` (new) + `POST /query/open-research` in
  `main.py` + `open_research_query` MCP tool in `mcp/server.py`: ungrounded,
  no retrieval, no citations, `OpenResearchResponse` schema (never
  `QueryResponse`), returns HTTP 503 if Groq isn't configured.
- **Simulation mode** (`AGENTIC_RAG_GROQ_SIMULATE=1`): since the user could
  not obtain a real `GROQ_API_KEY` in this session, both synthesis paths
  have an honest, explicitly-labeled simulated fallback — grounded mode
  dedupes/reorders real chunk sentences with valid `[n]` citation markers
  (never fabricates), open-research mode returns a fixed "this is
  simulated" message. Never silently indistinguishable from a real Groq
  answer — `model="simulated"` and an appended disclaimer string mark it.
  **When a real `GROQ_API_KEY` is available, set `AGENTIC_RAG_GROQ_API_KEY`
  as an env var (never in a file/commit), leave `AGENTIC_RAG_GROQ_SIMULATE`
  unset, and restart the backend to exercise the real path for the first
  time.**
- `ingestion/seed_data.py` grew from 7 to 15 documents across 6 domains
  (added oncology/checkpoint-inhibitor, oncology/PARP-inhibitor,
  cardio-renal-metabolic, HIV PrEP, gene-therapy docs) — verified
  `retrieval/engine.py`'s `MIN_RELEVANCE`/confidence thresholds still hold
  without retuning.
- Frontend restructured from a single-file page into a dashboard:
  `Sidebar` (Query/Browse/Open Research tabs + corpus stat tiles),
  `GroundedQueryPanel`, `OpenResearchPanel` (visually distinct, persistent
  disclaimer banner), `BrowsePanel`, `RecentQueriesWidget`. Query (grounded)
  remains the default tab; Open Research is opt-in only, per Commitment 6.
- Also fixed in this stretch: CORS (`main.py` now has explicit-origin
  `CORSMiddleware` for `localhost:3000`/`127.0.0.1:3000` — was causing
  "failed to fetch" from the browser).
- Both local demo servers were confirmed live and working end-to-end with
  `AGENTIC_RAG_GROQ_SIMULATE=1` set (backend on `127.0.0.1:8000`, frontend
  on `localhost:3000`) at the end of this stretch of work — verified via
  curl against both `/query` and `/query/open-research`.
- **Not yet done:** a formal eval-set/pytest pass specifically for the
  Groq/escalated/open-research code paths (existing sub-agent verification
  was curl-level, not a committed test file) — worth folding into Step 19.

**Next:** proceed with Step 19 (prompt engineering / eval iteration) per
`docs/AIDLC_PLAN.md`, then Step 20 (demo to first user). Update this file
and the per-agent state files after each step so the next session can
resume cleanly.

---
