
from time import perf_counter
from uuid import uuid4
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.models.ticket import TicketUpdate
from backend.database.connection import SessionLocal

from backend.database.crud import (
    create_ticket,
    create_evaluation,
    get_all_evaluations,
    get_evaluation_summary
)

from backend.database.tables import (
    Customer,
    Ticket,
    AuditLog,
    ConversationMessage,
    EvaluationHistory
)

from backend.graph.workflow import support_workflow
from evaluation.evaluator import evaluate_response


router = APIRouter(
    prefix="/api",
    tags=["Customer Support"]
)


# =====================================================
# REQUEST AND RESPONSE MODELS
# =====================================================

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    case_id: Optional[str] = None
    ticket_id: Optional[str] = None


class ChatResponse(BaseModel):
    case_id: Optional[str] = None
    ticket_id: Optional[str] = None
    intent: Optional[str] = None
    order_id: Optional[str] = None
    priority: Optional[str] = None
    final_response: str
    evaluation: Optional[dict] = None
    awaiting_order_id: bool = False


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def get_continuation_ticket(db, case_id, ticket_id):

    if not case_id or not ticket_id:
        raise HTTPException(
            status_code=400,
            detail="Both Case ID and Ticket ID are required."
        )

    linked_audit = db.query(AuditLog).filter(
        AuditLog.case_id == case_id,
        AuditLog.ticket_id == ticket_id
    ).first()

    if not linked_audit:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )

    ticket = db.query(Ticket).filter(
        Ticket.ticket_id == ticket_id
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found."
        )

    return ticket


def extract_raw_order_id(message):

    value = message.strip()

    if (
        3 <= len(value) <= 50
        and not any(character.isspace() for character in value)
    ):
        return value

    return None


def save_conversation_messages(
    db,
    case_id,
    ticket_id,
    user_message,
    assistant_message
):

    db.add_all([
        ConversationMessage(
            case_id=case_id,
            ticket_id=ticket_id,
            role="user",
            content=user_message
        ),
        ConversationMessage(
            case_id=case_id,
            ticket_id=ticket_id,
            role="assistant",
            content=assistant_message
        )
    ])

    db.commit()


def validate_conversation(db, case_id, ticket_id):

    linked = db.query(AuditLog).filter(
        AuditLog.case_id == case_id,
        AuditLog.ticket_id == ticket_id
    ).first()

    if not linked:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )

    ticket = db.query(Ticket).filter(
        Ticket.ticket_id == ticket_id
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found."
        )

    return ticket


