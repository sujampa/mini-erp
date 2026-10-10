from datetime import datetime

from pydantic import BaseModel, Field


class SalesOrderItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class SalesOrderCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=200)
    items: list[SalesOrderItemCreate] = Field(min_length=1)


class SalesOrderItemRead(BaseModel):
    id: int
    sales_order_id: int
    product_id: int
    quantity: int
    unit_price: float
    line_total: float


class SalesOrderRead(BaseModel):
    id: int
    customer_name: str
    status: str
    total_amount: float
    created_at: datetime
    items: list[SalesOrderItemRead]