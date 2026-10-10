from sqlmodel import Session, select

from app.models.inventory_transaction import InventoryTransaction


def get_inventory_history(
    session: Session,
    product_id: int,
) -> list[InventoryTransaction]:
    statement = (
        select(InventoryTransaction)
        .where(InventoryTransaction.product_id == product_id)
        .order_by(InventoryTransaction.id)
    )

    return list(session.exec(statement).all())
