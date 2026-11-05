
import time
from google import genai
from google.genai import types

from backend.core.config import settings


class GeminiService:

    def __init__(self):

        if not settings.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is missing in .env file"
            )

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

        self.model = settings.GEMINI_MODEL

    def generate_response(
        self,
        prompt: str,
        system_instruction: str = "You are a helpful customer support AI assistant."
    ) -> str:

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
                max_output_tokens=2048
            )
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response")

        return response.text

    def close(self):
        self.client.close()

    
    def generate_json_response(self, prompt: str) -> str:

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
                max_output_tokens=2048
            )
        )

        if not response.text:
            raise RuntimeError(
                f"Gemini returned empty JSON response. "
                f"Finish reason: {response.candidates[0].finish_reason if response.candidates else 'No candidates'}"
            )

        return response.text

def get_llm_service():

    return GeminiService()
