
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:

    PROJECT_NAME = "Autonomous Customer Support AI"

    VERSION = "1.0.0"

    API_HOST = os.getenv("API_HOST", "127.0.0.1")

    API_PORT = int(os.getenv("API_PORT", "8000"))

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    GEMINI_MODEL = os.getenv(
        "GEMINI_MODEL",
        "gemini-2.5-flash"
    )

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./customer_support.db"
    )

    VECTOR_DB_PATH = "data/vectorstore"

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # API Security

    API_KEY = os.getenv("API_KEY", "")

    # Rate Limiting

    RATE_LIMIT_REQUESTS = int(
        os.getenv("RATE_LIMIT_REQUESTS", "60")
    )

    RATE_LIMIT_WINDOW_SECONDS = int(
        os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60")
    )

    # CORS

    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:8501,http://127.0.0.1:8501"
        ).split(",")
        if origin.strip()
    ]


settings = Settings()
