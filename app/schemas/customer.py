from pydantic import BaseModel, ConfigDict, EmailStr


class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None
    is_active: bool = True


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    is_active: bool | None = None


class CustomerRead(CustomerBase):
    id: int

    model_config = ConfigDict(from_attributes=True)