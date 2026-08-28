from decimal import Decimal
from pydantic import BaseModel, Field

class CartItemCreate(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(gt=0)
