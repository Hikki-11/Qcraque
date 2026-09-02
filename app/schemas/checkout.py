from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field


class CheckoutRequest(BaseModel):
    user_id: UUID
    shipping_address_id: UUID


class CheckoutResponse(BaseModel):
    order_id: UUID
    user_id: UUID
    shipping_address_id: UUID
    status: str
    total_amount: Decimal = Field(ge=0)
    item_count: int = Field(ge=1)
    message: str
