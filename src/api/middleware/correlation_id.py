import uuid
from contextvars import ContextVar
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Context variable to store correlation ID across request
correlation_id_context: ContextVar[str] = ContextVar("correlation_id", default=None)

logger = structlog.get_logger()


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle X-Correlation-ID header and logging context
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract correlation ID from headers or generate a new one
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = f"req_{uuid.uuid4().hex[:12]}"

        # Store correlation ID in context
        correlation_id_context.set(correlation_id)

        # Log request start
        logger.info(
            "request.start",
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
            correlation_id=correlation_id,
            user_agent=request.headers.get("User-Agent", ""),
            client_ip=request.client.host if request.client else None,
        )

        # Process request
        response = await call_next(request)

        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id

        # Log request end
        logger.info(
            "request.end",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            correlation_id=correlation_id,
        )

        return response


def get_correlation_id() -> str:
    """Get the current correlation ID from context"""
    return correlation_id_context.get()


def configure_structlog():
    """Configure structlog with correlation ID processor"""

    def add_correlation_id(logger, method_name, event_dict):
        """Add correlation ID to all log entries"""
        correlation_id = correlation_id_context.get()
        if correlation_id:
            event_dict["correlation_id"] = correlation_id
        return event_dict

    structlog.configure(
        processors=[
            add_correlation_id,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
