
from dataclasses import dataclass


@dataclass
class PolicyCheckResult:
    allowed: bool
    message: str
    reason: str = ""


class PolicyChecker:

    def __init__(self):

        self.sensitive_requests = [
            "share your password",
            "send your password",
            "share your otp",
            "send your otp",
            "share your cvv",
            "send your cvv",
            "share your credit card pin",
            "send your credit card pin",
        ]

        self.unauthorized_commitments = [
            "your refund has been processed",
            "your refund is guaranteed",
            "your claim is approved",
            "your payment has been reversed",
            "your order has been cancelled",
        ]

    def check_input(self, user_input):

        if not isinstance(user_input, str):
            return PolicyCheckResult(
                False,
                "Invalid input.",
                "Input must be a string."
            )

        text = user_input.lower()

        for phrase in self.sensitive_requests:
            if phrase in text:
                return PolicyCheckResult(
                    False,
                    "Please do not share passwords, OTPs or card PINs.",
                    "Sensitive information request detected."
                )

        return PolicyCheckResult(
            True,
            "Input passed policy checks."
        )

    def check_output(self, response, verified_actions=None):

        if not isinstance(response, str):
            return PolicyCheckResult(
                False,
                "Invalid AI response.",
                "Response must be a string."
            )

        text = response.lower()
        verified_actions = verified_actions or []

        for phrase in self.unauthorized_commitments:

            if phrase in text and phrase not in verified_actions:
                return PolicyCheckResult(
                    False,
                    "I cannot confirm this action without verification.",
                    "Potential unauthorized commitment detected."
                )

        return PolicyCheckResult(
            True,
            "Output passed policy checks."
        )


policy_checker = PolicyChecker()
