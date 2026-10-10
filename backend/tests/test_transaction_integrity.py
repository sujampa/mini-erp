from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.product import Product
from app.models.sales_order import SalesOrder
from app.models.inventory_transaction import InventoryTransaction


def create_test_product(
    client: TestClient,
    quantity: int,
) -> dict:
    """Create a product with a unique SKU."""

    unique_id = uuid4().hex[:8]

    response = client.post(
        "/products/",
        json={
            "sku": f"TXN-{unique_id}",
            "name": f"Transaction Test {unique_id}",
            "description": "Transaction integrity test",
            "price": 100.0,
            "quantity": quantity,
        },
    )

    assert response.status_code == 201, response.text

    return response.json()


def test_failed_multi_product_order_changes_nothing(
    client: TestClient,
    db_session: Session,
):
    """
    If one product has insufficient stock, the entire order
    must fail without changing either product's inventory.
    """

    # Product A has sufficient stock.
    product_a = create_test_product(client, quantity=10)

    # Product B has insufficient stock.
    product_b = create_test_product(client, quantity=2)

    response = client.post(
        "/sales-orders/",
        json={
            "customer_name": "Transaction Integrity Customer",
            "items": [
                {
                    "product_id": product_a["id"],
                    "quantity": 3,
                },
                {
                    "product_id": product_b["id"],
                    "quantity": 5,
                },
            ],
        },
    )

    # The order should be rejected.
    assert response.status_code == 409

    # Refresh database state and verify both stock quantities.
    db_session.expire_all()

    saved_a = db_session.get(Product, product_a["id"])
    saved_b = db_session.get(Product, product_b["id"])

    assert saved_a is not None
    assert saved_b is not None

    assert saved_a.quantity == 10
    assert saved_b.quantity == 2

    # Neither product should have a transaction from this failed order.
    for product_id in (product_a["id"], product_b["id"]):
        transaction = db_session.exec(
            select(InventoryTransaction).where(
                InventoryTransaction.product_id == product_id
            )
        ).first()

        assert transaction is None

    # No order should have been created for this failed request.
    failed_order = db_session.exec(
        select(SalesOrder).where(
            SalesOrder.customer_name
            == "Transaction Integrity Customer"
        )
    ).first()

    assert failed_order is None