# =====================================================
# CUSTOMER CHAT API
# =====================================================

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    start_time = perf_counter()
    db = SessionLocal()

    try:

        # 1. NEW CONVERSATION OR CONTINUATION

        is_continuation = bool(
            request.case_id or request.ticket_id
        )

        if is_continuation:

            existing_ticket = get_continuation_ticket(
                db,
                request.case_id,
                request.ticket_id
            )

            case_id = request.case_id
            ticket_id = existing_ticket.ticket_id

            if existing_ticket.status in ["resolved", "escalated"]:
                raise HTTPException(
                    status_code=400,
                    detail="This ticket is closed. Start a new conversation."
                )

        else:

            case_id = str(uuid4())
            ticket_id = None
            existing_ticket = None

        # 2. ORDER ID EXTRACTION

        supplied_order_id = None

        if is_continuation:
            supplied_order_id = extract_raw_order_id(
                request.message
            )

        # 3. INITIAL WORKFLOW STATE

        initial_state = {
            "customer_message": request.message,
            "case_id": case_id,
            "intent": "",
            "order_id": supplied_order_id,
            "priority": (
                existing_ticket.priority
                if existing_ticket
                else "normal"
            ),
            "missing_information": [],
            "order_details": {},
            "policy_evidence": [],
            "resolution": "",
            "compliance_result": {},
            "escalation_result": {},
            "final_response": "",
            "error": None
        }

        agent_names = {
            "intake": "Intake Agent",
            "intent": "Intent Agent",
            "investigation": "Investigation Agent",
            "policy": "Policy Retrieval Agent",
            "resolution": "Resolution Agent",
            "compliance": "Compliance Agent",
            "escalation": "Escalation Agent",
            "final_response": "Final Response Agent"
        }

        result = dict(initial_state)

        # 4. EXECUTE WORKFLOW

        previous_node_time = perf_counter()

        for update in support_workflow.stream(
            initial_state,
            stream_mode="updates"
        ):

            for node_name, node_output in update.items():

                result.update(node_output)

                execution_time = (
                    perf_counter() - previous_node_time
                )

                previous_node_time = perf_counter()

                agent_name = agent_names.get(
                    node_name,
                    node_name
                )

                db.add(
                    AuditLog(
                        case_id=case_id,
                        ticket_id=ticket_id,
                        agent_name=agent_name,
                        action=f"{agent_name} executed",
                        status="success",
                        execution_time=execution_time,
                        details=(
                            "Agent execution completed. "
                            f"Output keys: {list(node_output.keys())}"
                        )
                    )
                )

                db.commit()

        result["case_id"] = case_id

        # 5. ORDER INVESTIGATION

        order_result = result.get(
            "order_details",
            {}
        ) or {}

        order = (
            order_result.get("order")
            if order_result.get("success")
            else None
        )

        order_id = result.get("order_id")

        awaiting_order_id = (
            not order_id
            or not order_result.get("success")
        )

        # 6. FINAL RESPONSE

        if not order_id:

            generated_answer = (
                "I can help you investigate your order. "
                "Please share your Order ID so I can check "
                "the verified order and tracking details."
            )

        elif not order_result.get("success"):

            generated_answer = (
                "I could not verify the order using the "
                "Order ID you provided. Please check the "
                "Order ID and send it again."
            )

        else:

            generated_answer = result.get(
                "final_response",
                "No response received."
            )

        # 7. POLICY CONTEXT

        policy_evidence = result.get(
            "policy_evidence",
            []
        )

        if isinstance(policy_evidence, list):

            retrieved_contexts = [
                str(item)
                for item in policy_evidence
            ]

            policy_context = "\n".join(
                retrieved_contexts
            )

        else:

            policy_context = str(policy_evidence)
            retrieved_contexts = [policy_context]

        # 8. EVALUATION

        evaluation_results = evaluate_response(
            customer_question=request.message,
            generated_answer=generated_answer,
            policy_context=policy_context,
            retrieved_contexts=retrieved_contexts,
            relevant_keywords=[],
            expected_keywords=[],
            start_time=start_time
        )

        # 9. CUSTOMER IDENTIFICATION

        if existing_ticket:

            customer_id = existing_ticket.customer_id

            if (
                order
                and order.get("customer_id") != customer_id
            ):
                raise HTTPException(
                    status_code=403,
                    detail="This Order ID does not belong to the current customer."
                )

        else:

            customer_id = (
                order.get("customer_id")
                if order
                else 1
            )

        customer = db.query(Customer).filter(
            Customer.id == customer_id
        ).first()

        if not customer:
            raise HTTPException(
                status_code=400,
                detail="Customer record not found."
            )

        # 10. CREATE OR UPDATE TICKET

        escalation = result.get(
            "escalation_result",
            {}
        ) or {}

        if awaiting_order_id:
            ticket_status = "awaiting_order_id"

        elif escalation.get("escalate"):
            ticket_status = "escalated"

        else:
            ticket_status = "open"

        if existing_ticket:

            existing_ticket.customer_message = request.message
            existing_ticket.order_id = order_id

            existing_ticket.intent = result.get(
                "intent",
                existing_ticket.intent
            )

            existing_ticket.priority = result.get(
                "priority",
                existing_ticket.priority
            )

            existing_ticket.status = ticket_status

            existing_ticket.escalation_reason = (
                escalation.get("reason")
                if ticket_status == "escalated"
                else None
            )

            db.commit()
            db.refresh(existing_ticket)

            ticket_id = existing_ticket.ticket_id

        else:

            ticket_id = f"TKT-{uuid4().hex[:8].upper()}"

            ticket_data = {
                "ticket_id": ticket_id,
                "customer_id": customer.id,
                "order_id": order_id,
                "customer_message": request.message,
                "intent": result.get("intent"),
                "priority": result.get("priority", "normal"),
                "status": ticket_status,
                "escalation_reason": (
                    escalation.get("reason")
                    if ticket_status == "escalated"
                    else None
                )
            }

            create_ticket(db, ticket_data)

        # 11. LINK AUDIT LOGS

        db.query(AuditLog).filter(
            AuditLog.case_id == case_id
        ).update(
            {"ticket_id": ticket_id},
            synchronize_session=False
        )

        db.commit()

        # 12. SAVE CONVERSATION MESSAGES

        save_conversation_messages(
            db=db,
            case_id=case_id,
            ticket_id=ticket_id,
            user_message=request.message,
            assistant_message=generated_answer
        )

        # 13. SAVE EVALUATION HISTORY

        evaluation_data = {
            "case_id": case_id,
            "ticket_id": ticket_id,
            "customer_question": request.message,
            "generated_answer": generated_answer,
            "answer_relevance": evaluation_results.get(
                "answer_relevance"
            ),
            "faithfulness": evaluation_results.get(
                "faithfulness"
            ),
            "context_precision": evaluation_results.get(
                "context_precision"
            ),
            "context_recall": evaluation_results.get(
                "context_recall"
            ),
            "overall_score": evaluation_results.get(
                "overall_score"
            ),
            "response_time_seconds": evaluation_results.get(
                "response_time_seconds"
            )
        }

        create_evaluation(db, evaluation_data)

        print("Workflow completed successfully")
        print("Case ID:", case_id)
        print("Ticket ID:", ticket_id)
        print("Order ID:", order_id)

        return ChatResponse(
            case_id=case_id,
            ticket_id=ticket_id,
            intent=result.get("intent"),
            order_id=order_id,
            priority=result.get("priority"),
            final_response=generated_answer,
            evaluation=evaluation_results,
            awaiting_order_id=awaiting_order_id
        )

    except HTTPException:

        db.rollback()
        raise

    except Exception as error:

        db.rollback()

        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Workflow execution failed: {str(error)}"
        )

    finally:

        db.close()


