from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.product import Product
from app.models.supplier import Supplier
from app.models.inventory_transaction import InventoryTransaction


def create_test_supplier(client: TestClient) -> int:
    """Create a supplier and return its ID."""
    unique_id = uuid4().hex[:8]

    response = client.post(
        "/suppliers/",
        json={
            "name": f"PO Test Supplier {unique_id}",
            "email": f"po-supplier-{unique_id}@example.com",
            "contact_person": "Test Contact",
            "phone": "9876543210",
            "address": "Test Address",
        },
    )

    assert response.status_code == 201, response.text
    return response.json()["id"]


def create_test_product(client: TestClient, quantity: int = 10) -> int:
    """Create a product and return its ID."""
    unique_id = uuid4().hex[:8]

    response = client.post(
        "/products/",
        json={
            "sku": f"PO-TEST-{unique_id}",
            "name": f"PO Test Product {unique_id}",
            "description": "Automated purchase order test",
            "price": 100.0,
            "quantity": quantity,
        },
    )

    assert response.status_code == 201, response.text
    return response.json()["id"]


def create_test_purchase_order(
    client: TestClient,
    supplier_id: int,
    product_id: int,
    quantity_ordered: int = 5,
) -> dict:
    """Create a purchase order and return its response."""
    response = client.post(
        "/purchase-orders/",
        json={
            "supplier_id": supplier_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity_ordered": quantity_ordered,
                    "unit_cost": 50.0,
                }
            ],
        },
    )

    assert response.status_code == 201, response.text
    return response.json()


def test_create_purchase_order(client: TestClient):
    supplier_id = create_test_supplier(client)
    product_id = create_test_product(client)

    response = client.post(
        "/purchase-orders/",
        json={
            "supplier_id": supplier_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity_ordered": 5,
                    "unit_cost": 50.0,
                }
            ],
        },
    )

    assert response.status_code == 201, response.text

    data = response.json()

    assert data["supplier_id"] == supplier_id
    assert data["status"] == "ordered"
    assert data["total_amount"] == 250.0
    assert data["items"][0]["product_id"] == product_id
    assert data["items"][0]["quantity_ordered"] == 5
    assert data["items"][0]["quantity_received"] == 0


def test_partial_and_complete_goods_receipt(
    client: TestClient,
    db_session: Session,
):
    supplier_id = create_test_supplier(client)
    product_id = create_test_product(client, quantity=10)

    order = create_test_purchase_order(
        client,
        supplier_id,
        product_id,
        quantity_ordered=5,
    )
    order_id = order["id"]

    # Receive the first 3 units.
    first_receipt = client.post(
        f"/purchase-orders/{order_id}/receive",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity_received": 3,
                }
            ]
        },
    )

    assert first_receipt.status_code == 200, first_receipt.text

    first_data = first_receipt.json()

    assert first_data["status"] == "partially_received"
    assert first_data["items"][0]["quantity_received"] == 3

    db_session.expire_all()
    product = db_session.get(Product, product_id)

    assert product is not None
    assert product.quantity == 13

    # Receive the remaining 2 units.
    second_receipt = client.post(
        f"/purchase-orders/{order_id}/receive",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity_received": 2,
                }
            ]
        },
    )

    assert second_receipt.status_code == 200, second_receipt.text

    second_data = second_receipt.json()

    assert second_data["status"] == "received"
    assert second_data["items"][0]["quantity_received"] == 5

    db_session.expire_all()
    product = db_session.get(Product, product_id)

    assert product is not None
    assert product.quantity == 15

    transactions = db_session.exec(
        select(InventoryTransaction)
        .where(InventoryTransaction.product_id == product_id)
        .order_by(InventoryTransaction.id)
    ).all()

    receipt_transactions = [
        transaction
        for transaction in transactions
        if transaction.reason == f"Goods receipt for purchase order #{order_id}"
    ]

    assert len(receipt_transactions) == 2

    assert receipt_transactions[0].quantity_change == 3
    assert receipt_transactions[0].quantity_before == 10
    assert receipt_transactions[0].quantity_after == 13

    assert receipt_transactions[1].quantity_change == 2
    assert receipt_transactions[1].quantity_before == 13
    assert receipt_transactions[1].quantity_after == 15


def test_receiving_after_full_receipt_returns_409(
    client: TestClient,
    db_session: Session,
):
    supplier_id = create_test_supplier(client)
    product_id = create_test_product(client, quantity=10)

    order = create_test_purchase_order(
        client,
        supplier_id,
        product_id,
        quantity_ordered=2,
    )
    order_id = order["id"]

    receipt = client.post(
        f"/purchase-orders/{order_id}/receive",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity_received": 2,
                }
            ]
        },
    )

    assert receipt.status_code == 200, receipt.text
    assert receipt.json()["status"] == "received"

    db_session.expire_all()
    product = db_session.get(Product, product_id)

    assert product is not None
    stock_before_invalid_receipt = product.quantity

    transactions_before = len(
        db_session.exec(
            select(InventoryTransaction).where(
                InventoryTransaction.product_id == product_id
            )
        ).all()
    )

    invalid_receipt = client.post(
        f"/purchase-orders/{order_id}/receive",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity_received": 1,
                }
            ]
        },
    )

    assert invalid_receipt.status_code == 409

    db_session.expire_all()
    product = db_session.get(Product, product_id)

    assert product is not None
    assert product.quantity == stock_before_invalid_receipt

    transactions_after = len(
        db_session.exec(
            select(InventoryTransaction).where(
                InventoryTransaction.product_id == product_id
            )
        ).all()
    )

    assert transactions_after == transactions_before


def test_receiving_more_than_outstanding_returns_409(
    client: TestClient,
    db_session: Session,
):
    supplier_id = create_test_supplier(client)
    product_id = create_test_product(client, quantity=10)

    order = create_test_purchase_order(
        client,
        supplier_id,
        product_id,
        quantity_ordered=5,
    )
    order_id = order["id"]

    invalid_receipt = client.post(
        f"/purchase-orders/{order_id}/receive",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity_received": 6,
                }
            ]
        },
    )

    assert invalid_receipt.status_code == 409

    db_session.expire_all()
    product = db_session.get(Product, product_id)

    assert product is not None
    assert product.quantity == 10

    order_response = client.get(f"/purchase-orders/{order_id}")

    assert order_response.status_code == 200

    order_data = order_response.json()

    assert order_data["status"] == "ordered"
    assert order_data["items"][0]["quantity_received"] == 0