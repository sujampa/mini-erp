from sqlmodel import SQLModel

from app.core.database import engine

# Import all models so SQLModel registers their tables.
from app.models.product import Product
from app.models.inventory_transaction import InventoryTransaction
from app.models.sales_order import SalesOrder
from app.models.sales_order_item import SalesOrderItem
from app.models.supplier import Supplier
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem
from app.models.user import User


def create_tables():
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    create_tables()