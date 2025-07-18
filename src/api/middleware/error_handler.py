import uuid
from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api.middleware.correlation_id import get_correlation_id
from src.shared.http.exceptions import NetworkError, ServerError, TimeoutError
from src.shared.schemas.error import ErrorDetail, ErrorResponse


def create_error_response(
    status_code: int, error_type: str, code: str, message: str, request_id: str = None
) -> dict[str, Any]:
    """Create a standardized error response"""
    if request_id is None:
        # Try to get correlation ID from context, fallback to UUID
        request_id = get_correlation_id() or f"req_{uuid.uuid4().hex[:8]}"

    error_response = ErrorResponse(
        status_code=status_code,
        error_type=error_type,
        details=[ErrorDetail(code=code, message=message)],
        request_id=request_id,
    )

    return error_response.model_dump()


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Handle HTTP exceptions with custom error format"""
    # Use correlation ID from context
    request_id = get_correlation_id() or f"req_{uuid.uuid4().hex[:8]}"

    # Map HTTP status codes to error types
    error_type_mapping = {
        400: "VALIDATION_ERROR",
        401: "AUTHENTICATION_ERROR",
        403: "AUTHORIZATION_ERROR",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_SERVER_ERROR",
        502: "EXTERNAL_SERVICE_ERROR",
        504: "TIMEOUT_ERROR",
    }

    error_type = error_type_mapping.get(exc.status_code, "UNKNOWN_ERROR")

    error_response = create_error_response(
        status_code=exc.status_code,
        error_type=error_type,
        code=f"HTTP_{exc.status_code}",
        message=str(exc.detail),
        request_id=request_id,
    )

    return JSONResponse(status_code=exc.status_code, content=error_response)


async def timeout_exception_handler(
    request: Request, exc: TimeoutError
) -> JSONResponse:
    """Handle timeout exceptions"""
    error_response = create_error_response(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        error_type="TIMEOUT_ERROR",
        code="REQUEST_TIMEOUT",
        message=str(exc),
    )

    return JSONResponse(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT, content=error_response
    )


async def network_exception_handler(
    request: Request, exc: NetworkError
) -> JSONResponse:
    """Handle network exceptions"""
    error_response = create_error_response(
        status_code=status.HTTP_502_BAD_GATEWAY,
        error_type="NETWORK_ERROR",
        code="NETWORK_FAILURE",
        message=str(exc),
    )

    return JSONResponse(status_code=status.HTTP_502_BAD_GATEWAY, content=error_response)


async def server_exception_handler(request: Request, exc: ServerError) -> JSONResponse:
    """Handle server exceptions"""
    error_response = create_error_response(
        status_code=status.HTTP_502_BAD_GATEWAY,
        error_type="EXTERNAL_SERVICE_ERROR",
        code="SERVER_ERROR",
        message=str(exc),
    )

    return JSONResponse(status_code=status.HTTP_502_BAD_GATEWAY, content=error_response)
