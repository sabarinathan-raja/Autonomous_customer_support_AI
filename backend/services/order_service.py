
from sqlalchemy.orm import Session

from backend.database.crud import get_order


class OrderService:

    def __init__(self, db: Session):
        self.db = db

    def investigate_order(self, order_id: str):

        order = get_order(self.db, order_id)

        if not order:
            return {
                "success": False,
                "message": "Order not found",
                "order": None
            }

        return {
            "success": True,
            "message": "Order retrieved successfully",
            "order": {
                "order_id": order.order_id,
                "status": order.status,
                "tracking_status": order.tracking_status,
                "customer_id": order.customer_id
            }
        }
