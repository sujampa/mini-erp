from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.product import Product
from app.models.sales_order import SalesOrder
from app.models.inventory_transaction import InventoryTransaction


def create_test_product(
    client: TestClient,
    quantity: int = 10,
    price: float = 100.0,
) -> dict:
    """Create a unique product for a sales-order test."""

    unique_id = uuid4().hex[:8]

    response = client.post(
        "/products/",
        json={
            "sku": f"SO-TEST-{unique_id}",
            "name": f"Sales Test Product {unique_id}",
            "description": "Automated sales-order test",
            "price": price,
            "quantity": quantity,
        },
    )

    assert response.status_code == 201, response.text
    return response.json()


def create_sales_order(
    client: TestClient,
    product_id: int,
    quantity: int = 2,
    customer_name: str = "Test Customer",
):
    """Submit a sales order."""

    return client.post(
        "/sales-orders/",
        json={
            "customer_name": customer_name,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": quantity,
                }
            ],
        },
    )


def test_create_sales_order_and_deduct_stock(
    client: TestClient,
    db_session: Session,
):
    """Creating a sales order should deduct stock and record the sale."""

    product = create_test_product(
        client,
        quantity=10,
        price=100.0,
    )

    response = create_sales_order(
        client,
        product["id"],
        quantity=3,
        customer_name="Test Customer",
    )

    assert response.status_code == 201, response.text

    order = response.json()

    assert order["customer_name"] == "Test Customer"
    assert order["status"] == "confirmed"
    assert order["total_amount"] == 300.0
    assert len(order["items"]) == 1

    order_item = order["items"][0]

    assert order_item["product_id"] == product["id"]
    assert order_item["quantity"] == 3
    assert order_item["unit_price"] == 100.0
    assert order_item["line_total"] == 300.0

    db_session.expire_all()

    saved_product = db_session.get(Product, product["id"])

    assert saved_product is not None
    assert saved_product.quantity == 7

    transaction = db_session.exec(
        select(InventoryTransaction).where(
            InventoryTransaction.product_id == product["id"],
            InventoryTransaction.reason == f"Sales order #{order['id']}",
        )
    ).first()

    assert transaction is not None
    assert transaction.quantity_change == -3
    assert transaction.quantity_before == 10
    assert transaction.quantity_after == 7


def test_get_existing_sales_order(client: TestClient):
    """An existing sales order should be retrievable by ID."""

    product = create_test_product(client)

    create_response = create_sales_order(
        client,
        product["id"],
        quantity=2,
    )

    assert create_response.status_code == 201, create_response.text

    order_id = create_response.json()["id"]

    response = client.get(f"/sales-orders/{order_id}")

    assert response.status_code == 200

    order = response.json()

    assert order["id"] == order_id
    assert order["items"][0]["product_id"] == product["id"]


def test_list_sales_orders(client: TestClient):
    """The sales-order listing should include a newly created order."""

    product = create_test_product(client)

    create_response = create_sales_order(
        client,
        product["id"],
        quantity=1,
        customer_name="Listing Test Customer",
    )

    assert create_response.status_code == 201, create_response.text

    order_id = create_response.json()["id"]

    response = client.get("/sales-orders/")

    assert response.status_code == 200

    orders = response.json()

    assert any(order["id"] == order_id for order in orders)


def test_missing_sales_order_returns_404(client: TestClient):
    """Requesting a nonexistent sales order should return 404."""

    response = client.get("/sales-orders/2147483647")

    assert response.status_code == 404
    assert response.json()["detail"] == "Sales order not found."


def test_insufficient_stock_rejects_order_without_changing_stock(
    client: TestClient,
    db_session: Session,
):
    """An order exceeding available stock should not change inventory."""

    product = create_test_product(client, quantity=5)

    response = create_sales_order(
        client,
        product["id"],
        quantity=6,
    )

    assert response.status_code == 409

    db_session.expire_all()

    saved_product = db_session.get(Product, product["id"])

    assert saved_product is not None
    assert saved_product.quantity == 5

    transaction = db_session.exec(
        select(InventoryTransaction).where(
            InventoryTransaction.product_id == product["id"]
        )
    ).first()

    assert transaction is None


def test_missing_product_rejects_order(client: TestClient):
    """A sales order cannot reference a nonexistent product."""

    response = create_sales_order(
        client,
        product_id=2147483647,
        quantity=1,
    )

    assert response.status_code == 409


def test_duplicate_product_in_order_is_rejected(
    client: TestClient,
    db_session: Session,
):
    """The same product cannot appear twice in one order."""

    product = create_test_product(client, quantity=10)

    response = client.post(
        "/sales-orders/",
        json={
            "customer_name": "Duplicate Item Test",
            "items": [
                {
                    "product_id": product["id"],
                    "quantity": 1,
                },
                {
                    "product_id": product["id"],
                    "quantity": 2,
                },
            ],
        },
    )

    assert response.status_code == 409

    db_session.expire_all()

    saved_product = db_session.get(Product, product["id"])

    assert saved_product is not None
    assert saved_product.quantity == 10

    transaction = db_session.exec(
        select(InventoryTransaction).where(
            InventoryTransaction.product_id == product["id"]
        )
    ).first()

    assert transaction is None


def test_zero_quantity_is_rejected_by_schema(client: TestClient):
    """The request schema must reject a zero order quantity."""

    product = create_test_product(client)

    response = create_sales_order(
        client,
        product["id"],
        quantity=0,
    )

    assert response.status_code == 422


def test_empty_customer_name_is_rejected_by_schema(
    client: TestClient,
):
    """The request schema must reject an empty customer name."""

    product = create_test_product(client)

    response = create_sales_order(
        client,
        product["id"],
        quantity=1,
        customer_name="",
    )

    assert response.status_code == 422