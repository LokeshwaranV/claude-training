"""Data models and schemas for the Elation Health Chat Bot."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SpecialtyEnum(str, Enum):
    """Medical specialties."""
    GENERAL_PRACTICE = "general_practice"
    CARDIOLOGY = "cardiology"
    NEUROLOGY = "neurology"
    DERMATOLOGY = "dermatology"
    PEDIATRICS = "pediatrics"
    PSYCHIATRY = "psychiatry"


class MessageRole(str, Enum):
    """Chat message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class PatientContext(BaseModel):
    """Patient clinical context."""
    patient_id: str
    name: str
    age: int
    gender: Optional[str] = None
    conditions: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    last_visit: Optional[datetime] = None


class ChatMessage(BaseModel):
    """Single chat message."""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    """Request for chat processing."""
    message: str
    session_id: Optional[str] = None
    patient_context: Optional[PatientContext] = None
    specialty: SpecialtyEnum = SpecialtyEnum.GENERAL_PRACTICE


class ChatResponse(BaseModel):
    """Response from chat processing."""
    session_id: str
    message: str
    response: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    confidence: Optional[float] = None


class GenerateNoteRequest(BaseModel):
    """Request for clinical note generation."""
    session_id: str
    patient_id: str
    encounter_type: str = "office_visit"
    specialty: SpecialtyEnum = SpecialtyEnum.GENERAL_PRACTICE


class GenerateNoteResponse(BaseModel):
    """Generated clinical note."""
    note_id: str
    note_content: str
    template_used: str
    validation_score: float
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Session(BaseModel):
    """Chat session."""
    session_id: str
    user_id: str
    patient_id: str
    specialty: SpecialtyEnum
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ValidationResult(BaseModel):
    """Clinical content validation result."""
    is_valid: bool
    score: float = Field(ge=0, le=100)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
