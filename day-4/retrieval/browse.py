"""Shared allowlist-filtered browse listing (Step 14 extraction).

Previously this filter lived inline in `main.py`'s `/browse` handler. It is
pulled out here so the HTTP endpoint and the Step 14 MCP `browse` tool call
one implementation instead of duplicating the allowlist/source_type filter
logic (commitment 1 and commitment 5 in SKILLS.md).
"""

from __future__ import annotations

from ingestion.seed_data import SEED_DOCUMENTS
from retrieval.schema import BrowseItem, SourceType


def browse_documents(source_type: SourceType | None = None) -> list[BrowseItem]:
    """List-only, allowlist-filtered browse across source types. No generation."""
    return [
        BrowseItem(
            document_id=doc["document_id"],
            title=doc["title"],
            source_type=SourceType(doc["source_type"]),
            approved=doc["approved"],
            version=doc["version"],
            superseded_by=doc.get("superseded_by"),
        )
        for doc in SEED_DOCUMENTS
        if doc["approved"] and (source_type is None or doc["source_type"] == source_type.value)
    ]
