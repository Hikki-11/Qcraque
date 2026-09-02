class CheckoutError(Exception):
    """Base exception for expected checkout failures."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ValidationError(CheckoutError):
    pass


class UserNotFoundError(CheckoutError):
    pass


class CartNotFoundError(CheckoutError):
    pass


class EmptyCartError(CheckoutError):
    pass


class AddressNotFoundError(CheckoutError):
    pass


class ProductNotFoundError(CheckoutError):
    pass


class ProductUnavailableError(CheckoutError):
    pass


class InsufficientStockError(CheckoutError):
    pass


class DatabaseError(CheckoutError):
    pass
