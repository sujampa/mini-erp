from sqlmodel import Session, select

from app.core.exceptions import BusinessRuleError
from app.models.product import Product


def validate_unique_sku(
    session: Session,
    sku: str,
    exclude_product_id: int | None = None,
) -> None:
    statement = select(Product).where(Product.sku == sku)

    existing_product = session.exec(statement).first()

    if existing_product is None:
        return

    if exclude_product_id is not None and existing_product.id == exclude_product_id:
        return

    raise BusinessRuleError(f"SKU '{sku}' already exists.")


def validate_product_is_active(product: Product) -> None:
    if not product.is_active:
        raise BusinessRuleError(
            f"Product '{product.sku}' is inactive and cannot be modified."
        )


def validate_product_can_be_deactivated(product: Product) -> None:
    if not product.is_active:
        raise BusinessRuleError(
            f"Product '{product.sku}' is already inactive."
        )
