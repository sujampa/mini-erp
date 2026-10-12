from fastapi.testclient import TestClient


def test_dashboard_returns_summary(client: TestClient):
    response = client.get("/dashboard/")

    assert response.status_code == 200

    data = response.json()

    expected_keys = {
        "total_products",
        "total_suppliers",
        "total_inventory_units",
        "inventory_value",
        "total_sales_orders",
        "total_sales_revenue",
        "pending_purchase_orders",
        "low_stock_threshold",
        "low_stock_products",
    }

    assert expected_keys.issubset(data.keys())

    assert isinstance(data["total_products"], int)
    assert isinstance(data["total_suppliers"], int)
    assert isinstance(data["total_inventory_units"], int)
    assert isinstance(data["inventory_value"], (int, float))
    assert isinstance(data["total_sales_orders"], int)
    assert isinstance(data["total_sales_revenue"], (int, float))
    assert isinstance(data["pending_purchase_orders"], int)
    assert isinstance(data["low_stock_products"], list)