# =====================================================
# CONVERSATION HISTORY APIs
# =====================================================

@router.get("/conversations")
def get_conversations():

    db = SessionLocal()

    try:

        links = db.query(
            AuditLog.case_id,
            AuditLog.ticket_id
        ).filter(
            AuditLog.case_id.isnot(None),
            AuditLog.ticket_id.isnot(None)
        ).distinct().all()

        conversations = []

        for case_id, ticket_id in links:

            ticket = db.query(Ticket).filter(
                Ticket.ticket_id == ticket_id
            ).first()

            if not ticket:
                continue

            last_message = db.query(
                ConversationMessage
            ).filter(
                ConversationMessage.case_id == case_id,
                ConversationMessage.ticket_id == ticket_id
            ).order_by(
                ConversationMessage.created_at.desc()
            ).first()

            conversations.append({
                "case_id": case_id,
                "ticket_id": ticket_id,
                "order_id": ticket.order_id,
                "status": ticket.status,
                "priority": ticket.priority,
                "last_message": (
                    last_message.content
                    if last_message
                    else ticket.customer_message
                ),
                "created_at": (
                    ticket.created_at.isoformat()
                    if ticket.created_at
                    else None
                )
            })

        conversations.sort(
            key=lambda item: item["created_at"] or "",
            reverse=True
        )

        return conversations

    finally:

        db.close()


@router.get("/conversations/{case_id}/{ticket_id}")
def get_conversation_history(
    case_id: str,
    ticket_id: str
):

    db = SessionLocal()

    try:

        ticket = validate_conversation(
            db,
            case_id,
            ticket_id
        )

        messages = db.query(
            ConversationMessage
        ).filter(
            ConversationMessage.case_id == case_id,
            ConversationMessage.ticket_id == ticket_id
        ).order_by(
            ConversationMessage.created_at.asc(),
            ConversationMessage.id.asc()
        ).all()

        evaluations = db.query(
            EvaluationHistory
        ).filter(
            EvaluationHistory.case_id == case_id,
            EvaluationHistory.ticket_id == ticket_id
        ).order_by(
            EvaluationHistory.created_at.asc(),
            EvaluationHistory.id.asc()
        ).all()

        # Match each evaluation to its assistant response.
        evaluation_index = 0
        history_messages = []

        for message in messages:

            evaluation = None

            if message.role == "assistant":

                if evaluation_index < len(evaluations):

                    item = evaluations[evaluation_index]

                    evaluation = {
                        "answer_relevance": item.answer_relevance,
                        "faithfulness": item.faithfulness,
                        "context_precision": item.context_precision,
                        "context_recall": item.context_recall,
                        "overall_score": item.overall_score,
                        "response_time_seconds": item.response_time_seconds
                    }

                    evaluation_index += 1

            history_messages.append({
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "evaluation": evaluation,
                "created_at": (
                    message.created_at.isoformat()
                    if message.created_at
                    else None
                )
            })

        return {
            "case_id": case_id,
            "ticket_id": ticket_id,
            "order_id": ticket.order_id,
            "status": ticket.status,
            "messages": history_messages
        }

    finally:

        db.close()


# =====================================================
# DASHBOARD SUMMARY API
# =====================================================

