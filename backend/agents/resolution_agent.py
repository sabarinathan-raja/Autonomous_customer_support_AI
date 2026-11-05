
from backend.services.llm_service import get_llm_service


class ResolutionAgent:

    def __init__(self):
        self.llm = get_llm_service()

    def generate_resolution(
        self,
        customer_message,
        order_details,
        policy_evidence
    ):

        prompt = f"""
You are a professional customer support resolution agent.

Customer message:
{customer_message}

Verified order details:
{order_details}

Retrieved policy evidence:
{policy_evidence}

Instructions:

1. Use only verified order information.
2. Explain the actual order and tracking status.
3. Never invent tracking information.
4. Do not invent refund eligibility.
5. Do not promise unauthorized actions.
6. If information is unavailable, clearly explain that.
7. Give a clear and natural customer response.
"""

        return self.llm.generate_response(prompt)

    def close(self):
        self.llm.close()
