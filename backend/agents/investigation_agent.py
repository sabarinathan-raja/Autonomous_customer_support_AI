
from backend.services.order_service import OrderService


class InvestigationAgent:

    def __init__(self, db):
        self.order_service = OrderService(db)

    def investigate(self, order_id: str):

        if not order_id:
            return {
                "success": False,
                "message": "Order ID is missing",
                "order": None
            }

        return self.order_service.investigate_order(order_id)
