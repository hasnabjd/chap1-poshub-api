from contextlib import asynccontextmanager
from typing import AsyncGenerator

import httpx
from fastapi import FastAPI
from mangum import Mangum
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api.middleware.correlation_id import (
    CorrelationIdMiddleware,
    configure_structlog,
)
from src.api.middleware.error_handler import (
    http_exception_handler,
    network_exception_handler,
    server_exception_handler,
    timeout_exception_handler,
)
from src.api.routes.auth import router as auth_router
from src.api.routes.external import router as external_router
from src.api.routes.orders import router as orders_router
from src.shared.config.settings import get_settings
from src.shared.http.exceptions import NetworkError, ServerError, TimeoutError
from src.shared.utils.ssm_utils import get_api_key_from_ssm
import structlog


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Configure structured logging
    configure_structlog()
    
    # Get configuration settings
    settings = get_settings()
    
    # Create HTTP client
    async with httpx.AsyncClient() as client:
        app.state.http = client
        
        # Read API key from SSM and log it (warning: don't do this in production!)
        try:
            print("🔍 Starting SSM parameter retrieval...")  # Debug print
            api_key = get_api_key_from_ssm(settings.API_KEY_PARAM)
            logger = structlog.get_logger(__name__)
            logger.info(f"API key retrieved from SSM parameter: {settings.API_KEY_PARAM}")
            logger.info(f"API key value: {api_key}")  # ⚠️ WARNING: Don't log secrets in production!
            print(f"✅ SSM parameter retrieved: {api_key}")  # Debug print
        except Exception as e:
            logger = structlog.get_logger(__name__)
            logger.error(f"Failed to retrieve API key from SSM: {e}")
            print(f"❌ SSM error: {e}")  # Debug print
        
        yield


app = FastAPI(
    title="PosHub API",
    description="API for PosHub application",
    version="1.0.0",
    lifespan=lifespan,
)

# Add correlation ID middleware (must be added before other middlewares)
app.add_middleware(CorrelationIdMiddleware)

# Register exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(TimeoutError, timeout_exception_handler)
app.add_exception_handler(NetworkError, network_exception_handler)
app.add_exception_handler(ServerError, server_exception_handler)

# Include routers
app.include_router(auth_router)
app.include_router(orders_router)
app.include_router(external_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


# Mangum handler for AWS Lambda
handler = Mangum(app, lifespan="off")
