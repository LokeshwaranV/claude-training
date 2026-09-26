"""Tests for the Step 14 MCP tool wrappers (mcp/server.py).

`mcp/` is deliberately not a Python package (no `__init__.py`) so that it
never shadows the installed `mcp` SDK package when the repo root is on
`sys.path`. That means the module is loaded here via `importlib` from its
file path rather than a normal `from mcp.server import ...` import.

These tests call the wrapped Python functions/tools directly rather than
spinning up a full MCP client/stdio transport — disproportionate effort for
a POC per the Step 14 task brief. They assert that going through the MCP
tool wrappers preserves the same allowlist/grounding/schema behavior as the
underlying `retrieval.answer.answer_query` / `retrieval.browse.browse_documents`
functions that `main.py`'s HTTP endpoints call.
"""

import importlib.util
import pathlib

from retrieval.schema import QueryResponse, SourceType, Status

_SERVER_PATH = pathlib.Path(__file__).resolve().parent.parent / "mcp" / "server.py"
_spec = importlib.util.spec_from_file_location("rag_mcp_server", _SERVER_PATH)
rag_mcp_server = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rag_mcp_server)


def test_query_tool_answers_with_grounded_citations():
    response = rag_mcp_server.query(
        "What is the mechanism of action of semaglutide as a GLP-1 receptor agonist?"
    )
    assert isinstance(response, QueryResponse)
    assert response.status == Status.answered
    assert response.answer
    assert len(response.citations) >= 1
    for citation in response.citations:
        assert citation.document_id
        assert citation.chunk_id


def test_query_tool_refuses_below_relevance_floor():
    response = rag_mcp_server.query(
        "What is the recommended dosage for treating unrelated pediatric asthma inhalers?"
    )
    assert response.status == Status.refused
    assert response.answer is None
    assert response.citations == []
    assert response.caveats


def test_browse_tool_filters_by_source_type_and_excludes_unapproved():
    items = rag_mcp_server.browse(SourceType.clinical_trial)
    assert len(items) >= 1
    for item in items:
        assert item.source_type == SourceType.clinical_trial
        assert item.approved is True
    assert all(item.document_id != "doc-ct-007" for item in items)


def test_browse_tool_without_filter_excludes_unapproved_docs():
    items = rag_mcp_server.browse()
    assert all(item.approved is True for item in items)
    unapproved_ids = {"doc-lit-005", "doc-pat-006", "doc-ct-007"}
    assert all(item.document_id not in unapproved_ids for item in items)


def test_mcp_tools_match_underlying_functions_exactly():
    """The MCP wrappers must not duplicate logic — same result as the
    functions main.py's HTTP endpoints call, for the same input."""
    from retrieval.answer import answer_query
    from retrieval.browse import browse_documents

    question = "What is the mechanism of action of semaglutide as a GLP-1 receptor agonist?"
    assert rag_mcp_server.query(question) == answer_query(question)
    assert rag_mcp_server.browse() == browse_documents()
