from uuid import uuid4

from fastapi.testclient import TestClient


def make_supplier_payload():
    """Generate unique supplier data for each test."""
    unique_id = uuid4().hex[:8]

    return {
        "name": f"Test Supplier {unique_id}",
        "contact_person": "Test Contact",
        "email": f"supplier-{unique_id}@example.com",
        "phone": "9876543210",
        "address": "Test Address",
    }


def test_create_supplier(client: TestClient):
    """Valid supplier creation should return HTTP 201."""
    payload = make_supplier_payload()

    response = client.post("/suppliers/", json=payload)

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == payload["name"]
    assert data["email"] == payload["email"]
    assert data["phone"] == payload["phone"]
    assert isinstance(data["id"], int)
    assert data["is_active"] is True


def test_get_existing_supplier(client: TestClient):
    """A created supplier should be retrievable."""
    payload = make_supplier_payload()

    create_response = client.post("/suppliers/", json=payload)
    assert create_response.status_code == 201

    supplier_id = create_response.json()["id"]

    response = client.get(f"/suppliers/{supplier_id}")

    assert response.status_code == 200
    assert response.json()["id"] == supplier_id
    assert response.json()["email"] == payload["email"]


def test_list_suppliers(client: TestClient):
    """The supplier list should contain a newly created supplier."""
    payload = make_supplier_payload()

    create_response = client.post("/suppliers/", json=payload)
    assert create_response.status_code == 201

    response = client.get("/suppliers/")

    assert response.status_code == 200
    assert any(
        supplier["email"] == payload["email"]
        for supplier in response.json()
    )


def test_duplicate_supplier_email_returns_409(client: TestClient):
    """A duplicate email should be rejected as a business rule violation."""
    payload = make_supplier_payload()

    first_response = client.post("/suppliers/", json=payload)
    assert first_response.status_code == 201

    duplicate_response = client.post("/suppliers/", json=payload)

    assert duplicate_response.status_code == 409
    assert "email already exists" in (
        duplicate_response.json()["detail"]
    )


def test_invalid_supplier_email_returns_422(client: TestClient):
    """An invalid email should fail schema validation."""
    payload = make_supplier_payload()
    payload["email"] = "not-an-email"

    response = client.post("/suppliers/", json=payload)

    assert response.status_code == 422


def test_get_missing_supplier_returns_404(client: TestClient):
    """A nonexistent supplier should return HTTP 404."""
    response = client.get("/suppliers/2147483647")

    assert response.status_code == 404
    assert response.json()["detail"] == "Supplier not found."