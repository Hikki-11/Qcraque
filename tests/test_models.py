from decimal import Decimal
from app.schemas.user import UserCreate
from app.schemas.product import ProductCreate
from app.schemas.cart import CartItemCreate
from app.schemas.order import OrderCreate

def test_user_validation():
    user = UserCreate(name="Test User", email="test@example.com", password="password123")
    assert user.email == "test@example.com"

def test_product_price_validation():
    product = ProductCreate(name="Laptop", sku="LAP001", price=Decimal("50000"))
    assert product.price > 0

def test_cart_quantity_validation():
    item = CartItemCreate(product_id="product-1", quantity=2, unit_price=Decimal("100"))
    assert item.quantity > 0

def test_order_total_validation():
    order = OrderCreate(
        user_id="user-1",
        shipping_address_id="address-1",
        total_amount=Decimal("1000")
    )
    assert order.total_amount >= 0
