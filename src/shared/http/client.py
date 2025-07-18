from typing import Any, Optional

import httpx
import structlog
from starlette.requests import Request
from tenacity import retry, stop_after_attempt, wait_exponential
from tenacity.retry import retry_if_exception_type

from src.shared.http.exceptions import NetworkError, ServerError, TimeoutError

logger = structlog.get_logger()


@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
    reraise=True,
)
async def safe_get(
    client: httpx.AsyncClient, url: str, *, params: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    """
    Safe GET request with retries and logging
    """
    try:
        logger.info("external_request.start", url=url, params=params)
        response = await client.get(url=url, params=params, timeout=10.0)
        response.raise_for_status()

        logger.info(
            "external_request.success",
            url=url,
            status_code=response.status_code,
            response_size=len(response.content),
        )
        return response.json()

    except httpx.TimeoutException as e:
        logger.error(
            "external_request.timeout", url=url, error=str(e), timeout_seconds=10.0
        )
        raise TimeoutError("Request timed out") from e

    except httpx.NetworkError as e:
        logger.error(
            "external_request.network_error",
            url=url,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise NetworkError("Network error occurred") from e

    except httpx.HTTPStatusError as e:
        if e.response.status_code >= 500:
            logger.error(
                "external_request.server_error",
                url=url,
                status_code=e.response.status_code,
                response_body=e.response.text[:500],  # Limit response body size
            )
            raise ServerError(
                f"External service error: {e.response.status_code}"
            ) from e

        logger.error(
            "external_request.client_error",
            url=url,
            status_code=e.response.status_code,
            response_body=e.response.text[:500],  # Limit response body size
        )
        raise


async def get_http_client(request: Request) -> httpx.AsyncClient:
    """
    Dependency of FastAPI to get the HTTP client from app state
    Used with Depends() on routers
    """
    if not hasattr(request.app.state, "http"):
        raise RuntimeError("HTTP client not initialized. Check lifespan configuration.")
    return request.app.state.http
