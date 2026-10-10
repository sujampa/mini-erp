from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.product import Product
from app.models.inventory_transaction import InventoryTransaction


def create_test_product(
    client: TestClient,
    quantity: int = 10,
) -> dict:
    """Create a unique product for an inventory test."""

    unique_id = uuid4().hex[:8]

    payload = {
        "sku": f"INV-TEST-{unique_id}",
        "name": f"Inventory Test Product {unique_id}",
        "description": "Created by automated inventory tests",
        "price": 100.0,
        "quantity": quantity,
    }

    response = client.post("/products/", json=payload)

    assert response.status_code == 201, response.text

    return response.json()


def test_increase_inventory(client: TestClient, db_session: Session):
    """Adding inventory should increase stock and record a transaction."""

    product = create_test_product(client, quantity=10)
    product_id = product["id"]

    response = client.post(
        "/inventory/adjust",
        json={
            "product_id": product_id,
            "quantity_change": 5,
            "reason": "Stock replenishment test",
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["quantity"] == 15

    db_session.expire_all()
    saved_product = db_session.get(Product, product_id)

    assert saved_product is not None
    assert saved_product.quantity == 15

    history = client.get(f"/inventory/{product_id}/history")

    assert history.status_code == 200, history.text

    transactions = history.json()

    assert len(transactions) == 1
    assert transactions[0]["quantity_change"] == 5
    assert transactions[0]["quantity_before"] == 10
    assert transactions[0]["quantity_after"] == 15
    assert transactions[0]["reason"] == "Stock replenishment test"


def test_decrease_inventory(client: TestClient, db_session: Session):
    """Removing inventory should decrease stock correctly."""

    product = create_test_product(client, quantity=10)
    product_id = product["id"]

    response = client.post(
        "/inventory/adjust",
        json={
            "product_id": product_id,
            "quantity_change": -3,
            "reason": "Damaged stock test",
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["quantity"] == 7

    db_session.expire_all()
    saved_product = db_session.get(Product, product_id)

    assert saved_product is not None
    assert saved_product.quantity == 7


def test_adjustment_that_causes_negative_stock_returns_409(
    client: TestClient,
    db_session: Session,
):
    """An adjustment must not make stock negative."""

    product = create_test_product(client, quantity=5)
    product_id = product["id"]

    response = client.post(
        "/inventory/adjust",
        json={
            "product_id": product_id,
            "quantity_change": -6,
            "reason": "Invalid stock reduction test",
        },
    )

    assert response.status_code == 409

    db_session.expire_all()
    saved_product = db_session.get(Product, product_id)

    assert saved_product is not None
    assert saved_product.quantity == 5

    history = client.get(f"/inventory/{product_id}/history")

    assert history.status_code == 200
    assert history.json() == []


def test_adjustment_for_missing_product_returns_409(client: TestClient):
    """An adjustment for a nonexistent product should be rejected."""

    response = client.post(
        "/inventory/adjust",
        json={
            "product_id": 2147483647,
            "quantity_change": 5,
            "reason": "Missing product test",
        },
    )

    assert response.status_code == 409


def test_inventory_history_preserves_transaction_order(
    client: TestClient,
):
    """Inventory history should contain transactions in creation order."""

    product = create_test_product(client, quantity=10)
    product_id = product["id"]

    first_response = client.post(
        "/inventory/adjust",
        json={
            "product_id": product_id,
            "quantity_change": 4,
            "reason": "First adjustment",
        },
    )

    assert first_response.status_code == 200, first_response.text

    second_response = client.post(
        "/inventory/adjust",
        json={
            "product_id": product_id,
            "quantity_change": -2,
            "reason": "Second adjustment",
        },
    )

    assert second_response.status_code == 200, second_response.text

    history_response = client.get(
        f"/inventory/{product_id}/history"
    )

    assert history_response.status_code == 200

    history = history_response.json()

    assert len(history) == 2

    assert history[0]["reason"] == "First adjustment"
    assert history[0]["quantity_before"] == 10
    assert history[0]["quantity_after"] == 14

    assert history[1]["reason"] == "Second adjustment"
    assert history[1]["quantity_before"] == 14
    assert history[1]["quantity_after"] == 12


def test_adjustment_with_empty_reason_returns_422(
    client: TestClient,
):
    """The request schema should reject an empty reason."""

    product = create_test_product(client, quantity=10)

    response = client.post(
        "/inventory/adjust",
        json={
            "product_id": product["id"],
            "quantity_change": 5,
            "reason": "",
        },
    )

    assert response.status_code == 422


def test_adjustment_with_zero_product_id_returns_422(
    client: TestClient,
):
    """The request schema should reject a nonpositive product ID."""

    response = client.post(
        "/inventory/adjust",
        json={
            "product_id": 0,
            "quantity_change": 5,
            "reason": "Invalid product ID test",
        },
    )

    assert response.status_code == 422