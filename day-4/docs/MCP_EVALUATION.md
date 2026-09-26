# MCP server evaluation (Step 13)

Step 13 of `docs/AIDLC_PLAN.md` evaluates existing servers from mcpservers.org
for reuse, before Step 14 builds the custom MCP server that wraps the RAG
engine's retrieve/ground/cite pipeline. Like Step 10, this is a decision
step, not an implementation step.

## Candidates considered

### filesystem MCP server

Would expose read access to a directory tree as MCP tools/resources.

**Not adopted.** There is no filesystem-based corpus to wrap: ingestion is
`ingestion/seed_data.py`, an in-memory Python list of 7 hand-authored seed
docs (see `.claude/state/backend.md`). A filesystem server has nothing real
to point at yet. Revisit if/when ingestion moves to reading a real corpus
(PDFs, HTML dumps, etc.) off disk — at that point the filesystem server may
cover the "read raw source files" step before chunking/indexing.

### Postgres MCP server

Would expose SQL query/execute tools against a Postgres instance.

**Not adopted.** There is no database in this build at all — `retrieval/engine.py`
holds everything in memory and re-scores the 7-doc corpus per request; there
is nothing for a Postgres MCP server to wrap. Adopting it now would mean
standing up a DB and a persistence layer neither Step 11 nor the POC's scale
requires. Revisit only if/when the corpus grows past what an in-memory
BM25/TF-IDF pass can serve interactively, and a real datastore is introduced
for documents/chunks — at that point, reusing the Postgres MCP server is
preferable to hand-rolling a DB wrapper inside Step 14's custom server.

### web-search MCP server

Would expose web search as MCP tools, redundant with the built-in
`web-search` capability already decided on in `docs/PLUGINS.md` (Step 10).

**Not adopted.** `docs/PLUGINS.md` already scoped web-search to
ingestion-authoring/testing time only (e.g. checking a candidate source's
metadata before adding it to the allowlist), explicitly never at query-time
(that would bypass the allowlist — commitment 1 in `SKILLS.md`). The
already-available built-in `web-search` tool covers that authoring-time use
case; a dedicated MCP server for the same capability adds nothing and,
being an additional standing tool grant, is more surface than the task
needs.

## Outcome

None of the three infra-level MCP servers evaluated are adopted at this
stage. All three are deferred for the same underlying reason: they would
each wrap infrastructure (files on disk, a SQL database, web search at
query-time) that this POC does not have or does not need yet at its current
7-doc, in-memory, offline scale. This is consistent with Step 10's "revisit
if Step 11/15 surfaces a concrete gap" stance — Step 11 did not surface one,
so Step 13 confirms the same call for the infra-level servers specifically.

Step 14 proceeds as planned: build a custom MCP server wrapping the
existing in-memory retrieve/ground/cite pipeline (`retrieval/engine.py`,
`retrieval/answer.py`) as MCP tools, with no external server dependency.

## Verification

Decision doc only — nothing to test. Verification is that this doc's calls
get referenced (not silently deviated from) when Step 14 is implemented, and
revisited explicitly if a real corpus/persistence need appears later.
