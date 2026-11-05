
from backend.agents.intake_agent import IntakeAgent
from backend.agents.intent_agent import IntentAgent
from backend.agents.investigation_agent import InvestigationAgent
from backend.agents.policy_agent import PolicyAgent
from backend.agents.resolution_agent import ResolutionAgent
from backend.agents.compliance_agent import ComplianceAgent
from backend.agents.escalation_agent import EscalationAgent

from backend.database.connection import SessionLocal


def intake_node(state):

    agent = IntakeAgent()

    try:
        result = agent.process(state["customer_message"])

        # Preserve Order ID supplied during conversation continuation
        order_id = (
            state.get("order_id")
            or result.get("order_id")
        )

        missing_information = result.get(
            "missing_information",
            []
        )

        if not order_id:
            if "order_id" not in missing_information:
                missing_information.append("order_id")

        else:
            missing_information = [
                item for item in missing_information
                if item != "order_id"
            ]

        return {
            "case_id": state.get("case_id"),
            "order_id": order_id,
            "priority": result.get("priority", "normal"),
            "missing_information": missing_information
        }

    finally:
        agent.close()


def intent_node(state):

    agent = IntentAgent()

    try:
        result = agent.classify(state["customer_message"])

        return {
            "intent": result["intent"],
            "priority": result.get(
                "priority",
                state.get("priority", "normal")
            )
        }

    finally:
        agent.close()


def investigation_node(state):

    order_id = state.get("order_id")

    if not order_id:
        return {
            "order_details": {
                "success": False,
                "message": "Order ID is required",
                "order": None
            }
        }

    db = SessionLocal()

    try:
        agent = InvestigationAgent(db)
        result = agent.investigate(order_id)

        return {
            "order_details": result
        }

    finally:
        db.close()


def policy_node(state):

    agent = PolicyAgent()

    result = agent.retrieve_policy(
        state["customer_message"]
    )

    return {
        "policy_evidence": result.get("evidence", [])
    }


def resolution_node(state):

    # Ask for missing Order ID instead of generating an unsupported answer
    if not state.get("order_id"):

        return {
            "resolution": (
                "I can help you investigate your order. "
                "Please share your Order ID so I can check "
                "the verified order and tracking details."
            )
        }

    order_details = state.get("order_details", {})

    if not order_details.get("success"):

        return {
            "resolution": (
                "I could not verify the order using the supplied Order ID. "
                "Please check the Order ID and send it again."
            )
        }

    evidence = state.get("policy_evidence", [])

    agent = ResolutionAgent()

    try:
        result = agent.generate_resolution(
            customer_message=state["customer_message"],
            order_details=order_details,
            policy_evidence=evidence
        )

        return {
            "resolution": result
        }

    finally:
        agent.close()


def compliance_node(state):

    agent = ComplianceAgent()

    order_result = state.get("order_details", {})

    order = (
        order_result.get("order")
        if order_result.get("success")
        else None
    )

    result = agent.validate(
        response=state.get("resolution"),
        policy_evidence=state.get("policy_evidence"),
        order_details=order,
        order_id=state.get("order_id")
    )

    return {
        "compliance_result": result
    }


def escalation_node(state):

    agent = EscalationAgent()

    result = agent.evaluate(
        compliance_result=state["compliance_result"],
        priority=state.get("priority", "normal")
    )

    return {
        "escalation_result": result
    }


def final_response_node(state):

    escalation = state.get("escalation_result", {})

    if not state.get("order_id"):

        message = state.get("resolution", "")

    elif escalation.get("escalate"):

        message = (
            "Your request requires additional human review. "
            "Our support team needs to verify the details "
            "before confirming a resolution."
        )

    else:

        message = state.get("resolution", "")

    return {
        "final_response": message
    }
