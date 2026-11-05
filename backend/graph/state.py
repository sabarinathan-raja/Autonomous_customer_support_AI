
from typing import TypedDict, Optional, Any


class SupportState(TypedDict, total=False):

    customer_message: str

    case_id: str

    intent: str

    order_id: Optional[str]

    priority: str

    missing_information: list

    order_details: dict

    policy_evidence: list

    resolution: str

    compliance_result: dict

    escalation_result: dict

    final_response: str

    error: Optional[str]
