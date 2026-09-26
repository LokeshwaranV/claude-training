"""Chat service for processing messages with Groq API."""

import os
from typing import Optional, List
from services.groq_client import GroqClient
from models.schemas import (
    ChatMessage, MessageRole, PatientContext, SpecialtyEnum, ValidationResult
)


class ChatService:
    """Service for handling chat interactions with Groq."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize chat service with Groq client."""
        self.groq_client = GroqClient(api_key=api_key or os.getenv("GROQ_API_KEY"))
        self.max_tokens = 2048

    def build_system_prompt(
        self,
        specialty: SpecialtyEnum,
        patient_context: Optional[PatientContext] = None
    ) -> str:
        """Build system prompt for clinical context."""
        base_prompt = f"""You are an expert clinical documentation assistant for {specialty.value.replace('_', ' ')} practices.
Your role is to help clinicians:
1. Draft accurate clinical notes
2. Summarize patient charts
3. Generate documentation
4. Validate clinical content

You prioritize accuracy, completeness, and HIPAA compliance.
Always maintain professional clinical language and evidence-based recommendations."""

        if patient_context:
            context_additions = f"""

CURRENT PATIENT CONTEXT:
- Patient: {patient_context.name}, Age {patient_context.age}
- Conditions: {', '.join(patient_context.conditions) if patient_context.conditions else 'None documented'}
- Current Medications: {', '.join(patient_context.medications) if patient_context.medications else 'None documented'}
- Allergies: {', '.join(patient_context.allergies) if patient_context.allergies else 'NKDA'}"""
            base_prompt += context_additions

        return base_prompt

    def process_message(
        self,
        user_message: str,
        conversation_history: List[ChatMessage],
        patient_context: Optional[PatientContext] = None,
        specialty: SpecialtyEnum = SpecialtyEnum.GENERAL_PRACTICE
    ) -> str:
        """Process user message and get response from Groq."""
        system_prompt = self.build_system_prompt(specialty, patient_context)

        # Build conversation context
        context = ""
        for msg in conversation_history[-5:]:  # Keep last 5 messages for context
            context += f"{msg.role.value.upper()}: {msg.content}\n"

        # Prepare full prompt
        full_prompt = f"{context}USER: {user_message}"

        # Call Groq API
        response = self.groq_client.generate_response(
            prompt=full_prompt,
            system_prompt=system_prompt,
            temperature=0.5,
            max_tokens=self.max_tokens
        )

        return response

    def generate_note(
        self,
        conversation_history: List[ChatMessage],
        patient_context: PatientContext,
        encounter_type: str = "office_visit",
        specialty: SpecialtyEnum = SpecialtyEnum.GENERAL_PRACTICE
    ) -> str:
        """Generate clinical note from conversation history."""
        system_prompt = self.build_system_prompt(specialty, patient_context)
        system_prompt += f"\n\nYou are now generating a formal {encounter_type} note."

        # Build conversation context
        conversation_text = "\n".join(
            [f"{msg.role.value.upper()}: {msg.content}" for msg in conversation_history]
        )

        prompt = f"""Based on the following conversation, generate a comprehensive clinical note:

{conversation_text}

Please provide:
1. Chief Complaint
2. History of Present Illness
3. Review of Systems
4. Physical Examination
5. Assessment and Plan
6. Medical Decision Making"""

        response = self.groq_client.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=3000
        )

        return response

    def validate_clinical_content(
        self,
        content: str,
        specialty: SpecialtyEnum = SpecialtyEnum.GENERAL_PRACTICE
    ) -> ValidationResult:
        """Validate clinical content for accuracy and completeness."""
        validation_prompt = f"""You are a clinical documentation validator for {specialty.value.replace('_', ' ')}.
Validate the following clinical content and provide:
1. A validity score (0-100)
2. Any errors or concerns
3. Any warnings or suggestions

Clinical Content to Validate:
{content}

Respond in JSON format:
{{
    "is_valid": boolean,
    "score": number,
    "errors": [list of errors],
    "warnings": [list of warnings]
}}"""

        response = self.groq_client.generate_response(
            prompt=validation_prompt,
            temperature=0.2,
            max_tokens=500
        )

        import json
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            return ValidationResult(**data)
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                score=0,
                errors=[str(e)]
            )

    def summarize_chart(
        self,
        chart_data: str,
        patient_context: PatientContext,
        specialty: SpecialtyEnum = SpecialtyEnum.GENERAL_PRACTICE
    ) -> str:
        """Summarize patient chart data."""
        system_prompt = self.build_system_prompt(specialty, patient_context)
        system_prompt += "\n\nYou are summarizing patient chart data for quick review."

        prompt = f"""Please provide a concise summary of the following patient chart data:

{chart_data}

Include:
1. Key findings
2. Current active problems
3. Recent treatments/interventions
4. Follow-up needed"""

        response = self.groq_client.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=1500
        )

        return response
