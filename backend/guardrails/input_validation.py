import re
from dataclasses import dataclass


@dataclass
class GuardrailResult:
    allowed: bool
    message: str
    reason: str = ""


class InputGuardrails:

    def __init__(self, max_input_length=5000):
        self.max_input_length = max_input_length

        self.injection_patterns = [
            r"ignore\s+(all\s+)?previous\s+instructions",
            r"ignore\s+(all\s+)?system\s+instructions",
            r"reveal\s+(your\s+)?system\s+prompt",
            r"show\s+(me\s+)?your\s+hidden\s+instructions",
            r"bypass\s+(all\s+)?safety",
            r"forget\s+(all\s+)?previous\s+instructions",
            r"override\s+(the\s+)?system\s+prompt",
        ]

    def validate_input(self, user_input):

        if not isinstance(user_input, str):
            return GuardrailResult(
                False,
                "Invalid input format.",
                "Input must be a string."
            )

        user_input = user_input.strip()

        if not user_input:
            return GuardrailResult(
                False,
                "Please enter a message.",
                "Empty input."
            )

        if len(user_input) > self.max_input_length:
            return GuardrailResult(
                False,
                "Your message is too long.",
                "Maximum input length exceeded."
            )

        normalized_input = re.sub(
            r"\s+", " ", user_input.lower()
        )

        for pattern in self.injection_patterns:
            if re.search(pattern, normalized_input):
                return GuardrailResult(
                    False,
                    "Your request contains suspicious instructions.",
                    "Possible prompt injection detected."
                )

        return GuardrailResult(
            True,
            "Input validation successful."
        )


input_guardrails = InputGuardrails()