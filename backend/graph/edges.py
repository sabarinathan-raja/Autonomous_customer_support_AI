
def route_after_investigation(state):
    order_id = state.get("order_id")

    if not order_id or not str(order_id).strip():
        return "final_response"

    return "policy"


def route_after_compliance(state):
    compliance_result = state.get("compliance_result", {})
    priority = str(state.get("priority", "normal")).lower()

    if (
        compliance_result.get("human_review_required", False)
        or priority in {"high", "urgent"}
    ):
        return "escalation"

    return "final_response"


def get_next_edges():
    return {
        "escalation": "escalation",
        "final_response": "final_response"
    }
