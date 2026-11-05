from backend.database.connection import SessionLocal, init_db
from backend.database.crud import create_customer, create_order
from backend.database.crud import get_order, get_customer


def seed_database():

    init_db()

    db = SessionLocal()

    try:
        customer = get_customer(db, 1)

        if not customer:
            customer = create_customer(
                db,
                {
                    "name": "Arun Kumar",
                    "email": "arun@example.com",
                    "phone": "9876543210"
                }
            )

        order = get_order(db, "ORD-1042")

        if not order:
            create_order(
                db,
                {
                    "order_id": "ORD-1042",
                    "customer_id": customer.id,
                    "status": "delayed",
                    "tracking_status": "In Transit"
                }
            )

        print("Mock customer and order seeded successfully!")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()