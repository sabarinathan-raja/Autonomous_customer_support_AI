
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from backend.core.config import settings


class Base(DeclarativeBase):
    pass


database_url = settings.DATABASE_URL

connect_args = {}

if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}


engine = create_engine(
    database_url,
    connect_args=connect_args,
    echo=False
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def migrate_evaluation_table():

    if not database_url.startswith("sqlite"):
        return

    inspector = inspect(engine)

    if not inspector.has_table("evaluation_history"):
        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("evaluation_history")
    }

    new_columns = {
        "context_recall": "FLOAT",
        "overall_score": "FLOAT"
    }

    with engine.begin() as connection:

        for column_name, column_type in new_columns.items():

            if column_name not in existing_columns:

                connection.execute(
                    text(
                        f"ALTER TABLE evaluation_history "
                        f"ADD COLUMN {column_name} {column_type}"
                    )
                )

                print(
                    f"Database migration: Added {column_name}"
                )


def init_db():

    from backend.database import tables

    # Create missing tables
    Base.metadata.create_all(bind=engine)

    # Add missing evaluation columns
    migrate_evaluation_table()

    print("Database initialized successfully!")

    return True
