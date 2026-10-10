from sqlmodel import Session, select

from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate
from app.core.exceptions import BusinessRuleError


def create_supplier(
    session: Session,
    supplier_data: SupplierCreate,
) -> Supplier:
    name = supplier_data.name.strip()

    if not name:
        raise BusinessRuleError("Supplier name cannot be empty.")

    if supplier_data.email:
        statement = select(Supplier).where(
            Supplier.email == str(supplier_data.email)
        )
        existing = session.exec(statement).first()

        if existing:
            raise BusinessRuleError(
                "A supplier with this email already exists."
            )

    supplier = Supplier(
        name=name,
        contact_person=supplier_data.contact_person,
        email=(
            str(supplier_data.email)
            if supplier_data.email
            else None
        ),
        phone=supplier_data.phone,
        address=supplier_data.address,
    )

    try:
        session.add(supplier)
        session.commit()
        session.refresh(supplier)
        return supplier
    except Exception:
        session.rollback()
        raise


def get_suppliers(session: Session) -> list[Supplier]:
    statement = select(Supplier).order_by(Supplier.id)
    return list(session.exec(statement).all())


def get_supplier(
    session: Session,
    supplier_id: int,
) -> Supplier | None:
    return session.get(Supplier, supplier_id)


def update_supplier(
    session: Session,
    supplier_id: int,
    supplier_data: SupplierUpdate,
) -> Supplier | None:
    supplier = session.get(Supplier, supplier_id)

    if supplier is None:
        return None

    updates = supplier_data.model_dump(exclude_unset=True)

    if "name" in updates:
        name = updates["name"]

        if name is None or not name.strip():
            raise BusinessRuleError(
                "Supplier name cannot be empty."
            )

        updates["name"] = name.strip()

    if "email" in updates and updates["email"] is not None:
        updates["email"] = str(updates["email"])

        statement = select(Supplier).where(
            Supplier.email == updates["email"],
            Supplier.id != supplier_id,
        )

        if session.exec(statement).first():
            raise BusinessRuleError(
                "Another supplier already uses this email."
            )

    for field, value in updates.items():
        setattr(supplier, field, value)

    try:
        session.add(supplier)
        session.commit()
        session.refresh(supplier)
        return supplier
    except Exception:
        session.rollback()
        raise


def delete_supplier(
    session: Session,
    supplier_id: int,
) -> bool:
    supplier = session.get(Supplier, supplier_id)

    if supplier is None:
        return False

    try:
        session.delete(supplier)
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise