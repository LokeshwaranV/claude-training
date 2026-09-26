# Step 14 review — custom MCP server

Triage-only review (no `code-review` skill pass — this diff is a thin
wrapper around already-reviewed Step 11 logic, not new pipeline behavior;
`docs/DELEGATION.md` allows triage-alone for small diffs).

## Verdict: PASS

Checked against all five `SKILLS.md` commitments:

1. **Allowlist-only retrieval** — `mcp/server.py`'s `query`/`browse` tools
   call the exact same `retrieval.answer.answer_query` /
   `retrieval.browse.browse_documents` functions the HTTP endpoints use; no
   separate or looser codepath.
2. **Claim-level grounding** — `query` tool output is `answer_query()`'s
   result unmodified; citations still resolve to real `(document_id,
   chunk_id)` pairs.
3. **Structured output** — MCP tools return the real `QueryResponse` /
   `BrowseItem` pydantic models, not ad hoc dicts.
4. **Graceful refusal** — refusal path (`status=refused`, no citations)
   preserved through the wrapper; covered by
   `test_query_tool_refuses_below_relevance_floor`.
5. **Cross-domain browsing** — `browse(source_type=...)` filter preserved.

**No duplicated logic**: `main.py`'s `/browse` and the new MCP `browse`
tool both call one implementation, `retrieval/browse.py::browse_documents()`
(extracted from what was previously inlined in `main.py`). Confirmed by
`test_mcp_tools_match_underlying_functions_exactly`.

**Tests**: triage independently ran `python3 -m pytest eval/ -q` → 10
passed (5 pre-existing + 5 new in `eval/test_mcp_server.py`).

**Frontend boundary**: no `/frontend` changes — confirmed via `git diff
--stat`.

## Non-blocking note

`requirements.txt`'s new `mcp` entry is unpinned. Not a new deviation (some
existing entries are also unpinned) but worth pinning once Step 15+
observability tooling starts depending on a stable `mcp` API surface.
Deferred, not a blocker for this POC step.

## Files

`mcp/server.py` (new), `retrieval/browse.py` (new), `main.py` (changed —
`/browse` delegates to the extracted function), `requirements.txt` (added
`mcp`), `eval/test_mcp_server.py` (new, 5 tests).
