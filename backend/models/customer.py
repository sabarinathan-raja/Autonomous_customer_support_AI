
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional


class CustomerCreate(BaseModel):

    name: str

    email: EmailStr

    phone: Optional[str] = None


class CustomerResponse(BaseModel):

    id: int

    name: str

    email: EmailStr

    phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