@router.get("/dashboard/summary")
def dashboard_summary():

    db = SessionLocal()

    try:

        total = db.query(Ticket).count()

        resolved = db.query(Ticket).filter(
            Ticket.status == "resolved"
        ).count()

        escalated = db.query(Ticket).filter(
            Ticket.status == "escalated"
        ).count()

        pending = db.query(Ticket).filter(
            Ticket.status.in_([
                "open",
                "pending",
                "in_progress",
                "awaiting_order_id"
            ])
        ).count()

        return {
            "total_tickets": total,
            "resolved_tickets": resolved,
            "pending_tickets": pending,
            "escalated_tickets": escalated
        }

    finally:

        db.close()


# =====================================================
# TICKET APIs
# =====================================================

@router.get("/tickets")
def get_tickets():

    db = SessionLocal()

    try:

        tickets = db.query(Ticket).order_by(
            Ticket.created_at.desc()
        ).all()

        return [
            {
                "ticket_id": ticket.ticket_id,
                "customer_id": ticket.customer_id,
                "order_id": ticket.order_id,
                "customer_message": ticket.customer_message,
                "intent": ticket.intent,
                "priority": ticket.priority,
                "status": ticket.status,
                "escalation_reason": ticket.escalation_reason
            }
            for ticket in tickets
        ]

    finally:

        db.close()


@router.put("/tickets/{ticket_id}")
def update_ticket_status(
    ticket_id: str,
    request: TicketUpdate
):

    db = SessionLocal()

    try:

        ticket = db.query(Ticket).filter(
            Ticket.ticket_id == ticket_id
        ).first()

        if not ticket:
            raise HTTPException(
                status_code=404,
                detail="Ticket not found"
            )

        if request.status is not None:

            allowed_statuses = [
                "open",
                "awaiting_order_id",
                "in_progress",
                "resolved",
                "escalated"
            ]

            if request.status not in allowed_statuses:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid ticket status"
                )

            ticket.status = request.status

        if request.priority is not None:
            ticket.priority = request.priority

        if request.escalation_reason is not None:
            ticket.escalation_reason = request.escalation_reason

        db.commit()
        db.refresh(ticket)

        return {
            "message": "Ticket updated successfully",
            "ticket_id": ticket.ticket_id,
            "status": ticket.status,
            "priority": ticket.priority
        }

    finally:

        db.close()


# =====================================================
# ESCALATION API
# =====================================================

@router.get("/escalations")
def get_escalations():

    db = SessionLocal()

    try:

        tickets = db.query(Ticket).filter(
            Ticket.status == "escalated"
        ).order_by(
            Ticket.created_at.desc()
        ).all()

        return [
            {
                "ticket_id": ticket.ticket_id,
                "customer_id": ticket.customer_id,
                "order_id": ticket.order_id,
                "customer_message": ticket.customer_message,
                "priority": ticket.priority,
                "status": ticket.status,
                "escalation_reason": ticket.escalation_reason
            }
            for ticket in tickets
        ]

    finally:

        db.close()


# =====================================================
# EVALUATION HISTORY API
# =====================================================

@router.get("/evaluation/history")
def evaluation_history():

    db = SessionLocal()

    try:

        evaluations = get_all_evaluations(db)

        return [
            {
                "id": item.id,
                "case_id": item.case_id,
                "ticket_id": item.ticket_id,
                "customer_question": item.customer_question,
                "generated_answer": item.generated_answer,
                "answer_relevance": item.answer_relevance,
                "faithfulness": item.faithfulness,
                "context_precision": item.context_precision,
                "context_recall": item.context_recall,
                "overall_score": item.overall_score,
                "response_time_seconds": item.response_time_seconds,
                "created_at": (
                    item.created_at.isoformat()
                    if item.created_at
                    else None
                )
            }
            for item in evaluations
        ]

    finally:

        db.close()


# =====================================================
# EVALUATION SUMMARY API
# =====================================================

@router.get("/evaluation/summary")
def evaluation_summary():

    db = SessionLocal()

    try:

        return get_evaluation_summary(db)

    finally:

        db.close()


# =====================================================
# AUDIT LOGS API
# =====================================================

@router.get("/audit-logs")
def get_audit_logs():

    db = SessionLocal()

    try:

        logs = db.query(AuditLog).order_by(
            AuditLog.created_at.desc()
        ).all()

        return [
            {
                "id": log.id,
                "case_id": log.case_id,
                "ticket_id": log.ticket_id,
                "agent_name": log.agent_name,
                "action": log.action,
                "status": log.status,
                "execution_time": log.execution_time,
                "details": log.details,
                "created_at": (
                    log.created_at.isoformat()
                    if log.created_at
                    else None
                )
            }
            for log in logs
        ]

    finally:

        db.close()
