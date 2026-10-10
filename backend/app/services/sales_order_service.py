from sqlmodel import Session, select

from app.core.exceptions import BusinessRuleError
from app.models.inventory_transaction import InventoryTransaction
from app.models.product import Product
from app.models.sales_order import SalesOrder
from app.models.sales_order_item import SalesOrderItem
from app.schemas.sales_order import (
    SalesOrderCreate,
    SalesOrderItemRead,
    SalesOrderRead,
)


def _build_sales_order_response(
    session: Session,
    sales_order: SalesOrder,
) -> SalesOrderRead:
    """Build a complete sales order response, including its items."""

    statement = (
        select(SalesOrderItem)
        .where(SalesOrderItem.sales_order_id == sales_order.id)
        .order_by(SalesOrderItem.id)
    )

    order_items = session.exec(statement).all()

    return SalesOrderRead(
        id=sales_order.id,
        customer_name=sales_order.customer_name,
        status=sales_order.status,
        total_amount=sales_order.total_amount,
        created_at=sales_order.created_at,
        items=[
            SalesOrderItemRead(
                id=item.id,
                sales_order_id=item.sales_order_id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                line_total=item.line_total,
            )
            for item in order_items
        ],
    )


def create_sales_order(
    session: Session,
    order_data: SalesOrderCreate,
) -> SalesOrderRead:
    """Validate, create and return a complete sales order."""

    try:
        # 1. Validate customer name.
        customer_name = order_data.customer_name.strip()

        if not customer_name:
            raise BusinessRuleError(
                "Customer name cannot be empty."
            )

        # 2. Reject duplicate products in the same request.
        product_ids = [
            item.product_id for item in order_data.items
        ]

        if len(product_ids) != len(set(product_ids)):
            raise BusinessRuleError(
                "A product can appear only once in a sales order."
            )

        # 3. Load and validate all products before changing stock.
        products: dict[int, Product] = {}

        for item in order_data.items:
            product = session.get(Product, item.product_id)

            if product is None:
                raise BusinessRuleError(
                    f"Product with ID {item.product_id} was not found."
                )

            if not product.is_active:
                raise BusinessRuleError(
                    f"Product '{product.sku}' is inactive "
                    "and cannot be ordered."
                )

            if product.quantity < item.quantity:
                raise BusinessRuleError(
                    f"Insufficient stock for product '{product.sku}'. "
                    f"Available: {product.quantity}, "
                    f"requested: {item.quantity}."
                )

            products[item.product_id] = product

        # 4. Calculate prices using trusted database values.
        total_amount = sum(
            products[item.product_id].price * item.quantity
            for item in order_data.items
        )

        # 5. Create the order header.
        sales_order = SalesOrder(
            customer_name=customer_name,
            status="confirmed",
            total_amount=total_amount,
        )

        session.add(sales_order)
        session.flush()

        # 6. Create order items and inventory transactions.
        for item in order_data.items:
            product = products[item.product_id]

            quantity_before = product.quantity
            quantity_after = quantity_before - item.quantity

            line_total = product.price * item.quantity

            order_item = SalesOrderItem(
                sales_order_id=sales_order.id,
                product_id=product.id,
                quantity=item.quantity,
                unit_price=product.price,
                line_total=line_total,
            )

            inventory_transaction = InventoryTransaction(
                product_id=product.id,
                quantity_change=-item.quantity,
                quantity_before=quantity_before,
                quantity_after=quantity_after,
                reason=f"Sales order #{sales_order.id}",
            )

            product.quantity = quantity_after

            session.add(order_item)
            session.add(product)
            session.add(inventory_transaction)

        # 7. Commit the entire operation together.
        session.commit()
        session.refresh(sales_order)

        # 8. Return the order with its individual items.
        return _build_sales_order_response(
            session,
            sales_order,
        )

    except Exception:
        session.rollback()
        raise


def get_sales_orders(
    session: Session,
) -> list[SalesOrderRead]:
    """Return all sales orders, including their items."""

    statement = select(SalesOrder).order_by(SalesOrder.id)

    sales_orders = session.exec(statement).all()

    return [
        _build_sales_order_response(session, order)
        for order in sales_orders
    ]


def get_sales_order(
    session: Session,
    sales_order_id: int,
) -> SalesOrderRead | None:
    """Return one sales order with its items."""

    sales_order = session.get(SalesOrder, sales_order_id)

    if sales_order is None:
        return None

    return _build_sales_order_response(
        session,
        sales_order,
    )