from decimal import Decimal
from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
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
from app.models import Address, Cart, CartItem, Inventory, Order, OrderItem, Product, User
from app.schemas.checkout import CheckoutRequest, CheckoutResponse

router = APIRouter(prefix="/checkout", tags=["Checkout"])


@router.post("/", response_model=CheckoutResponse, status_code=status.HTTP_201_CREATED)
def checkout(request: CheckoutRequest, db: Session = Depends(get_db)):
    """Convert the user's active cart into an order with validated stock."""
    try:
        user = db.query(User).filter(User.user_id == request.user_id).first()
        if user is None:
            raise UserNotFoundError("User not found")

        address = (
            db.query(Address)
            .filter(
                Address.address_id == request.shipping_address_id,
                Address.user_id == request.user_id,
            )
            .first()
        )
        if address is None:
            raise AddressNotFoundError("Shipping address not found for this user")

        cart = (
            db.query(Cart)
            .filter(Cart.user_id == request.user_id, Cart.status == "ACTIVE")
            .first()
        )
        if cart is None:
            raise CartNotFoundError("No active cart found for this user")

        cart_items = db.query(CartItem).filter(CartItem.cart_id == cart.cart_id).all()
        if not cart_items:
            raise EmptyCartError("Cannot checkout because the cart is empty")

        order_items_data = []
        total_amount = Decimal("0.00")

        for item in cart_items:
            if item.quantity <= 0:
                raise ValidationError(
                    f"Invalid quantity for cart item {item.cart_item_id}: quantity must be greater than zero"
                )

            product = db.query(Product).filter(Product.product_id == item.product_id).first()
            if product is None:
                raise ProductNotFoundError(f"Product {item.product_id} was not found")
            if product.status != "ACTIVE":
                raise ProductUnavailableError(f"Product '{product.name}' is not available")

            inventory = (
                db.query(Inventory)
                .filter(Inventory.product_id == item.product_id)
                .first()
            )
            if inventory is None:
                raise ProductUnavailableError(
                    f"Inventory is not configured for product '{product.name}'"
                )

            available = inventory.quantity - inventory.reserved_quantity
            if available < item.quantity:
                raise InsufficientStockError(
                    f"Insufficient stock for '{product.name}'. Available: {available}, requested: {item.quantity}"
                )

            unit_price = Decimal(product.price)
            total_amount += unit_price * item.quantity
            order_items_data.append((item, product, inventory, unit_price))

        order = Order(
            user_id=request.user_id,
            shipping_address_id=request.shipping_address_id,
            status="PENDING",
            total_amount=total_amount,
        )
        db.add(order)
        db.flush()

        for item, product, inventory, unit_price in order_items_data:
            db.add(
                OrderItem(
                    order_id=order.order_id,
                    product_id=product.product_id,
                    quantity=item.quantity,
                    unit_price=unit_price,
                )
            )
            inventory.quantity -= item.quantity

        cart.status = "CHECKED_OUT"
        db.commit()
        db.refresh(order)

        return CheckoutResponse(
            order_id=order.order_id,
            user_id=order.user_id,
            shipping_address_id=order.shipping_address_id,
            status=order.status,
            total_amount=order.total_amount,
            item_count=len(order_items_data),
            message="Checkout completed successfully",
        )

    except (
        UserNotFoundError,
        AddressNotFoundError,
        CartNotFoundError,
        EmptyCartError,
        ValidationError,
        ProductNotFoundError,
        ProductUnavailableError,
        InsufficientStockError,
    ):
        db.rollback()
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        # Do not expose database internals to the client.
        from app.exceptions import DatabaseError
        raise DatabaseError("A database error occurred while processing checkout") from exc
    except Exception as exc:
        db.rollback()
        from app.exceptions import DatabaseError
        raise DatabaseError("An unexpected error occurred while processing checkout") from exc
