from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class PurchaseOrder(SQLModel, table=True):
    __tablename__ = "purchase_orders"

    id: int | None = Field(default=None, primary_key=True)

    supplier_id: int = Field(index=True)

    status: str = Field(default="ordered", max_length=30)

    total_amount: float = Field(default=0.0)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )