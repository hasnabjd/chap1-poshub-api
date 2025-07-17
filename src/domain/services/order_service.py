from typing import List
from uuid import UUID, uuid4

from src.domain.exceptions.order_exceptions import (
    OrderAlreadyExistsException,
    OrderNotFoundException,
)
from src.domain.schemas.order import OrderIn, OrderOut

# Global list to store orders
orders: List[OrderOut] = []


class OrderService:
    def create_order(self, order: OrderIn) -> OrderOut:
        order_id = uuid4()
        order_out = OrderOut(
            order=order_id,
            nom_client=order.customer_name,
            montant=order.total_amount,
            devise=order.currency
        )
        orders.append(order_out)
        return order_out

    def get_order(self, order_id: UUID) -> OrderOut:
        for order in orders:
            if order.order_id == order_id:
                return order
        raise OrderNotFoundException(f"Order {order_id} not found") 