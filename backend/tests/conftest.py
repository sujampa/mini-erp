import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import URL
from sqlmodel import Session, SQLModel, create_engine

# Import the application and its database dependency.
from app.main import app
from app.core.database import get_session

# Import all models so SQLModel registers their tables.
from app.models.product import Product
from app.models.inventory_transaction import InventoryTransaction
from app.models.sales_order import SalesOrder
from app.models.sales_order_item import SalesOrderItem
from app.models.supplier import Supplier
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem


@pytest.fixture(scope="session")
def test_engine():
    """Create a separate engine for the test database."""

    database_url = URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv("TEST_DB_USER", "postgres"),
        password=os.environ["TEST_DB_PASSWORD"],
        host=os.getenv("TEST_DB_HOST", "localhost"),
        port=int(os.getenv("TEST_DB_PORT", "5432")),
        database="mini_erp_test",
    )

    engine = create_engine(database_url, echo=False)

    # Only create tables in mini_erp_test.
    SQLModel.metadata.create_all(engine)

    yield engine

    engine.dispose()


@pytest.fixture
def db_session(test_engine):
    """Provide a session for preparing and checking test data."""

    with Session(test_engine) as session:
        yield session


@pytest.fixture
def client(test_engine):
    """Make API requests using the isolated test database."""

    def override_get_session():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()