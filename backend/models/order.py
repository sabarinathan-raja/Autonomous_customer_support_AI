
from pydantic import BaseModel, ConfigDict
from typing import Optional


class OrderCreate(BaseModel):

    order_id: str

    customer_id: int

    status: str = "processing"

    tracking_status: Optional[str] = None


class OrderResponse(BaseModel):

    id: int

    order_id: str

    customer_id: int

    status: str

    tracking_status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
