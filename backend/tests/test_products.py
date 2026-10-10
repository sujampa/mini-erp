from uuid import uuid4

from fastapi.testclient import TestClient


def make_product_payload():
    """Create unique test data for every test."""
    unique_id = uuid4().hex[:8]

    return {
        "sku": f"TEST-{unique_id}",
        "name": f"Test Product {unique_id}",
        "description": "Created by automated API tests",
        "price": 100.0,
        "quantity": 10,
    }


def test_create_product(client: TestClient):
    """Creating a valid product should return HTTP 201."""
    payload = make_product_payload()

    response = client.post("/products/", json=payload)

    assert response.status_code == 201

    data = response.json()
    assert data["sku"] == payload["sku"]
    assert data["name"] == payload["name"]
    assert data["price"] == payload["price"]
    assert data["quantity"] == payload["quantity"]
    assert isinstance(data["id"], int)


def test_get_existing_product(client: TestClient):
    """A created product should be retrievable by its ID."""
    payload = make_product_payload()

    create_response = client.post("/products/", json=payload)
    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    response = client.get(f"/products/{product_id}")

    assert response.status_code == 200
    assert response.json()["id"] == product_id
    assert response.json()["sku"] == payload["sku"]


def test_get_missing_product_returns_404(client: TestClient):
    """A nonexistent product should return HTTP 404."""
    response = client.get("/products/2147483647")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found."


def test_create_product_rejects_negative_price(client: TestClient):
    """Schema validation should reject a negative price."""
    payload = make_product_payload()
    payload["price"] = -100

    response = client.post("/products/", json=payload)

    assert response.status_code == 422


def test_create_product_rejects_negative_quantity(client: TestClient):
    """Schema validation should reject a negative quantity."""
    payload = make_product_payload()
    payload["quantity"] = -5

    response = client.post("/products/", json=payload)

    assert response.status_code == 422