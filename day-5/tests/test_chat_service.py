"""Tests for chat service."""

import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from services.chat_service import ChatService
from models.schemas import (
    ChatMessage, MessageRole, PatientContext, SpecialtyEnum
)


@pytest.fixture
def chat_service():
    """Create chat service instance."""
    return ChatService()


@pytest.fixture
def patient_context():
    """Create sample patient context."""
    return PatientContext(
        patient_id="P001",
        name="John Doe",
        age=45,
        gender="M",
        conditions=["Hypertension", "Type 2 Diabetes"],
        medications=["Lisinopril 10mg daily", "Metformin 500mg BID"],
        allergies=["Penicillin"]
    )


def test_chat_service_initialization(chat_service):
    """Test chat service initialization."""
    assert chat_service is not None
    assert chat_service.model == "claude-3-5-sonnet-20241022"
    assert chat_service.max_tokens == 2048


def test_build_system_prompt_basic(chat_service):
    """Test system prompt building without patient context."""
    prompt = chat_service.build_system_prompt(SpecialtyEnum.GENERAL_PRACTICE)
    assert "clinical documentation assistant" in prompt.lower()
    assert "general practice" in prompt.lower()


def test_build_system_prompt_with_patient(chat_service, patient_context):
    """Test system prompt building with patient context."""
    prompt = chat_service.build_system_prompt(
        SpecialtyEnum.CARDIOLOGY,
        patient_context
    )
    assert "cardiology" in prompt.lower()
    assert patient_context.name in prompt
    assert "Hypertension" in prompt


def test_chat_message_creation():
    """Test chat message creation."""
    msg = ChatMessage(
        role=MessageRole.USER,
        content="Hello, doctor"
    )
    assert msg.role == MessageRole.USER
    assert msg.content == "Hello, doctor"
    assert msg.timestamp is not None


def test_patient_context_creation(patient_context):
    """Test patient context creation."""
    assert patient_context.patient_id == "P001"
    assert patient_context.name == "John Doe"
    assert patient_context.age == 45
    assert len(patient_context.conditions) == 2
    assert "Penicillin" in patient_context.allergies


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
