from fastapi import FastAPI

from app.database import engine
from app.models.base import Base
from app.models import User, Product, Inventory, Cart, CartItem, Address, Order, OrderItem, Payment
from app.routes.products import router as product_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(product_router)