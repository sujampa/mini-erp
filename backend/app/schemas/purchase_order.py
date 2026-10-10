from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class PurchaseOrderItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity_ordered: int = Field(gt=0)
    unit_cost: float = Field(ge=0)


class PurchaseOrderCreate(BaseModel):
    supplier_id: int = Field(gt=0)
    items: list[PurchaseOrderItemCreate] = Field(min_length=1)


class PurchaseOrderItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    purchase_order_id: int
    product_id: int
    quantity_ordered: int
    quantity_received: int
    unit_cost: float
    line_total: float


class PurchaseOrderRead(BaseModel):
    id: int
    supplier_id: int
    status: str
    total_amount: float
    created_at: datetime
    items: list[PurchaseOrderItemRead]


class GoodsReceiptItem(BaseModel):
    product_id: int = Field(gt=0)
    quantity_received: int = Field(gt=0)


class GoodsReceiptCreate(BaseModel):
    items: list[GoodsReceiptItem] = Field(min_length=1)


class PurchaseOrderStatusUpdate(BaseModel):
    status: Literal["cancelled"]