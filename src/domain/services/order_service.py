from typing import List
from uuid import UUID, uuid4

import structlog

from src.domain.exceptions.order_exceptions import (
    OrderAlreadyExistsException,
    OrderNotFoundException,
)
from src.domain.schemas.order import OrderIn, OrderOut

# Global list to store orders
orders: List[OrderOut] = []

logger = structlog.get_logger()


class OrderService:
    def create_order(self, order: OrderIn) -> OrderOut:
        logger.info(
            "order.create.start",
            customer_name=order.customer_name,
            amount=order.total_amount,
            currency=order.currency
        )
        
        order_id = uuid4()
        order_out = OrderOut(
            order_id=order_id,
            customer_name=order.customer_name,
            total_amount=order.total_amount,
            currency=order.currency
        )
        orders.append(order_out)
        
        logger.info(
            "order.create.success",
            order_id=str(order_id),
            customer_name=order.customer_name,
            amount=order.total_amount,
            currency=order.currency
        )
        
        return order_out

    def get_order(self, order_id: UUID) -> OrderOut:
        logger.info("order.get.start", order_id=str(order_id))
        
        for order in orders:
            if order.order_id == order_id:
                logger.info(
                    "order.get.success",
                    order_id=str(order_id),
                    customer_name=order.customer_name
                )
                return order
        
        logger.warning("order.get.not_found", order_id=str(order_id))
        raise OrderNotFoundException(f"Order {order_id} not found") 