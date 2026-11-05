
import logging
import secrets
import time
from collections import defaultdict, deque

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from backend.core.config import settings


security_logger = logging.getLogger("security")

security_logger.setLevel(logging.INFO)

if not security_logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - SECURITY - %(levelname)s - %(message)s"
        )
    )
    security_logger.addHandler(handler)


class APISecurityMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)

        self.request_history = defaultdict(deque)

        self.exempt_paths = {
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json"
        }

    async def dispatch(self, request: Request, call_next):

        path = request.url.path

        if request.method == "OPTIONS":
            return await call_next(request)

        if path in self.exempt_paths:
            return await call_next(request)

        # API Key Authentication

        api_key = settings.API_KEY

        if not api_key:
            security_logger.error(
                "API_KEY is missing from environment configuration"
            )

            return JSONResponse(
                status_code=503,
                content={
                    "detail": "API security is not configured."
                }
            )

        received_key = request.headers.get("X-API-Key", "")

        if not received_key or not secrets.compare_digest(
            received_key,
            api_key
        ):

            client_ip = (
                request.client.host
                if request.client
                else "unknown"
            )

            security_logger.warning(
                "Unauthorized request | IP=%s | Path=%s",
                client_ip,
                path
            )

            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Invalid or missing API key."
                }
            )

        # Rate Limiting

        client_ip = (
            request.client.host
            if request.client
            else "unknown"
        )

        current_time = time.monotonic()

        history = self.request_history[client_ip]

        window_seconds = settings.RATE_LIMIT_WINDOW_SECONDS

        while history and (
            current_time - history[0]
        ) >= window_seconds:
            history.popleft()

        if len(history) >= settings.RATE_LIMIT_REQUESTS:

            security_logger.warning(
                "Rate limit exceeded | IP=%s | Path=%s",
                client_ip,
                path
            )

            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please try again later."
                },
                headers={
                    "Retry-After": str(window_seconds)
                }
            )

        history.append(current_time)

        return await call_next(request)
