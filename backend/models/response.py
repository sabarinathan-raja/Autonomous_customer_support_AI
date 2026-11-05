
from pydantic import BaseModel, Field
from typing import Optional, List


class AgentResponse(BaseModel):

    agent_name: str

    status: str

    message: str


class SupportResponse(BaseModel):

    case_id: str

    intent: str

    priority: str

    verified_facts: List[str] = Field(default_factory=list)

    evidence: List[str] = Field(default_factory=list)

    decision: str

    customer_message: str

    human_review_required: bool = False

    escalation_reason: Optional[str] = None

    agents: List[AgentResponse] = Field(default_factory=list)
