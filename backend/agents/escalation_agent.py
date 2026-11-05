
class EscalationAgent:

    def evaluate(self, compliance_result, priority="normal"):

        violations = compliance_result.get("violations", [])
        priority = str(priority).lower()

        escalate = (
            not compliance_result.get("passed", False)
            or priority in {"high", "urgent"}
        )

        if violations:
            reason = ", ".join(violations)
        elif priority in {"high", "urgent"}:
            reason = f"{priority.capitalize()} priority case"
        else:
            reason = "No escalation required"

        return {
            "escalate": escalate,
            "queue": "human_support" if escalate else None,
            "reason": reason
        }
