import uuid
from decimal import Decimal
from sqlalchemy import Integer, Numeric, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class CartItem(Base):
    __tablename__ = "cart_items"

    cart_item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cart_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("carts.cart_id"), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.product_id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    __table_args__ = (
        UniqueConstraint("cart_id", "product_id", name="unique_cart_product"),
        CheckConstraint("quantity > 0", name="cart_quantity_positive"),
        CheckConstraint("unit_price > 0", name="cart_unit_price_positive"),
    )

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")
