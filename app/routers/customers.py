from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate
from app.services import customer as customer_service


router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


@router.get("/", response_model=list[CustomerRead])
def list_customers(
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
):
    return customer_service.get_customers(
        db=db,
        skip=skip,
        limit=limit,
        is_active=is_active,
    )


@router.post("/", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
):
    existing_customer = customer_service.get_customer_by_email(
        db=db,
        email=str(customer_data.email),
    )

    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer with this email already exists.",
        )

    return customer_service.create_customer(db=db, customer_data=customer_data)


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
):
    customer = customer_service.get_customer(db=db, customer_id=customer_id)

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    return customer


@router.patch("/{customer_id}", response_model=CustomerRead)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
):
    customer = customer_service.get_customer(db=db, customer_id=customer_id)

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    if customer_data.email:
        existing_customer = customer_service.get_customer_by_email(
            db=db,
            email=str(customer_data.email),
        )

        if existing_customer and existing_customer.id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer with this email already exists.",
            )

    return customer_service.update_customer(
        db=db,
        customer=customer,
        customer_data=customer_data,
    )


@router.delete("/{customer_id}", response_model=CustomerRead)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
):
    customer = customer_service.get_customer(db=db, customer_id=customer_id)

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    return customer_service.delete_customer(db=db, customer=customer)