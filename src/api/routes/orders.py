from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from src.api.dependencies.auth import AuthenticatedUser, RequireOrdersRead, RequireOrdersWrite
from src.domain.exceptions.order_exceptions import (
    OrderAlreadyExistsException,
    OrderNotFoundException,
)
from src.domain.schemas.order import OrderIn, OrderOut
from src.domain.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])

order_service = OrderService()

def get_order_service() -> OrderService:
    return order_service


@router.post("", status_code=status.HTTP_201_CREATED, response_model=OrderOut)
async def create_order(
    order: OrderIn,
    service: Annotated[OrderService, Depends(get_order_service)],
    current_user: Annotated[AuthenticatedUser, RequireOrdersWrite]
) -> OrderOut:
    try:
        return service.create_order(order)
    except OrderAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: UUID,
    service: Annotated[OrderService, Depends(get_order_service)],
    current_user: Annotated[AuthenticatedUser, RequireOrdersRead]
) -> OrderOut:
    try:
        return service.get_order(order_id)
    except OrderNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format"
        ) 