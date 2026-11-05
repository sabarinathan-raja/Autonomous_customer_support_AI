
from backend.graph.workflow import support_workflow


def test_customer_support_workflow():

    initial_state = {
        "customer_message": (
            "My order ORD-1042 has not arrived. "
            "I want to know the refund policy."
        )
    }

    result = support_workflow.invoke(initial_state)

    print("\n========== WORKFLOW RESULT ==========")

    print("Case ID:", result.get("case_id"))

    print("Intent:", result.get("intent"))

    print("Order ID:", result.get("order_id"))

    print("Order Details:", result.get("order_details"))

    print("Policy Evidence:", result.get("policy_evidence"))

    print("Compliance:", result.get("compliance_result"))

    print("Escalation:", result.get("escalation_result"))

    print("Final Response:", result.get("final_response"))

    assert result.get("final_response")


if __name__ == "__main__":

    test_customer_support_workflow()
