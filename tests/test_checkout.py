from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app


class FakeQuery:
    def __init__(self, model, db):
        self.model = model
        self.db = db

    def filter(self, *args):
        return self

    def first(self):
        return self.db.data.get(self.model.__name__)

    def all(self):
        return self.db.data.get(self.model.__name__, [])


class FakeDB:
    def __init__(self, data):
        self.data = data
        self.added = []
        self.rolled_back = False
        self.committed = False

    def query(self, model):
        return FakeQuery(model, self)

    def add(self, obj):
        self.added.append(obj)
        if obj.__class__.__name__ == "Order" and getattr(obj, "order_id", None) is None:
            obj.order_id = uuid4()

    def flush(self):
        pass

    def commit(self):
        self.committed = True

    def refresh(self, obj):
        pass

    def rollback(self):
        self.rolled_back = True


def make_db(cart_items=None, **overrides):
    from app.models import Address, Cart, CartItem, Inventory, Product, User

    user_id = uuid4()
    address_id = uuid4()
    cart_id = uuid4()
    product_id = uuid4()

    user = SimpleNamespace(user_id=user_id)
    address = SimpleNamespace(address_id=address_id, user_id=user_id)
    cart = SimpleNamespace(cart_id=cart_id, user_id=user_id, status="ACTIVE")
    product = SimpleNamespace(
        product_id=product_id,
        name="Laptop",
        price=Decimal("1000.00"),
        status="ACTIVE",
    )
    inventory = SimpleNamespace(product_id=product_id, quantity=5, reserved_quantity=0)
    item = SimpleNamespace(cart_item_id=uuid4(), cart_id=cart_id, product_id=product_id, quantity=2)

    data = {
        "User": user,
        "Address": address,
        "Cart": cart,
        "CartItem": [item] if cart_items is None else cart_items,
        "Product": product,
        "Inventory": inventory,
    }
    data.update(overrides)
    return FakeDB(data), user_id, address_id


client = TestClient(app)


def override_db(db):
    def dependency():
        yield db
    app.dependency_overrides[get_db] = dependency


def clear_override():
    app.dependency_overrides.clear()


def test_checkout_success():
    db, user_id, address_id = make_db()
    override_db(db)
    try:
        response = client.post(
            "/checkout/",
            json={"user_id": str(user_id), "shipping_address_id": str(address_id)},
        )
        assert response.status_code == 201
        assert response.json()["message"] == "Checkout completed successfully"
        assert response.json()["total_amount"] == "2000.00"
        assert db.committed is True
    finally:
        clear_override()


def test_checkout_empty_cart():
    db, user_id, address_id = make_db(cart_items=[])
    override_db(db)
    try:
        response = client.post(
            "/checkout/",
            json={"user_id": str(user_id), "shipping_address_id": str(address_id)},
        )
        assert response.status_code == 400
        assert response.json()["error"] == "empty_cart"
    finally:
        clear_override()


def test_checkout_product_not_found():
    db, user_id, address_id = make_db()
    db.data["Product"] = None
    override_db(db)
    try:
        response = client.post(
            "/checkout/",
            json={"user_id": str(user_id), "shipping_address_id": str(address_id)},
        )
        assert response.status_code == 404
        assert response.json()["error"] == "product_not_found"
    finally:
        clear_override()


def test_checkout_insufficient_stock():
    db, user_id, address_id = make_db()
    db.data["Inventory"].quantity = 1
    override_db(db)
    try:
        response = client.post(
            "/checkout/",
            json={"user_id": str(user_id), "shipping_address_id": str(address_id)},
        )
        assert response.status_code == 409
        assert response.json()["error"] == "insufficient_stock"
    finally:
        clear_override()


def test_checkout_invalid_input():
    response = client.post(
        "/checkout/",
        json={"user_id": "not-a-uuid", "shipping_address_id": "not-a-uuid"},
    )
    assert response.status_code == 422


def test_checkout_missing_user():
    db, user_id, address_id = make_db()
    db.data["User"] = None
    override_db(db)
    try:
        response = client.post(
            "/checkout/",
            json={"user_id": str(user_id), "shipping_address_id": str(address_id)},
        )
        assert response.status_code == 404
        assert response.json()["error"] == "user_not_found"
    finally:
        clear_override()
