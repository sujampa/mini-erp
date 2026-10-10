from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.database import get_session
from app.core.exceptions import BusinessRuleError
from app.schemas.purchase_order import (
    GoodsReceiptCreate,
    PurchaseOrderCreate,
    PurchaseOrderRead,
)
from app.services.purchase_order_service import (
    create_purchase_order,
    get_purchase_order,
    get_purchase_orders,
    receive_purchase_order,
)

router = APIRouter(
    prefix="/purchase-orders",
    tags=["Purchase Orders"],
)


@router.post(
    "/",
    response_model=PurchaseOrderRead,
    status_code=status.HTTP_201_CREATED,
)
def create_purchase_order_endpoint(
    order_data: PurchaseOrderCreate,
    session: Session = Depends(get_session),
):
    return create_purchase_order(session, order_data)


@router.get(
    "/",
    response_model=list[PurchaseOrderRead],
)
def list_purchase_orders_endpoint(
    session: Session = Depends(get_session),
):
    return get_purchase_orders(session)


@router.get(
    "/{purchase_order_id}",
    response_model=PurchaseOrderRead,
)
def get_purchase_order_endpoint(
    purchase_order_id: int,
    session: Session = Depends(get_session),
):
    order = get_purchase_order(session, purchase_order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found.",
        )

    return order


@router.post(
    "/{purchase_order_id}/receive",
    response_model=PurchaseOrderRead,
)
def receive_purchase_order_endpoint(
    purchase_order_id: int,
    receipt_data: GoodsReceiptCreate,
    session: Session = Depends(get_session),
):
    try:
        return receive_purchase_order(
            session,
            purchase_order_id,
            receipt_data,
        )
    except BusinessRuleError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=exc.message,
        ) from exc