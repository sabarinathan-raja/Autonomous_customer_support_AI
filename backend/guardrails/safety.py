
from dataclasses import dataclass


@dataclass
class SafetyCheckResult:
    safe: bool
    message: str
    reason: str = ""


class SafetyGuardrails:

    def __init__(self):

        self.blocked_patterns = [
            "kill yourself",
            "how to make a bomb",
            "how to hack someone's account",
            "steal someone's password",
        ]

        self.max_response_length = 10000

    def check_input(self, user_input):

        if not isinstance(user_input, str):
            return SafetyCheckResult(
                False,
                "Invalid input.",
                "Input must be a string."
            )

        text = user_input.lower()

        for pattern in self.blocked_patterns:

            if pattern in text:
                return SafetyCheckResult(
                    False,
                    "This request cannot be processed.",
                    "Unsafe content detected."
                )

        return SafetyCheckResult(
            True,
            "Input passed safety checks."
        )

    def check_output(self, response):

        if not isinstance(response, str):
            return SafetyCheckResult(
                False,
                "Invalid response.",
                "Response must be a string."
            )

        if len(response.strip()) > self.max_response_length:
            return SafetyCheckResult(
                False,
                "Response exceeds the allowed length.",
                "Output length exceeded."
            )

        if not response.strip():
            return SafetyCheckResult(
                False,
                "Unable to generate a response.",
                "Empty response."
            )

        return SafetyCheckResult(
            True,
            "Output passed safety checks."
        )


safety_guardrails = SafetyGuardrails()
