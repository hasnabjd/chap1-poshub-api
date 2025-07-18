from contextlib import asynccontextmanager
from typing import AsyncGenerator

import httpx
from fastapi import FastAPI
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
from src.shared.http.exceptions import NetworkError, ServerError, TimeoutError


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Configure structured logging
    configure_structlog()
    
    # Create HTTP client
    async with httpx.AsyncClient() as client:
        app.state.http = client
        yield


app = FastAPI(
    title="PosHub API",
    description="API for PosHub application",
    version="1.0.0",
    lifespan=lifespan
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