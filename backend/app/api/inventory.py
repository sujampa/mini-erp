from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.schemas.inventory import (
    InventoryAdjustment,
    InventoryTransactionRead,
)
from app.schemas.product import ProductRead
from app.services.inventory_history_service import get_inventory_history
from app.services.inventory_service import adjust_inventory


router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
)


@router.post(
    "/adjust",
    response_model=ProductRead,
)
def adjust_inventory_endpoint(
    adjustment: InventoryAdjustment,
    session: Session = Depends(get_session),
):
    return adjust_inventory(session, adjustment)


@router.get(
    "/{product_id}/history",
    response_model=list[InventoryTransactionRead],
)
def get_inventory_history_endpoint(
    product_id: int,
    session: Session = Depends(get_session),
):
    return get_inventory_history(session, product_id)