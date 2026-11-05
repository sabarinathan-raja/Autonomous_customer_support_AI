
import json
import re
from uuid import uuid4

from backend.services.llm_service import get_llm_service


class IntakeAgent:

    def __init__(self):
        self.llm = get_llm_service()

    def process(self, customer_message: str):

        case_id = str(uuid4())

        prompt = f"""
Analyze this customer support message.

Return only valid JSON.

Required format:
{{
    "case_id": "{case_id}",
    "intent": "delayed_order",
    "order_id": null,
    "issue": "Customer issue",
    "priority": "normal",
    "missing_information": []
}}

Rules:
- Extract order ID if present.
- Use null if order ID is missing.
- Priority: normal, high, urgent.
- Do not invent information.
- Return JSON only.

Customer message:
{customer_message}
"""

        response = self.llm.generate_json_response(prompt)

        if not response or not response.strip():
            raise ValueError("Intake Agent received empty response")

        try:
            cleaned = re.sub(
                r"```(?:json)?\s*|\s*```",
                "",
                response,
                flags=re.IGNORECASE
            ).strip()

            start = cleaned.find("{")
            end = cleaned.rfind("}")

            if start == -1 or end == -1:
                raise ValueError("JSON object not found")

            result = json.loads(cleaned[start:end + 1])

            required_fields = [
                "case_id",
                "intent",
                "order_id",
                "issue",
                "priority",
                "missing_information"
            ]

            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing field: {field}")

            if result["priority"] not in {
                "normal", "high", "urgent"
            }:
                raise ValueError("Invalid priority")

            if not isinstance(result["missing_information"], list):
                raise ValueError("missing_information must be a list")

            result["case_id"] = case_id

            return result

        except (json.JSONDecodeError, ValueError) as error:
            raise ValueError(
                f"Intake Agent parsing failed: {error}. "
                f"Raw response: {response[:500]!r}"
            ) from error

    def close(self):
        self.llm.close()
