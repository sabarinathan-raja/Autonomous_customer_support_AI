
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from time import perf_counter

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from backend.database.connection import init_db, engine
from backend.api.routes import router

from backend.core.api_monitoring import (
    APIMonitoringMiddleware,
    api_monitor
)

from backend.core.security import APISecurityMiddleware
from backend.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):

    init_db()

    print("Database initialized successfully!")
    print("Customer Support AI Backend Ready!")

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Multi-Agent Customer Support and Escalation System",
    version=settings.VERSION,
    lifespan=lifespan
)


# API Monitoring Middleware

app.add_middleware(APISecurityMiddleware)


# API Security Middleware

app.add_middleware(APIMonitoringMiddleware)


# CORS Middleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key"]
)


# API Router

app.include_router(router)


@app.get("/health")
def health_check():

    database_status = "healthy"
    database_response_time = None
    database_message = "Database connection successful"

    start_time = perf_counter()

    try:

        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        database_response_time = round(
            (perf_counter() - start_time) * 1000, 2
        )

    except Exception as error:

        database_status = "unhealthy"
        database_message = str(error)

    overall_status = (
        "healthy"
        if database_status == "healthy"
        else "degraded"
    )

    return {
        "status": overall_status,
        "application": settings.PROJECT_NAME,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "api": {
                "status": "healthy",
                "message": "FastAPI backend is running"
            },
            "database": {
                "status": database_status,
                "message": database_message,
                "response_time_ms": database_response_time
            },
            "workflow": {
                "status": "available",
                "message": "LangGraph workflow is registered"
            }
        }
    }


@app.get("/api/monitoring/summary")
def get_api_monitoring_summary():

    return api_monitor.get_summary()
