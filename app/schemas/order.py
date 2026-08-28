from decimal import Decimal
from pydantic import BaseModel, Field

class OrderCreate(BaseModel):
    user_id: str
    shipping_address_id: str
    total_amount: Decimal = Field(ge=0)
