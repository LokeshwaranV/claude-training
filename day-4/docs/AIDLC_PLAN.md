# AIDLC Build Plan — Agentic RAG for Pharma Literature Review & Drug-Discovery Intelligence

## Context

This is the "sixth POC" build, following a 20-step Claude-based AI Development Life Cycle (AIDLC). It implements the system described in Case Study 1 (Appendix A): a grounded, agentic retrieval system for pharma R&D that finds evidence, judges confidence, and traces every claim to a source — under four governing commitments: allowlist-only retrieval, claim-level grounding, structured output, and graceful failure/escalation.

The project directory is currently empty (`/home/labuser/Downloads/Agentic-RAG`, not a git repo). This plan defines requirements and assigns concrete tools/models/methods to each of the 20 AIDLC steps so the build can proceed step-by-step.

## Requirements derived from the case study

- **Allowlisted retrieval**: ingestion must tag every source with an approval status; the retriever must filter to approved sources only, before ranking.
- **Claim-level grounding**: every generated statement must carry a citation resolvable to a specific chunk/document in the allowlist — no ungrounded claims pass through.
- **Structured output**: responses conform to a fixed schema (e.g. `{answer, confidence, citations[], caveats[]}`), not free text.
- **Graceful failure**: when confidence is low or evidence is insufficient, the system refuses or escalates instead of generating an answer.
- **Multi-source ingestion**: literature (papers), patents, clinical-trial registries, internal reports — each with different formats/update cadences (version drift risk).
- **Auditability**: since claims may be legally challenged, the source trail (retrieval → chunk → citation) must be reconstructable after the fact.
- **Cross-domain browsing**: users can browse/filter the corpus across source types (literature, patent, clinical trial, internal report) as a first-class exploration mode, not just via query-answer — still constrained to the allowlist.

## Step-by-step tool/model/method mapping

**Stage 1 — Problem definition & planning**
- Step 1: Identify Problem Statement — done (this conversation / case study doc).
- Step 2: Plan the AIDLC — Claude Chat (Opus/Sonnet 5) to draft the architecture doc: ingestion → retrieval → grounding → generation → structured output → refusal logic.

**Stage 2 — Repo & agent scaffolding**
- Step 3: Claude Code — `claude init` style scaffold: create repo dirs (`/ingestion`, `/retrieval`, `/agents`, `/mcp`, `/eval`), add `SKILLS.md` (documents allowlist rules, grounding rules, schema) and `.claude/settings.json` hooks (e.g. pre-commit lint, PII scan hook).
- Step 4: Two sub-agents:
  - **Backend sub-agent**: Python (FastAPI), owns ingestion, retrieval, grounding, schema enforcement.
  - **Frontend sub-agent**: React/Next.js, owns query UI, citation display, confidence indicators, and a cross-domain browse view (facet filters by `source_type`: literature / patent / clinical_trial / internal_report, plus free-text search within a facet).
- Step 5: **P3-Triage-Agent** — a review/reporting sub-agent (Claude Sonnet 5) that runs after each backend/frontend change: checks schema conformance, citation validity, allowlist compliance; produces a pass/fail report.

**Stage 3 — Multi-agent context management**
- Step 6: Isolation context — each sub-agent gets its own `.claude/agents/<name>.md` with scoped tool access (backend agent: file/bash/DB tools only; frontend agent: file/bash/browser-preview only; triage agent: read-only + ReportFindings).
- Step 7: Delegation — main orchestrator (Claude Code session) routes: ingestion/RAG tasks → backend agent, UI tasks → frontend agent, all diffs → triage agent before merge.
- Step 8: Context trimming — cap each sub-agent's stored history to a running summary (~12-15% of context budget) + last 8-10 raw turns; implement via a simple summarizer hook or session compaction policy documented in each agent's memory file.
- Step 9: Reusable setup — extract common scaffolding (agent definitions, hooks, schema validators) into a template/`cookiecutter`-style config so future POCs reuse it.

**Stage 4 — Knowledge & tool integration**
- Step 10: Plugins — internal: custom retrieval/grounding tools as MCP tools; external: pull from claude.com/plugins (e.g. web-search, code-review plugin already available in this env).
- Step 11: RAG engine — embedding model (e.g. `voyage-3` or OpenAI-compatible embeddings) + vector store (Chroma/Weaviate/pgvector) + hybrid (BM25 + vector) retrieval + allowlist filter + reranker; generation via Claude Sonnet 5 with structured-output enforcement (JSON schema / tool-use forced format). Retrieval layer exposes a separate **browse endpoint** (facet-filter + list, no generation) alongside the query/answer endpoint, so users can explore by `source_type` without triggering an LLM call.

**Stage 5 — Review & orchestration**
- Step 12: Test/review/report — use the `code-review` skill/plugin on each PR; triage agent produces the report artifact.
- Step 13: MCP server — evaluate existing servers from mcpservers.org (e.g. filesystem, web-search, Postgres) for reuse.
- Step 14: Custom MCP server — wrap the RAG engine (retrieve, ground, cite) as MCP tools so any agent/client can orchestrate the pipeline uniformly.

**Stage 6 — Reliability & knowledge management**
- Step 15: Observability — instrument backend with OpenTelemetry SDK; export traces/metrics/logs to Grafana or SigNoz; track retrieval latency, grounding failures, refusal rate.
- Step 16: Load testing — k6 or JMeter scripts against the query API; visualize p50/p95 latency and throughput in the same Grafana dashboard.
- Step 17: Knowledge vault — Obsidian vault as the project's living README/wiki (architecture notes, decisions, allowlist policy docs), "readme mode" = auto-generated index note.
- Step 18: Graph database nodes — use the `graphify` skill to turn the codebase/docs into a knowledge graph (files, sources, citations as nodes) for architecture/traceability queries.

**Stage 7 — Validation & demo**
- Step 19: Prompt engineering iteration — refine grounding/refusal prompts against an eval set (golden Q&A pairs with expected citations); measure grounding accuracy and refusal correctness.
- Step 20: Demo to first user — package a walkthrough (sample queries, one showing correct grounded answer, one showing correct refusal).

## Verification

- Steps 1-2: architecture doc reviewed and agreed before scaffolding.
- Steps 3-9: `claude code` scaffold runs; sub-agents respond correctly to scoped test prompts; context-trimming behavior manually verified on a long session.
- Steps 10-14: RAG engine returns grounded, schema-valid answers for known queries; MCP server tools callable independently of the main agent.
- Steps 15-16: Grafana dashboard shows live traces during a load test run.
- Steps 17-18: Obsidian vault and graphify graph reflect current repo state.
- Steps 19-20: Eval set passes threshold (e.g. >90% correct grounding/refusal) before live demo.

## Next step

Start with Step 3 (Claude Code scaffolding: directories, SKILLS.md, hooks) once this plan is approved — Steps 1-2 are effectively complete via this conversation and case-study doc.
