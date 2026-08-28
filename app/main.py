from fastapi import FastAPI
from app.models.base import Base

app = FastAPI(title="CheckQuick Checkout API", version="1.0.0")

@app.get("/")
def root():
    return {"message": "CheckQuick Checkout API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

# Import models so SQLAlchemy can discover them when metadata is used.
from app.models import User, Product, Inventory, Cart, CartItem, Address, Order, OrderItem, Payment
