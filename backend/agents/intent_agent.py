
import json
import re

from backend.services.llm_service import get_llm_service


class IntentAgent:

    def __init__(self):
        self.llm = get_llm_service()

    def classify(self, message: str):

        prompt = f"""
Classify the customer support message.

Choose exactly one intent:
- delayed_order
- refund
- cancellation
- damaged_product
- payment_issue
- account_issue
- other

Priority must be normal, high, or urgent.

Return only a valid JSON object:

{{
    "intent": "delayed_order",
    "priority": "normal",
    "reason": "Order delivery is delayed"
}}

Customer message:
{message}
"""

        response = self.llm.generate_json_response(prompt)

        if not response or not response.strip():
            raise ValueError("Intent Agent received empty response")

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

            allowed_intents = {
                "delayed_order",
                "refund",
                "cancellation",
                "damaged_product",
                "payment_issue",
                "account_issue",
                "other"
            }

            if result.get("intent") not in allowed_intents:
                raise ValueError("Invalid intent category")

            if result.get("priority") not in {
                "normal", "high", "urgent"
            }:
                raise ValueError("Invalid priority")

            if not result.get("reason"):
                raise ValueError("Missing classification reason")

            return result

        except (json.JSONDecodeError, ValueError) as error:
            raise ValueError(
                f"Intent Agent parsing failed: {error}. "
                f"Raw response: {response[:500]!r}"
            ) from error

    def close(self):
        self.llm.close()
