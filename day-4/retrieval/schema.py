from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel


class SourceType(str, Enum):
    literature = "literature"
    patent = "patent"
    clinical_trial = "clinical_trial"
    internal_report = "internal_report"


class Confidence(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class Status(str, Enum):
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


class OpenResearchResponse(BaseModel):
    answer: str
    mode: Literal["open_research"] = "open_research"
    model: str
    disclaimer: str = (
        "Ungrounded — generated from general model knowledge, no corpus "
        "citations, not verified against the allowlist."
    )


class BrowseItem(BaseModel):
    document_id: str
    title: str
    source_type: SourceType
    approved: bool
    version: str
    superseded_by: Optional[str] = None
