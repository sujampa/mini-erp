from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.database import get_session
from app.schemas.sales_order import SalesOrderCreate, SalesOrderRead
from app.services.sales_order_service import (
    create_sales_order,
    get_sales_order,
    get_sales_orders,
)


router = APIRouter(
    prefix="/sales-orders",
    tags=["Sales Orders"],
)


@router.post(
    "/",
    response_model=SalesOrderRead,
    status_code=status.HTTP_201_CREATED,
)
def create_sales_order_endpoint(
    order_data: SalesOrderCreate,
    session: Session = Depends(get_session),
):
    sales_order = create_sales_order(
        session,
        order_data,
    )

    return sales_order


@router.get(
    "/",
    response_model=list[SalesOrderRead],
)
def get_sales_orders_endpoint(
    session: Session = Depends(get_session),
):
    return get_sales_orders(session)


@router.get(
    "/{sales_order_id}",
    response_model=SalesOrderRead,
)
def get_sales_order_endpoint(
    sales_order_id: int,
    session: Session = Depends(get_session),
):
    sales_order = get_sales_order(
        session,
        sales_order_id,
    )

    if sales_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales order not found.",
        )

    return sales_order