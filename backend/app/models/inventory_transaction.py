from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class InventoryTransaction(SQLModel, table=True):
    __tablename__ = "inventory_transactions"

    id: int | None = Field(default=None, primary_key=True)

    product_id: int = Field(index=True)

    quantity_change: int

    quantity_before: int

    quantity_after: int

    reason: str

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
