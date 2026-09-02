from fastapi import Request
from fastapi.responses import JSONResponse
from app.exceptions import (
    AddressNotFoundError,
    CartNotFoundError,
    EmptyCartError,
    InsufficientStockError,
    ProductNotFoundError,
    ProductUnavailableError,
    UserNotFoundError,
    ValidationError,
)


def _response(status_code: int, error: str, message: str):
    return JSONResponse(
        status_code=status_code,
        content={"error": error, "message": message},
    )


async def validation_error_handler(request: Request, exc: ValidationError):
    return _response(400, "validation_error", exc.message)


async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    return _response(404, "user_not_found", exc.message)


async def cart_not_found_handler(request: Request, exc: CartNotFoundError):
    return _response(404, "cart_not_found", exc.message)


async def empty_cart_handler(request: Request, exc: EmptyCartError):
    return _response(400, "empty_cart", exc.message)


async def address_not_found_handler(request: Request, exc: AddressNotFoundError):
    return _response(404, "address_not_found", exc.message)


async def product_not_found_handler(request: Request, exc: ProductNotFoundError):
    return _response(404, "product_not_found", exc.message)


async def product_unavailable_handler(request: Request, exc: ProductUnavailableError):
    return _response(409, "product_unavailable", exc.message)


async def insufficient_stock_handler(request: Request, exc: InsufficientStockError):
    return _response(409, "insufficient_stock", exc.message)
