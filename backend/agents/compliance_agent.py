
class ComplianceAgent:

    def validate(
        self,
        response,
        policy_evidence,
        order_details,
        order_id=None
    ):

        # Missing Order ID is a pending-information state,
        # not automatically a compliance failure.
        if not order_id:

            return {
                "passed": True,
                "violations": [],
                "human_review_required": False,
                "awaiting_order_id": True
            }

        violations = []

        if not order_details:
            violations.append("Order evidence is missing")

        if not policy_evidence:
            violations.append("Policy evidence is missing")

        if not response:
            violations.append("Response is empty")

        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "human_review_required": len(violations) > 0,
            "awaiting_order_id": False
        }
