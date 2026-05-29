from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem, OrderStatusHistory
from app.models.product import Product
from app.schemas.order import OrderCreate


def get_orders(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    customer_id: int | None = None,
):
    query = db.query(Order)

    if status is not None:
        query = query.filter(Order.status == status)

    if customer_id is not None:
        query = query.filter(Order.customer_id == customer_id)

    return query.order_by(Order.id.desc()).offset(skip).limit(limit).all()


def get_order(db: Session, order_id: int):
    return db.query(Order).filter(Order.id == order_id).first()


def create_order(db: Session, order_data: OrderCreate):
    order = Order(
        customer_id=order_data.customer_id,
        status="pending",
        notes=order_data.notes,
        total_amount=Decimal("0.00"),
    )

    db.add(order)
    db.flush()

    total_amount = Decimal("0.00")

    for item_data in order_data.items:
        product = db.query(Product).filter(Product.id == item_data.product_id).first()

        unit_price = product.price
        total_price = unit_price * item_data.quantity

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item_data.quantity,
            unit_price=unit_price,
            total_price=total_price,
        )

        product.stock_quantity -= item_data.quantity

        total_amount += total_price
        db.add(order_item)

    order.total_amount = total_amount

    status_history = OrderStatusHistory(
        order_id=order.id,
        old_status=None,
        new_status="pending",
    )

    db.add(status_history)
    db.commit()
    db.refresh(order)

    return order


def update_order_status(db: Session, order: Order, new_status: str):
    old_status = order.status

    order.status = new_status

    status_history = OrderStatusHistory(
        order_id=order.id,
        old_status=old_status,
        new_status=new_status,
    )

    db.add(status_history)
    db.commit()
    db.refresh(order)

    return order