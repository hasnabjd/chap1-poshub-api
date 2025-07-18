class OrderAlreadyExistsException(Exception):
    """Raised when attempting to create an order that already exists"""

    pass


class OrderNotFoundException(Exception):
    """Raised when an order is not found"""

    pass
