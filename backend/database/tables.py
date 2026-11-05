from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Float
)

from backend.database.connection import Base


class Customer(Base):

    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    email = Column(String(150), unique=True, index=True)

    phone = Column(String(20), nullable=True)


class Order(Base):

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(String(50), unique=True, index=True)

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False
    )

    status = Column(String(50), default="processing")

    tracking_status = Column(String(100), nullable=True)


class Ticket(Base):

    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)

    ticket_id = Column(String(50), unique=True, index=True)

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False
    )

    order_id = Column(String(50), nullable=True)

    customer_message = Column(Text, nullable=False)

    intent = Column(String(100), nullable=True)

    priority = Column(String(30), default="normal")

    status = Column(String(50), default="open")

    escalation_reason = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


class ConversationMessage(Base):

    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, index=True)

    case_id = Column(
        String(100),
        nullable=False,
        index=True
    )

    ticket_id = Column(
        String(50),
        nullable=False,
        index=True
    )

    role = Column(
        String(20),
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )


class EvaluationHistory(Base):

    __tablename__ = "evaluation_history"

    id = Column(Integer, primary_key=True, index=True)

    case_id = Column(String(100), nullable=False, index=True)

    ticket_id = Column(String(50), nullable=True, index=True)

    customer_question = Column(Text, nullable=False)

    generated_answer = Column(Text, nullable=False)

    answer_relevance = Column(Float, nullable=True)

    faithfulness = Column(Float, nullable=True)

    context_precision = Column(Float, nullable=True)

    context_recall = Column(Float, nullable=True)

    overall_score = Column(Float, nullable=True)

    response_time_seconds = Column(Float, nullable=True)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


class AuditLog(Base):

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    case_id = Column(String(100), nullable=True, index=True)

    ticket_id = Column(String(50), nullable=True, index=True)

    agent_name = Column(String(100), nullable=False)

    action = Column(String(200), nullable=False)

    status = Column(String(30), nullable=False)

    execution_time = Column(Float, nullable=True)

    details = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


class APIMonitorLog(Base):

    __tablename__ = "api_monitor_logs"

    id = Column(Integer, primary_key=True, index=True)

    method = Column(String(10), nullable=False)

    endpoint = Column(String(300), nullable=False, index=True)

    status_code = Column(Integer, nullable=False, index=True)

    response_time_ms = Column(Float, nullable=False)

    error = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )