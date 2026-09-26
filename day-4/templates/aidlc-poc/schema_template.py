"""Generic structured-response schema pattern for AIDLC POCs.

Fill in the enums and fields for the new domain, then keep this module and
`SKILLS.md`'s response-schema block in sync by hand — the triage agent checks
for drift between them.
"""
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class SourceType(str, Enum):
    """Replace with the new domain's document/source categories."""
    example_type_a = "example_type_a"
    example_type_b = "example_type_b"


class Confidence(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class Status(str, Enum):
    """The graceful-failure discriminator: generation must set one of these,
    never leave `answer` populated without `status == answered`."""
    answered = "answered"
    refused = "refused"
    escalated = "escalated"


class Citation(BaseModel):
    document_id: str
    chunk_id: str
    source_type: SourceType


class QueryResponse(BaseModel):
    answer: Optional[str] = None
    confidence: Confidence
    citations: list[Citation] = []
    caveats: list[str] = []
    status: Status


class BrowseItem(BaseModel):
    """List-only, no-generation browse entries — allowlist filter still
    applies (`approved` must be checked before returning any item)."""
    document_id: str
    title: str
    source_type: SourceType
    approved: bool
    version: str
