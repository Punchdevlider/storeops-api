from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category_id: int | None = None,
    is_active: bool | None = None,
):
    query = db.query(Product)

    if category_id is not None:
        query = query.filter(Product.category_id == category_id)

    if is_active is not None:
        query = query.filter(Product.is_active == is_active)

    return query.offset(skip).limit(limit).all()


def get_product(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()


def get_product_by_sku(db: Session, sku: str):
    return db.query(Product).filter(Product.sku == sku).first()


def create_product(db: Session, product_data: ProductCreate):
    product = Product(
        name=product_data.name,
        sku=product_data.sku,
        description=product_data.description,
        price=product_data.price,
        stock_quantity=product_data.stock_quantity,
        is_active=product_data.is_active,
        category_id=product_data.category_id,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


def update_product(db: Session, product: Product, product_data: ProductUpdate):
    update_data = product_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product


def delete_product(db: Session, product: Product):
    db.delete(product)
    db.commit()

    return product