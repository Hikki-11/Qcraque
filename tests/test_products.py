from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    r = client.get("/")
    assert r.status_code == 200

def test_health():
    r = client.get("/health")
    assert r.status_code == 200

def test_product_validation():
    r = client.post("/products/", json={"name": "Invalid", "sku": "BAD001", "price": -10})
    assert r.status_code == 422
