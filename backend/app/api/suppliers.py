from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.database import get_session
from app.schemas.supplier import (
    SupplierCreate,
    SupplierRead,
    SupplierUpdate,
)
from app.services.supplier_service import (
    create_supplier,
    delete_supplier,
    get_supplier,
    get_suppliers,
    update_supplier,
)

router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"],
)


@router.post(
    "/",
    response_model=SupplierRead,
    status_code=status.HTTP_201_CREATED,
)
def create_supplier_endpoint(
    supplier_data: SupplierCreate,
    session: Session = Depends(get_session),
):
    return create_supplier(session, supplier_data)


@router.get("/", response_model=list[SupplierRead])
def list_suppliers_endpoint(
    session: Session = Depends(get_session),
):
    return get_suppliers(session)


@router.get("/{supplier_id}", response_model=SupplierRead)
def get_supplier_endpoint(
    supplier_id: int,
    session: Session = Depends(get_session),
):
    supplier = get_supplier(session, supplier_id)

    if supplier is None:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found.",
        )

    return supplier


@router.put("/{supplier_id}", response_model=SupplierRead)
def update_supplier_endpoint(
    supplier_id: int,
    supplier_data: SupplierUpdate,
    session: Session = Depends(get_session),
):
    supplier = update_supplier(
        session,
        supplier_id,
        supplier_data,
    )

    if supplier is None:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found.",
        )

    return supplier


@router.delete("/{supplier_id}")
def delete_supplier_endpoint(
    supplier_id: int,
    session: Session = Depends(get_session),
):
    deleted = delete_supplier(session, supplier_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found.",
        )

    return {
        "message": "Supplier deleted successfully.",
        "supplier_id": supplier_id,
    }