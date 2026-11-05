from dataclasses import dataclass


@dataclass
class OutputValidationResult:
    allowed: bool
    message: str
    reason: str = ""


class OutputGuardrails:

    def validate_output(self, response):

        if not isinstance(response, str):
            return OutputValidationResult(
                False,
                "Invalid AI response.",
                "Response must be a string."
            )

        response = response.strip()

        if not response:
            return OutputValidationResult(
                False,
                "Unable to generate a response.",
                "Empty AI response."
            )

        if len(response) > 10000:
            return OutputValidationResult(
                False,
                "Response is too long.",
                "Maximum output length exceeded."
            )

        return OutputValidationResult(
            True,
            "Output validation successful."
        )


output_guardrails = OutputGuardrails()