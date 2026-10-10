# Mini ERP Backend

A backend application for managing products, suppliers, inventory, sales orders,
and purchase orders. Built with FastAPI and PostgreSQL, with automated API
tests using pytest.

## Features

### Product Management
- Create and retrieve products.
- Update product information.
- Deactivate products.
- Validate product data and SKU uniqueness.

### Supplier Management
- Create and retrieve suppliers.
- Update and delete suppliers.
- Validate email addresses.
- Prevent duplicate supplier emails.

### Inventory Management
- Increase or decrease stock quantities.
- Prevent inventory from becoming negative.
- Maintain inventory transaction history.
- Reject adjustments to inactive products.

### Sales Orders
- Create and retrieve sales orders.
- Calculate order totals using product prices.
- Deduct inventory when an order is created.
- Reject orders with insufficient stock.
- Record inventory transactions for sales.

### Purchase Orders
- Create and retrieve purchase orders.
- Track ordered and received quantities.
- Support partial and complete goods receipts.
- Update inventory when goods are received.
- Prevent receiving quantities beyond the outstanding amount.

## Technology Stack

- Python
- FastAPI
- SQLModel
- PostgreSQL
- SQLAlchemy
- Pydantic
- Pytest
- HTTPX
- Uvicorn

## Project Structure

```text
mini_erp/
├── README.md
└── backend/
    ├── app/
    │   ├── api/
    │   │   ├── inventory.py
    │   │   ├── products.py
    │   │   ├── purchase_orders.py
    │   │   ├── sales_order.py
    │   │   └── suppliers.py
    │   ├── core/
    │   ├── models/
    │   ├── schemas/
    │   ├── services/
    │   └── main.py
    ├── tests/
    ├── .env
    └── .venv/