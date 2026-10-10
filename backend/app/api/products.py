from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.database import get_session
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.services.product_service import (
    create_product,
    deactivate_product,
    get_product,
    get_products,
    update_product,
)


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.post(
    "/",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
)
def create_product_endpoint(
    product_data: ProductCreate,
    session: Session = Depends(get_session),
):
    return create_product(session, product_data)


@router.get(
    "/",
    response_model=list[ProductRead],
)
def get_products_endpoint(
    session: Session = Depends(get_session),
):
    return get_products(session)


@router.get(
    "/{product_id}",
    response_model=ProductRead,
)
def get_product_endpoint(
    product_id: int,
    session: Session = Depends(get_session),
):
    product = get_product(session, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    return product


@router.put(
    "/{product_id}",
    response_model=ProductRead,
)
def update_product_endpoint(
    product_id: int,
    product_data: ProductUpdate,
    session: Session = Depends(get_session),
):
    product = get_product(session, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    return update_product(session, product, product_data)


@router.delete(
    "/{product_id}",
    response_model=ProductRead,
)
def deactivate_product_endpoint(
    product_id: int,
    session: Session = Depends(get_session),
):
    product = get_product(session, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    return deactivate_product(session, product)
