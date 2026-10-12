from sqlmodel import Session, select

from app.models.product import Product
from app.models.supplier import Supplier
from app.models.sales_order import SalesOrder
from app.models.purchase_order import PurchaseOrder


LOW_STOCK_THRESHOLD = 5


def get_dashboard_summary(session: Session) -> dict:
    """Calculate dashboard metrics from the existing database."""

    products = session.exec(select(Product)).all()
    suppliers = session.exec(select(Supplier)).all()
    sales_orders = session.exec(select(SalesOrder)).all()
    purchase_orders = session.exec(select(PurchaseOrder)).all()

    active_products = [
        product for product in products if product.is_active
    ]

    active_suppliers = [
        supplier for supplier in suppliers if supplier.is_active
    ]

    low_stock_products = [
        {
            "id": product.id,
            "sku": product.sku,
            "name": product.name,
            "quantity": product.quantity,
        }
        for product in active_products
        if product.quantity <= LOW_STOCK_THRESHOLD
    ]

    total_inventory_units = sum(
        product.quantity for product in active_products
    )

    inventory_value = sum(
        product.price * product.quantity
        for product in active_products
    )

    total_sales_revenue = sum(
        order.total_amount for order in sales_orders
    )

    pending_purchase_orders = sum(
        1 for order in purchase_orders
        if order.status == "ordered"
    )

    return {
        "total_products": len(active_products),
        "total_suppliers": len(active_suppliers),
        "total_inventory_units": total_inventory_units,
        "inventory_value": round(inventory_value, 2),
        "total_sales_orders": len(sales_orders),
        "total_sales_revenue": round(total_sales_revenue, 2),
        "pending_purchase_orders": pending_purchase_orders,
        "low_stock_threshold": LOW_STOCK_THRESHOLD,
        "low_stock_products": low_stock_products,
    }