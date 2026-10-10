from sqlmodel import Field, SQLModel


class SalesOrderItem(SQLModel, table=True):
    __tablename__ = "sales_order_items"

    id: int | None = Field(default=None, primary_key=True)

    sales_order_id: int = Field(index=True)

    product_id: int = Field(index=True)

    quantity: int

    unit_price: float

    line_total: float