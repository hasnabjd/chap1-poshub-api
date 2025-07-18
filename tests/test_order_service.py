import uuid
from uuid import UUID

import pytest

from src.domain.exceptions.order_exceptions import OrderNotFoundException
from src.domain.schemas.order import OrderIn, OrderOut
from src.domain.services.order_service import OrderService, orders


class TestOrderService:
    """Tests pour le service de commandes"""

    def setup_method(self):
        """Nettoyer les commandes avant chaque test"""
        orders.clear()
        self.service = OrderService()

    def test_create_order_success(self):
        """Test création réussie d'une commande"""
        # Arrange
        order_data = OrderIn(
            customer_name="John Doe", total_amount=99.99, currency="EUR"
        )

        # Act
        result = self.service.create_order(order_data)

        # Assert
        assert isinstance(result, OrderOut)
        assert result.customer_name == "John Doe"
        assert result.total_amount == 99.99
        assert result.currency == "EUR"
        assert isinstance(result.order_id, UUID)
        assert len(orders) == 1

    def test_get_order_success(self):
        """Test récupération réussie d'une commande"""
        # Arrange
        order_data = OrderIn(customer_name="Jane", total_amount=150.0, currency="GBP")
        created_order = self.service.create_order(order_data)

        # Act
        result = self.service.get_order(created_order.order_id)

        # Assert
        assert result.order_id == created_order.order_id
        assert result.customer_name == "Jane"
        assert result.total_amount == 150.0
        assert result.currency == "GBP"

    def test_get_order_not_found(self):
        """Test récupération d'une commande inexistante"""
        # Arrange
        non_existent_id = uuid.uuid4()

        # Act & Assert
        with pytest.raises(OrderNotFoundException) as exc_info:
            self.service.get_order(non_existent_id)

        assert str(non_existent_id) in str(exc_info.value)
        assert "not found" in str(exc_info.value)
