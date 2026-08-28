from decimal import Decimal
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    sku: str = Field(min_length=1, max_length=100)
    price: Decimal = Field(gt=0)
    status: str = Field(default="ACTIVE", max_length=20)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    sku: str | None = Field(default=None, min_length=1, max_length=100)
    price: Decimal | None = Field(default=None, gt=0)
    status: str | None = Field(default=None, max_length=20)


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: UUID
    name: str
    description: str | None
    sku: str
    price: Decimal
    status: str
    created_at: datetime
    updated_at: datetime