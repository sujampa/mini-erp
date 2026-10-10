from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.product import Product
from app.models.inventory_transaction import InventoryTransaction


def create_test_product(client: TestClient, quantity: int = 10) -> dict:
    """Create a unique active product."""

    unique_id = uuid4().hex[:8]

    response = client.post(
        "/products/",
        json={
            "sku": f"LIFE-{unique_id}",
            "name": f"Lifecycle Product {unique_id}",
            "description": "Product lifecycle automated test",
            "price": 100.0,
            "quantity": quantity,
        },
    )

    assert response.status_code == 201, response.text
    return response.json()


def test_deactivate_product(client: TestClient):
    """Deactivating a product should change its active status."""

    product = create_test_product(client)

    response = client.delete(f"/products/{product['id']}")

    assert response.status_code == 200, response.text
    assert response.json()["is_active"] is False


def test_inactive_product_cannot_be_sold(
    client: TestClient,
    db_session: Session,
):
    """An inactive product must not be sold."""

    product = create_test_product(client, quantity=10)
    product_id = product["id"]

    deactivate_response = client.delete(f"/products/{product_id}")

    assert deactivate_response.status_code == 200, deactivate_response.text
    assert deactivate_response.json()["is_active"] is False

    sales_response = client.post(
        "/sales-orders/",
        json={
            "customer_name": "Lifecycle Test Customer",
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2,
                }
            ],
        },
    )

    assert sales_response.status_code == 409

    db_session.expire_all()
    saved_product = db_session.get(Product, product_id)

    assert saved_product is not None
    assert saved_product.quantity == 10

    transactions = db_session.exec(
        select(InventoryTransaction).where(
            InventoryTransaction.product_id == product_id
        )
    ).all()

    assert transactions == []


def test_inactive_product_inventory_adjustment_is_rejected(
    client: TestClient,
    db_session: Session,
):
    """Inventory adjustments must reject inactive products."""

    product = create_test_product(client, quantity=10)
    product_id = product["id"]

    deactivate_response = client.delete(f"/products/{product_id}")

    assert deactivate_response.status_code == 200

    adjustment_response = client.post(
        "/inventory/adjust",
        json={
            "product_id": product_id,
            "quantity_change": 5,
            "reason": "Inactive product test",
        },
    )

    assert adjustment_response.status_code == 409

    db_session.expire_all()
    saved_product = db_session.get(Product, product_id)

    assert saved_product is not None
    assert saved_product.quantity == 10

    transactions = db_session.exec(
        select(InventoryTransaction).where(
            InventoryTransaction.product_id == product_id
        )
    ).all()

    assert transactions == []


def test_inactive_product_cannot_be_updated(client: TestClient):
    """The product service should reject updates to inactive products."""

    product = create_test_product(client)

    deactivate_response = client.delete(f"/products/{product['id']}")

    assert deactivate_response.status_code == 200

    update_response = client.put(
        f"/products/{product['id']}",
        json={
            "name": "Attempted Update",
        },
    )

    assert update_response.status_code == 409