from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class SalesOrder(SQLModel, table=True):
    __tablename__ = "sales_orders"

    id: int | None = Field(default=None, primary_key=True)

    customer_name: str

    status: str = Field(default="confirmed")

    total_amount: float = Field(default=0.0)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )