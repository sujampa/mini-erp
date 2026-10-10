from sqlmodel import Field, SQLModel


class PurchaseOrderItem(SQLModel, table=True):
    __tablename__ = "purchase_order_items"

    id: int | None = Field(default=None, primary_key=True)

    purchase_order_id: int = Field(index=True)

    product_id: int = Field(index=True)

    quantity_ordered: int

    quantity_received: int = Field(default=0)

    unit_cost: float

    line_total: float