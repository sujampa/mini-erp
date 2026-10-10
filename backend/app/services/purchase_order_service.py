from decimal import Decimal

from sqlalchemy import select as sqlalchemy_select
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.core.exceptions import BusinessRuleError
from app.models.inventory_transaction import InventoryTransaction
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem
from app.schemas.purchase_order import (
    GoodsReceiptCreate,
    PurchaseOrderCreate,
    PurchaseOrderItemRead,
    PurchaseOrderRead,
)


def _build_purchase_order_response(
    session: Session,
    order: PurchaseOrder,
) -> PurchaseOrderRead:
    items = session.exec(
        select(PurchaseOrderItem)
        .where(PurchaseOrderItem.purchase_order_id == order.id)
        .order_by(PurchaseOrderItem.id)
    ).all()

    return PurchaseOrderRead(
        id=order.id,
        supplier_id=order.supplier_id,
        status=order.status,
        total_amount=order.total_amount,
        created_at=order.created_at,
        items=[
            PurchaseOrderItemRead(
                id=item.id,
                purchase_order_id=item.purchase_order_id,
                product_id=item.product_id,
                quantity_ordered=item.quantity_ordered,
                quantity_received=item.quantity_received,
                unit_cost=item.unit_cost,
                line_total=item.line_total,
            )
            for item in items
        ],
    )


def create_purchase_order(
    session: Session,
    order_data: PurchaseOrderCreate,
) -> PurchaseOrderRead:
    try:
        supplier = session.get(Supplier, order_data.supplier_id)

        if supplier is None:
            raise BusinessRuleError(
                f"Supplier with ID {order_data.supplier_id} was not found."
            )

        if not supplier.is_active:
            raise BusinessRuleError(
                f"Supplier '{supplier.name}' is inactive."
            )

        product_ids = [item.product_id for item in order_data.items]

        if len(product_ids) != len(set(product_ids)):
            raise BusinessRuleError(
                "A product can appear only once in a purchase order."
            )

        for item in order_data.items:
            product = session.get(Product, item.product_id)

            if product is None:
                raise BusinessRuleError(
                    f"Product with ID {item.product_id} was not found."
                )

            if not product.is_active:
                raise BusinessRuleError(
                    f"Product '{product.sku}' is inactive."
                )

        total_amount = sum(
            (
                Decimal(str(item.unit_cost))
                * item.quantity_ordered
                for item in order_data.items
            ),
            Decimal("0"),
        )

        order = PurchaseOrder(
            supplier_id=supplier.id,
            status="ordered",
            total_amount=float(total_amount),
        )

        session.add(order)
        session.flush()

        for item in order_data.items:
            line_total = (
                Decimal(str(item.unit_cost))
                * item.quantity_ordered
            )

            session.add(
                PurchaseOrderItem(
                    purchase_order_id=order.id,
                    product_id=item.product_id,
                    quantity_ordered=item.quantity_ordered,
                    quantity_received=0,
                    unit_cost=item.unit_cost,
                    line_total=float(line_total),
                )
            )

        session.commit()
        session.refresh(order)

        return _build_purchase_order_response(session, order)

    except Exception:
        session.rollback()
        raise


def get_purchase_orders(
    session: Session,
) -> list[PurchaseOrderRead]:
    orders = session.exec(
        select(PurchaseOrder).order_by(PurchaseOrder.id)
    ).all()

    return [
        _build_purchase_order_response(session, order)
        for order in orders
    ]


def get_purchase_order(
    session: Session,
    purchase_order_id: int,
) -> PurchaseOrderRead | None:
    order = session.get(PurchaseOrder, purchase_order_id)

    if order is None:
        return None

    return _build_purchase_order_response(session, order)


def receive_purchase_order(
    session: Session,
    purchase_order_id: int,
    receipt_data: GoodsReceiptCreate,
) -> PurchaseOrderRead:
    try:
        # Lock the purchase order so concurrent receipt requests
        # for this order are serialized.
        order_statement = (
            select(PurchaseOrder)
            .where(PurchaseOrder.id == purchase_order_id)
            .with_for_update()
        )

        order = session.exec(order_statement).first()

        if order is None:
            raise BusinessRuleError(
                f"Purchase order {purchase_order_id} was not found."
            )

        if order.status == "cancelled":
            raise BusinessRuleError(
                "Goods cannot be received against a cancelled order."
            )

        if order.status == "received":
            raise BusinessRuleError(
                "This purchase order has already been fully received."
            )

        requested_product_ids = [
            item.product_id for item in receipt_data.items
        ]

        if len(requested_product_ids) != len(set(requested_product_ids)):
            raise BusinessRuleError(
                "A product can appear only once in a single receipt."
            )

        # Lock the order items to protect received quantities.
        item_statement = (
            select(PurchaseOrderItem)
            .where(
                PurchaseOrderItem.purchase_order_id == purchase_order_id
            )
            .order_by(PurchaseOrderItem.id)
            .with_for_update()
        )

        order_items = session.exec(item_statement).all()

        items_by_product = {
            item.product_id: item for item in order_items
        }

        # Validate the entire receipt before modifying inventory.
        for receipt_item in receipt_data.items:
            order_item = items_by_product.get(receipt_item.product_id)

            if order_item is None:
                raise BusinessRuleError(
                    f"Product {receipt_item.product_id} "
                    "is not part of this purchase order."
                )

            outstanding = (
                order_item.quantity_ordered
                - order_item.quantity_received
            )

            if receipt_item.quantity_received > outstanding:
                raise BusinessRuleError(
                    f"Cannot receive {receipt_item.quantity_received} "
                    f"units of product {receipt_item.product_id}. "
                    f"Only {outstanding} units remain outstanding."
                )

            product = session.get(
                Product,
                receipt_item.product_id,
            )

            if product is None:
                raise BusinessRuleError(
                    f"Product {receipt_item.product_id} was not found."
                )

            if not product.is_active:
                raise BusinessRuleError(
                    f"Product '{product.sku}' is inactive."
                )

        # All validation passed. Apply the receipt.
        for receipt_item in receipt_data.items:
            order_item = items_by_product[receipt_item.product_id]

            product_statement = (
                select(Product)
                .where(Product.id == receipt_item.product_id)
                .with_for_update()
            )

            product = session.exec(product_statement).first()

            if product is None:
                raise BusinessRuleError(
                    f"Product {receipt_item.product_id} was not found."
                )

            quantity_before = product.quantity
            quantity_change = receipt_item.quantity_received
            quantity_after = quantity_before + quantity_change

            product.quantity = quantity_after
            order_item.quantity_received += quantity_change

            transaction = InventoryTransaction(
                product_id=product.id,
                quantity_change=quantity_change,
                quantity_before=quantity_before,
                quantity_after=quantity_after,
                reason=(
                    f"Goods receipt for purchase order "
                    f"#{purchase_order_id}"
                ),
            )

            session.add(product)
            session.add(order_item)
            session.add(transaction)

        # Derive status from the quantities received.
        all_fully_received = all(
            item.quantity_received == item.quantity_ordered
            for item in order_items
        )

        any_received = any(
            item.quantity_received > 0
            for item in order_items
        )

        if all_fully_received:
            order.status = "received"
        elif any_received:
            order.status = "partially_received"
        else:
            order.status = "ordered"

        session.add(order)

        # Commit stock changes, receipt quantities, transaction history,
        # and order status together.
        session.commit()
        session.refresh(order)

        return _build_purchase_order_response(session, order)

    except Exception:
        session.rollback()
        raise