from datetime import datetime

from pydantic import BaseModel, Field


class InventoryAdjustment(BaseModel):
    product_id: int = Field(gt=0)
    quantity_change: int
    reason: str = Field(min_length=1, max_length=500)


class InventoryTransactionRead(BaseModel):
    id: int
    product_id: int
    quantity_change: int
    quantity_before: int
    quantity_after: int
    reason: str
    created_at: datetime
