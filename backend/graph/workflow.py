
from time import perf_counter

from langgraph.graph import StateGraph, START, END

from backend.graph.state import SupportState

from backend.graph.nodes import (
    intake_node,
    intent_node,
    investigation_node,
    policy_node,
    resolution_node,
    compliance_node,
    escalation_node,
    final_response_node
)

from backend.graph.edges import (
    route_after_investigation,
    route_after_compliance
)

from backend.database.connection import SessionLocal
from backend.database.tables import AuditLog


def timed_node(node_name, node_function):

    def wrapper(state):

        start_time = perf_counter()
        db = SessionLocal()

        try:
            result = node_function(state)

            execution_time = perf_counter() - start_time

            audit_record = AuditLog(
                case_id=state.get("case_id"),
                agent_name=node_name,
                action=f"{node_name} executed",
                status="success",
                execution_time=execution_time,
                details="Agent execution completed successfully"
            )

            db.add(audit_record)
            db.commit()

            return result

        except Exception as error:

            execution_time = perf_counter() - start_time

            audit_record = AuditLog(
                case_id=state.get("case_id"),
                agent_name=node_name,
                action=f"{node_name} execution failed",
                status="failed",
                execution_time=execution_time,
                details=str(error)
            )

            db.add(audit_record)
            db.commit()

            raise

        finally:
            db.close()

    return wrapper


def build_support_workflow():

    graph = StateGraph(SupportState)

    graph.add_node(
        "intake",
        timed_node("Intake Agent", intake_node)
    )

    graph.add_node(
        "intent",
        timed_node("Intent Agent", intent_node)
    )

    graph.add_node(
        "investigation",
        timed_node("Investigation Agent", investigation_node)
    )

    graph.add_node(
        "policy",
        timed_node("Policy Retrieval Agent", policy_node)
    )

    graph.add_node(
        "resolution",
        timed_node("Resolution Agent", resolution_node)
    )

    graph.add_node(
        "compliance",
        timed_node("Compliance Agent", compliance_node)
    )

    graph.add_node(
        "escalation",
        timed_node("Escalation Agent", escalation_node)
    )

    graph.add_node(
        "final_response",
        timed_node("Final Response Agent", final_response_node)
    )

    graph.add_edge(START, "intake")
    graph.add_edge("intake", "intent")
    graph.add_edge("intent", "investigation")

    graph.add_conditional_edges(
        "investigation",
        route_after_investigation,
        {
            "policy": "policy",
            "final_response": "final_response"
        }
    )

    graph.add_edge("policy", "resolution")
    graph.add_edge("resolution", "compliance")

    graph.add_conditional_edges(
        "compliance",
        route_after_compliance,
        {
            "escalation": "escalation",
            "final_response": "final_response"
        }
    )

    graph.add_edge("escalation", "final_response")
    graph.add_edge("final_response", END)

    return graph.compile()


support_workflow = build_support_workflow()
