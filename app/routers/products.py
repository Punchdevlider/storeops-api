from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.services import category as category_service
from app.services import product as product_service


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.get("/", response_model=list[ProductRead])
def list_products(
    skip: int = 0,
    limit: int = 100,
    category_id: int | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
):
    return product_service.get_products(
        db=db,
        skip=skip,
        limit=limit,
        category_id=category_id,
        is_active=is_active,
    )


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
):
    category = category_service.get_category(
        db=db,
        category_id=product_data.category_id,
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found.",
        )

    existing_product = product_service.get_product_by_sku(
        db=db,
        sku=product_data.sku,
    )

    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this SKU already exists.",
        )

    return product_service.create_product(db=db, product_data=product_data)


@router.get("/{product_id}", response_model=ProductRead)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = product_service.get_product(db=db, product_id=product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    return product


@router.patch("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
):
    product = product_service.get_product(db=db, product_id=product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    if product_data.category_id is not None:
        category = category_service.get_category(
            db=db,
            category_id=product_data.category_id,
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )

    if product_data.sku:
        existing_product = product_service.get_product_by_sku(
            db=db,
            sku=product_data.sku,
        )

        if existing_product and existing_product.id != product_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this SKU already exists.",
            )

    return product_service.update_product(
        db=db,
        product=product,
        product_data=product_data,
    )


@router.delete("/{product_id}", response_model=ProductRead)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = product_service.get_product(db=db, product_id=product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    return product_service.delete_product(db=db, product=product)