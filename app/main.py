from fastapi import FastAPI

from app.exceptions import (
    AddressNotFoundError,
    CartNotFoundError,
    DatabaseError,
    EmptyCartError,
    InsufficientStockError,
    ProductNotFoundError,
    ProductUnavailableError,
    UserNotFoundError,
    ValidationError,
)
from app.handlers import (
    address_not_found_handler,
    cart_not_found_handler,
    empty_cart_handler,
    insufficient_stock_handler,
    product_not_found_handler,
    product_unavailable_handler,
    user_not_found_handler,
    validation_error_handler,
)
from app.routes.checkout import router as checkout_router
from app.routes.products import router as product_router

app = FastAPI(title="CheckQuick Checkout API", version="1.0.0")

app.include_router(checkout_router)
app.include_router(product_router)

app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(UserNotFoundError, user_not_found_handler)
app.add_exception_handler(CartNotFoundError, cart_not_found_handler)
app.add_exception_handler(EmptyCartError, empty_cart_handler)
app.add_exception_handler(AddressNotFoundError, address_not_found_handler)
app.add_exception_handler(ProductNotFoundError, product_not_found_handler)
app.add_exception_handler(ProductUnavailableError, product_unavailable_handler)
app.add_exception_handler(InsufficientStockError, insufficient_stock_handler)


async def database_error_handler(request, exc: DatabaseError):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={"error": "database_error", "message": exc.message},
    )


app.add_exception_handler(DatabaseError, database_error_handler)


@app.get("/")
def root():
    return {"message": "CheckQuick Checkout API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


# Import models so SQLAlchemy can discover them when metadata is used.
from app.models import User, Product, Inventory, Cart, CartItem, Address, Order, OrderItem, Payment
