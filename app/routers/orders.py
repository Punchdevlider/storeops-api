from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.order import OrderCreate, OrderRead, OrderStatus, OrderStatusUpdate
from app.services import customer as customer_service
from app.services import order as order_service
from app.services import product as product_service


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.get("/", response_model=list[OrderRead])
def list_orders(
    skip: int = 0,
    limit: int = 100,
    status_filter: OrderStatus | None = None,
    customer_id: int | None = None,
    db: Session = Depends(get_db),
):
    return order_service.get_orders(
        db=db,
        skip=skip,
        limit=limit,
        status=status_filter.value if status_filter else None,
        customer_id=customer_id,
    )


@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
):
    customer = customer_service.get_customer(
        db=db,
        customer_id=order_data.customer_id,
    )

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    if not customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer is not active.",
        )

    product_ids = [item.product_id for item in order_data.items]

    if len(product_ids) != len(set(product_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate products are not allowed in one order.",
        )

    for item in order_data.items:
        product = product_service.get_product(
            db=db,
            product_id=item.product_id,
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item.product_id} not found.",
            )

        if not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with id {item.product_id} is not active.",
            )

        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock for product with id {item.product_id}.",
            )

    return order_service.create_order(db=db, order_data=order_data)


@router.get("/{order_id}", response_model=OrderRead)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
):
    order = order_service.get_order(db=db, order_id=order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found.",
        )

    return order


@router.patch("/{order_id}/status", response_model=OrderRead)
def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: Session = Depends(get_db),
):
    order = order_service.get_order(db=db, order_id=order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found.",
        )

    if order.status == status_data.status.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order already has this status.",
        )

    return order_service.update_order_status(
        db=db,
        order=order,
        new_status=status_data.status.value,
    )