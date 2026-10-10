from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SupplierCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    contact_person: str | None = Field(default=None, max_length=200)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = Field(default=None, max_length=500)


class SupplierUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    contact_person: str | None = Field(default=None, max_length=200)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class SupplierRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    contact_person: str | None
    email: str | None
    phone: str | None
    address: str | None
    is_active: bool
    created_at: datetime