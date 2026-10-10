from sqlmodel import Session, select

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.product_rules import (
    validate_product_can_be_deactivated,
    validate_product_is_active,
    validate_unique_sku,
)


def create_product(session: Session, product_data: ProductCreate) -> Product:
    validate_unique_sku(session, product_data.sku)

    product = Product(
        sku=product_data.sku,
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        quantity=product_data.quantity,
    )

    session.add(product)
    session.commit()
    session.refresh(product)

    return product


def get_products(session: Session) -> list[Product]:
    statement = select(Product).order_by(Product.id)
    return list(session.exec(statement).all())


def get_product(session: Session, product_id: int) -> Product | None:
    return session.get(Product, product_id)


def update_product(
    session: Session,
    product: Product,
    product_data: ProductUpdate,
) -> Product:
    validate_product_is_active(product)

    update_data = product_data.model_dump(exclude_unset=True)

    if "sku" in update_data:
        validate_unique_sku(
            session,
            update_data["sku"],
            exclude_product_id=product.id,
        )

    for field, value in update_data.items():
        setattr(product, field, value)

    session.add(product)
    session.commit()
    session.refresh(product)

    return product


def deactivate_product(session: Session, product: Product) -> Product:
    validate_product_can_be_deactivated(product)

    product.is_active = False

    session.add(product)
    session.commit()
    session.refresh(product)

    return product
