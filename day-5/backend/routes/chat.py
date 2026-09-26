"""Chat API routes."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
from models.schemas import (
    ChatRequest, ChatResponse, GenerateNoteRequest, GenerateNoteResponse,
    ValidationResult, MessageRole, PatientContext, SpecialtyEnum
)
from services.chat_service import ChatService
from session.manager import SessionManager

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Initialize services
chat_service = ChatService()
session_manager = SessionManager()


@router.post("/message", response_model=ChatResponse)
async def process_message(request: ChatRequest) -> ChatResponse:
    """Process a chat message and return response."""
    try:
        # Get or create session
        if request.session_id:
            session = session_manager.get_session(request.session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            session_id = request.session_id
        else:
            session_id = session_manager.create_session(
                user_id="default_user",
                patient_id=request.patient_context.patient_id if request.patient_context else "unknown",
                specialty=request.specialty
            )

        # Get conversation history
        history = session_manager.get_conversation_history(session_id)

        # Process message with Claude
        response = chat_service.process_message(
            user_message=request.message,
            conversation_history=history,
            patient_context=request.patient_context,
            specialty=request.specialty
        )

        # Store messages in session
        session_manager.add_message(session_id, MessageRole.USER, request.message)
        session_manager.add_message(session_id, MessageRole.ASSISTANT, response)

        return ChatResponse(
            session_id=session_id,
            message=request.message,
            response=response
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-note", response_model=GenerateNoteResponse)
async def generate_note(request: GenerateNoteRequest) -> GenerateNoteResponse:
    """Generate clinical note from conversation history."""
    try:
        session = session_manager.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Build patient context from request
        patient_context = PatientContext(
            patient_id=request.patient_id,
            name="Patient",
            age=0,
            conditions=[],
            medications=[],
            allergies=[]
        )

        # Generate note
        note_content = chat_service.generate_note(
            conversation_history=session.messages,
            patient_context=patient_context,
            encounter_type=request.encounter_type,
            specialty=request.specialty
        )

        # Validate generated note
        validation = chat_service.validate_clinical_content(
            content=note_content,
            specialty=request.specialty
        )

        return GenerateNoteResponse(
            note_id=f"note_{request.session_id}",
            note_content=note_content,
            template_used=request.encounter_type,
            validation_score=validation.score
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}")
async def get_history(session_id: str, limit: int = 50) -> dict:
    """Get conversation history for a session."""
    try:
        history = session_manager.get_conversation_history(session_id)
        if not history:
            raise HTTPException(status_code=404, detail="Session not found")

        # Return limited history
        messages = [
            {
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in history[-limit:]
        ]

        return {"session_id": session_id, "messages": messages}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate")
async def validate_content(content: str, specialty: SpecialtyEnum = SpecialtyEnum.GENERAL_PRACTICE) -> ValidationResult:
    """Validate clinical content."""
    try:
        result = chat_service.validate_clinical_content(
            content=content,
            specialty=specialty
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize")
async def summarize_chart(
    chart_data: str,
    patient_id: str,
    specialty: SpecialtyEnum = SpecialtyEnum.GENERAL_PRACTICE
) -> dict:
    """Summarize patient chart data."""
    try:
        patient_context = PatientContext(
            patient_id=patient_id,
            name="Patient",
            age=0
        )

        summary = chat_service.summarize_chart(
            chart_data=chart_data,
            patient_context=patient_context,
            specialty=specialty
        )

        return {
            "patient_id": patient_id,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{session_id}")
async def delete_session(session_id: str) -> dict:
    """End a session."""
    try:
        success = session_manager.end_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"session_id": session_id, "status": "ended"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
