from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


def get_customers(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
):
    query = db.query(Customer)

    if is_active is not None:
        query = query.filter(Customer.is_active == is_active)

    return query.offset(skip).limit(limit).all()


def get_customer(db: Session, customer_id: int):
    return db.query(Customer).filter(Customer.id == customer_id).first()


def get_customer_by_email(db: Session, email: str):
    return db.query(Customer).filter(Customer.email == email).first()


def create_customer(db: Session, customer_data: CustomerCreate):
    customer = Customer(
        first_name=customer_data.first_name,
        last_name=customer_data.last_name,
        email=customer_data.email,
        phone=customer_data.phone,
        is_active=customer_data.is_active,
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


def update_customer(db: Session, customer: Customer, customer_data: CustomerUpdate):
    update_data = customer_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)

    return customer


def delete_customer(db: Session, customer: Customer):
    db.delete(customer)
    db.commit()

    return customer