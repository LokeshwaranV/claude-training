# Graph Report - Agentic-RAG  (2026-09-19)

## Corpus Check
- Corpus is ~16,328 words - fits in a single context window. You may not need a graph.

## Summary
- 274 nodes · 476 edges · 21 communities (12 shown, 9 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 27 edges (avg confidence: 0.89)
- Token cost: 286,746 input · 0 output

## Community Hubs (Navigation)
- HTTP API Layer (main.py)
- Agent Roles & Build Plan
- Frontend Package Config
- Ingestion & Retrieval Engine
- Load Testing (locust)
- Backend/MCP Test Suite
- TypeScript Config
- Knowledge Vault Decisions
- Structured Response Schema
- Observability Test Suite
- Frontend Query UI
- Load-Test User Behavior
- Frontend Agent Rules Docs
- File Icon Asset
- Globe Icon Asset
- Next.js Logo Asset
- Vercel Logo Asset
- Window Icon Asset
- Frontend Scaffold README

## God Nodes (most connected - your core abstractions)
1. `answer_query()` - 21 edges
2. `compilerOptions` - 16 edges
3. `SourceType` - 13 edges
4. `SKILLS.md Governing Rules` - 13 edges
5. `Backend Agent State Log` - 12 edges
6. `Status` - 11 edges
7. `AIDLC 20-Step Build Plan` - 11 edges
8. `Next Session Resume Prompt` - 11 edges
9. `Home (Vault Index)` - 11 edges
10. `browse_documents()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `Observability and Load Testing` --semantically_similar_to--> `eval/loadtest.py (locust script)`  [INFERRED] [semantically similar]
  docs/vault/decisions/Observability and Load Testing.md → eval/LOADTEST.md
- `test_browse_tool_filters_by_source_type_and_excludes_unapproved()` --uses--> `SourceType`  [INFERRED]
  eval/test_mcp_server.py → retrieval/schema.py
- `test_query_with_allowlisted_match_answers_with_citations()` --uses--> `Status`  [INFERRED]
  eval/test_main.py → retrieval/schema.py
- `test_query_with_no_allowlisted_match_refuses()` --uses--> `Status`  [INFERRED]
  eval/test_main.py → retrieval/schema.py
- `test_query_tool_answers_with_grounded_citations()` --uses--> `QueryResponse`  [INFERRED]
  eval/test_mcp_server.py → retrieval/schema.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Four Commitments Enforced Across Ingestion-Retrieval-Grounding-Output Pipeline** — skills_allowlist_only_retrieval, skills_claim_level_grounding, skills_structured_output, skills_fail_gracefully, retrieval_engine, retrieval_answer, retrieval_schema [EXTRACTED 0.90]
- **Backend/Frontend/Triage Multi-Agent Delegation Workflow** — claude_agents_backend, claude_agents_frontend, claude_agents_p3_triage_agent, docs_delegation, docs_context_trimming [EXTRACTED 0.85]
- **Shared Retrieve/Ground/Cite Pipeline Wrapped by HTTP and MCP Entry Points** — main_py, mcp_server, retrieval_answer, retrieval_browse, retrieval_telemetry [EXTRACTED 0.90]
- **AIDLC Steps 8-16 Decision Notes Group** — docs_vault_decisions_delegation_policy, docs_vault_decisions_context_trimming_policy, docs_vault_decisions_plugin_strategy, docs_vault_decisions_mcp_server_strategy, docs_vault_decisions_observability_and_load_testing [INFERRED 0.85]
- **Shared Retrieval Pipeline Functions Reused by HTTP and MCP Entry Points** — main_py, mcp_server, retrieval_answer, retrieval_browse, retrieval_engine [EXTRACTED 1.00]
- **AIDLC POC Template Reusable Scaffolding** — templates_aidlc_poc_readme, templates_aidlc_poc__claude_state_readme, docs_vault_decisions_delegation_policy, docs_vault_decisions_context_trimming_policy [INFERRED 0.85]

## Communities (21 total, 9 thin omitted)

### Community 0 - "HTTP API Layer (main.py)"
Cohesion: 0.12
Nodes (33): Backend Agent State Log, Fixed Gap: missing superseded_by field, Step 14 Review Report (Custom MCP Server), fastapi, get, browse(), health(), main.py (FastAPI /query /browse) (+25 more)

### Community 1 - "Agent Roles & Build Plan"
Cohesion: 0.10
Nodes (35): Backend Sub-Agent, Frontend Sub-Agent, P3-Triage-Agent, Agentic RAG Project CLAUDE.md, Frontend Agent State Log, frontend/src/app/page.tsx (query+browse UI), Triage Agent Verdict Log, AIDLC 20-Step Build Plan (+27 more)

### Community 2 - "Frontend Package Config"
Cohesion: 0.06
Nodes (27): nextConfig, dependencies, next, react, react-dom, devDependencies, @types/node, @types/react (+19 more)

### Community 3 - "Ingestion & Retrieval Engine"
Cohesion: 0.09
Nodes (26): collections, dataclasses, Step 15 Review Report (OpenTelemetry), Design Choice: Grafana via OTLP collector, Chunk, Document, Seed source registry for the Agentic RAG POC (Step 11). A tiny, hand-authored…, math (+18 more)

### Community 4 - "Load Testing (locust)"
Cohesion: 0.08
Nodes (26): contextlib, Step 16 Review Report (Load Testing), Tool Substitution: locust instead of k6, eval/loadtest.py (locust script), Locust load-test script for the Agentic RAG query API (Step 16). k6-vs-locust:…, locust, opentelemetry_sdk_metrics, opentelemetry_sdk_metrics_export (+18 more)

### Community 5 - "Backend/MCP Test Suite"
Cohesion: 0.13
Nodes (13): Basic unit tests for the FastAPI app (main.py) and retrieval/schema.py. Run…, test_query_with_allowlisted_match_answers_with_citations(), test_query_with_no_allowlisted_match_refuses(), Tests for the Step 14 MCP tool wrappers (mcp/server.py). `mcp/` is deliberately…, The MCP wrappers must not duplicate logic — same result as the functions…, test_browse_tool_filters_by_source_type_and_excludes_unapproved(), test_mcp_tools_match_underlying_functions_exactly(), test_query_tool_answers_with_grounded_citations() (+5 more)

### Community 6 - "TypeScript Config"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 7 - "Knowledge Vault Decisions"
Cohesion: 0.33
Nodes (16): code-review skill, Allowlist Policy, Architecture, Context Trimming Policy, Delegation Policy, MCP Server Strategy, Observability and Load Testing, Plugin Strategy (+8 more)

### Community 8 - "Structured Response Schema"
Cohesion: 0.20
Nodes (14): pydantic, BrowseItem, Citation, Confidence, BaseModel, Enum, str, QueryResponse (+6 more)

### Community 9 - "Observability Test Suite"
Cohesion: 0.27
Nodes (13): _counter_value(), _metric_points(), Tests for Step 15 observability: retrieval latency, grounding failures, and…, test_query_requests_and_grounding_failure_counters_on_refusal(), test_query_requests_counter_without_grounding_failure_on_success(), test_refusal_rate_derivable_from_counters_across_multiple_calls(), test_retrieval_latency_histogram_and_span_recorded(), InMemoryMetricReader (+5 more)

### Community 10 - "Frontend Query UI"
Cohesion: 0.20
Nodes (7): BrowseItem, Citation, Home(), frontend_src_app_page_module, QueryResponse, SOURCE_TYPES, react

### Community 11 - "Load-Test User Behavior"
Cohesion: 0.33
Nodes (4): QueryApiUser, Simulates a user hitting /health, /browse, and (mostly) /query., HttpUser, task

## Knowledge Gaps
- **57 isolated node(s):** `nextConfig`, `name`, `version`, `private`, `dev` (+52 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 130 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Next Session Resume Prompt` connect `Agent Roles & Build Plan` to `HTTP API Layer (main.py)`, `Ingestion & Retrieval Engine`, `Load Testing (locust)`, `Knowledge Vault Decisions`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Why does `Backend Agent State Log` connect `HTTP API Layer (main.py)` to `Agent Roles & Build Plan`, `Ingestion & Retrieval Engine`, `Load Testing (locust)`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Why does `QueryApiUser` connect `Load-Test User Behavior` to `Load Testing (locust)`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `SourceType` (e.g. with `test_browse_tool_filters_by_source_type_and_excludes_unapproved()` and `browse()`) actually correct?**
  _`SourceType` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `nextConfig`, `name`, `version` to the rest of the system?**
  _57 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `HTTP API Layer (main.py)` be split into smaller, more focused modules?**
  _Cohesion score 0.1166429587482219 - nodes in this community are weakly interconnected._
- **Should `Agent Roles & Build Plan` be split into smaller, more focused modules?**
  _Cohesion score 0.10084033613445378 - nodes in this community are weakly interconnected._