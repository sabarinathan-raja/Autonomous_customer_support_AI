
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class TicketCreate(BaseModel):

    customer_id: int
    order_id: Optional[str] = None
    customer_message: str = Field(..., min_length=1)
    intent: Optional[str] = None
    priority: str = "normal"
    status: str = "open"
    escalation_reason: Optional[str] = None


class TicketResponse(BaseModel):

    id: int
    ticket_id: str
    customer_id: int
    order_id: Optional[str] = None
    customer_message: str
    intent: Optional[str] = None
    priority: str
    status: str
    escalation_reason: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketUpdate(BaseModel):

    status: Optional[str] = None
    priority: Optional[str] = None
    escalation_reason: Optional[str] = None
