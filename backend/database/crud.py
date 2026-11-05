
from sqlalchemy.orm import Session

from backend.database.tables import (
    Customer,
    Order,
    Ticket,
    EvaluationHistory
)


# -------------------------------
# CUSTOMER CRUD
# -------------------------------

def get_customer(db: Session, customer_id: int):

    return db.query(Customer).filter(
        Customer.id == customer_id
    ).first()


def create_customer(db: Session, customer_data: dict):

    customer = Customer(**customer_data)

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


# -------------------------------
# ORDER CRUD
# -------------------------------

def get_order(db: Session, order_id: str):

    return db.query(Order).filter(
        Order.order_id == order_id
    ).first()


def create_order(db: Session, order_data: dict):

    order = Order(**order_data)

    db.add(order)
    db.commit()
    db.refresh(order)

    return order


# -------------------------------
# TICKET CRUD
# -------------------------------

def create_ticket(db: Session, ticket_data: dict):

    ticket = Ticket(**ticket_data)

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket


def get_ticket(db: Session, ticket_id: str):

    return db.query(Ticket).filter(
        Ticket.ticket_id == ticket_id
    ).first()


def get_all_tickets(db: Session):

    return db.query(Ticket).order_by(
        Ticket.created_at.desc()
    ).all()


# -------------------------------
# EVALUATION CRUD
# -------------------------------

def create_evaluation(db: Session, evaluation_data: dict):

    evaluation = EvaluationHistory(**evaluation_data)

    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)

    return evaluation


def get_all_evaluations(db: Session):

    return db.query(EvaluationHistory).order_by(
        EvaluationHistory.created_at.desc()
    ).all()


def get_evaluation_summary(db: Session):

    evaluations = db.query(EvaluationHistory).all()

    total = len(evaluations)

    if total == 0:
        return {
            "total_evaluations": 0,
            "average_answer_relevance": 0,
            "average_faithfulness": 0,
            "average_context_precision": 0,
            "average_response_time": 0
        }

    def average(field):

        values = [
            getattr(item, field)
            for item in evaluations
            if getattr(item, field) is not None
        ]

        return round(sum(values) / len(values), 4) if values else 0

    return {
        "total_evaluations": total,
        "average_answer_relevance": average("answer_relevance"),
        "average_faithfulness": average("faithfulness"),
        "average_context_precision": average("context_precision"),
        "average_context_recall": average("context_recall"),
        "average_overall_score": average("overall_score"),
        "average_response_time": average("response_time_seconds")
    }
