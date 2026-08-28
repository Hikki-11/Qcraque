from decimal import Decimal
from pydantic import BaseModel, Field

class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    sku: str = Field(min_length=1, max_length=100)
    price: Decimal = Field(gt=0)
    status: str = "ACTIVE"
