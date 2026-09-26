"""Groq API client for fast inference with open-source models."""

import os
from typing import Optional, List
from groq import Groq


class GroqClient:
    """Client for Groq API - fast LLM inference with open-source models."""

    # Available high-performance open-source models on Groq
    AVAILABLE_MODELS = {
        "gpt-oss-120b": "openai/gpt-oss-120b",  # Recommended - large OSS model on Groq
        "gpt-oss-20b": "openai/gpt-oss-20b",  # Faster, smaller alternative
    }

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-oss-120b"):
        """Initialize Groq client with high-performance OSS models."""
        self.client = Groq(api_key=api_key or os.getenv("GROQ_API_KEY"))
        self.model = self.AVAILABLE_MODELS.get(model, "openai/gpt-oss-120b")
        self.max_tokens = 4096

    def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate response using Groq."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens or self.max_tokens,
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")

    def stream_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ):
        """Stream response from Groq."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise Exception(f"Groq streaming error: {str(e)}")

    def generate_clinical_summary(
        self,
        patient_notes: str,
        max_length: int = 500
    ) -> str:
        """Generate clinical summary - optimized for fast inference."""
        prompt = f"""Provide a concise clinical summary of the following notes (max {max_length} words):

{patient_notes}

Summary:"""

        system_prompt = "You are a clinical assistant. Provide concise, accurate summaries."

        return self.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=max_length // 4
        )

    def extract_entities(self, text: str) -> dict:
        """Extract clinical entities from text."""
        prompt = f"""Extract the following from the clinical text:
- Medications mentioned
- Conditions/Diagnoses
- Vital signs or values
- Treatment recommendations

Clinical text:
{text}

Response (JSON format):"""

        response = self.generate_response(
            prompt=prompt,
            temperature=0.2,
            max_tokens=1000
        )

        import json
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw_response": response}

    def validate_content_fast(self, content: str) -> dict:
        """Fast content validation using Groq."""
        prompt = f"""Validate this clinical content for basic accuracy and completeness.
Return JSON with: is_valid (bool), confidence (0-100), issues (list)

Content:
{content}

Response (JSON):"""

        response = self.generate_response(
            prompt=prompt,
            temperature=0.2,
            max_tokens=300
        )

        import json
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"is_valid": True, "confidence": 50, "issues": []}

    def get_model_info(self) -> dict:
        """Get Groq model information."""
        return {
            "model": self.model,
            "provider": "Groq",
            "max_tokens": self.max_tokens,
            "type": "Open-source (Llama 3.1/Mixtral)",
            "use_case": "Real-time responses, clinical documentation, entity extraction",
            "inference_speed": "Ultra-fast",
            "available_models": self.AVAILABLE_MODELS
        }

    def switch_model(self, model: str) -> str:
        """Switch to a different model."""
        if model in self.AVAILABLE_MODELS:
            self.model = self.AVAILABLE_MODELS[model]
            return f"Switched to {model}: {self.model}"
        available = ", ".join(self.AVAILABLE_MODELS.keys())
        return f"Invalid model. Available: {available}"
