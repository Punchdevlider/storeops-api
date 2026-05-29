from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    name: str
    sku: str
    description: str | None = None
    price: Decimal
    stock_quantity: int = 0
    is_active: bool = True
    category_id: int


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = None
    sku: str | None = None
    description: str | None = None
    price: Decimal | None = None
    stock_quantity: int | None = None
    is_active: bool | None = None
    category_id: int | None = None


class ProductRead(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)