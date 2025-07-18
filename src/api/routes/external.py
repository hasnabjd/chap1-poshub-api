from typing import Annotated, Any

from fastapi import APIRouter, Depends
from httpx import AsyncClient

from src.shared.http.client import get_http_client, safe_get

router = APIRouter(tags=["external"])


@router.get("/external-demo")
async def external_demo(
    client: Annotated[AsyncClient, Depends(get_http_client)],
) -> dict[str, Any]:
    """
    Demo endpoint that calls httpbin.org
    """
    # Quand une exception n'est pas capturée dans une route
    # Elle "remonte" automatiquement vers FastAPI
    return await safe_get(client, "https://httpbin.org/get", params={"demo": "SMCP"})
