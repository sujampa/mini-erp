from sqlmodel import Session, select

from app.core.database import engine
from app.models.product import Product


def get_low_stock_products(threshold: int = 5) -> list[dict]:
    """Return active products with stock at or below the threshold."""

    with Session(engine) as session:
        statement = (
            select(Product)
            .where(
                Product.is_active == True,
                Product.quantity <= threshold,
            )
            .order_by(Product.quantity)
        )

        products = session.exec(statement).all()

        return [
            {
                "id": product.id,
                "sku": product.sku,
                "name": product.name,
                "quantity": product.quantity,
                "price": product.price,
            }
            for product in products
        ]


def get_inventory_summary() -> dict:
    """Return a summary of active inventory."""

    with Session(engine) as session:
        statement = select(Product).where(
            Product.is_active == True
        )

        products = session.exec(statement).all()

        total_products = len(products)

        total_units = sum(
            product.quantity for product in products
        )

        total_value = sum(
            product.price * product.quantity
            for product in products
        )

        return {
            "total_active_products": total_products,
            "total_stock_units": total_units,
            "total_inventory_value": round(total_value, 2),
        }
def get_low_cost_products(limit: int = 5) -> list[dict]:
    """Return the cheapest active products from the database."""

    if limit < 1:
        raise ValueError("Limit must be at least 1.")

    with Session(engine) as session:
        statement = (
            select(Product)
            .where(Product.is_active == True)
            .order_by(Product.price, Product.id)
            .limit(limit)
        )

        products = session.exec(statement).all()

        return [
            {
                "id": product.id,
                "sku": product.sku,
                "name": product.name,
                "price": product.price,
                "quantity": product.quantity,
            }
            for product in products
        ]