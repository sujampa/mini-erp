from sqlmodel import Session

from app.core.exceptions import BusinessRuleError
from app.models.inventory_transaction import InventoryTransaction
from app.models.product import Product
from app.schemas.inventory import InventoryAdjustment


def adjust_inventory(
    session: Session,
    adjustment: InventoryAdjustment,
) -> Product:
    product = session.get(Product, adjustment.product_id)

    if product is None:
        raise BusinessRuleError(
            f"Product with ID {adjustment.product_id} was not found."
        )

    if not product.is_active:
        raise BusinessRuleError(
            f"Product '{product.sku}' is inactive and cannot have inventory adjusted."
        )

    quantity_before = product.quantity

    new_quantity = quantity_before + adjustment.quantity_change

    if new_quantity < 0:
        raise BusinessRuleError(
            f"Inventory adjustment would make product '{product.sku}' quantity negative."
        )

    product.quantity = new_quantity

    transaction = InventoryTransaction(
        product_id=product.id,
        quantity_change=adjustment.quantity_change,
        quantity_before=quantity_before,
        quantity_after=new_quantity,
        reason=adjustment.reason,
    )

    session.add(product)
    session.add(transaction)

    session.commit()
    session.refresh(product)

    return product