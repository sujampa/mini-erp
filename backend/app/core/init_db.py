from sqlmodel import SQLModel

from app.core.database import engine
from app.models.inventory_transaction import InventoryTransaction
from app.models.product import Product
from app.models.sales_order import SalesOrder
from app.models.sales_order_item import SalesOrderItem


def create_tables():
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    create_tables()