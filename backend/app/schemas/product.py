from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    price: float = Field(default=0.0, ge=0)
    quantity: int = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    sku: str | None = Field(default=None, min_length=1, max_length=100)
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    price: float | None = Field(default=None, ge=0)
    quantity: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ProductRead(BaseModel):
    id: int
    sku: str
    name: str
    description: str | None
    price: float
    quantity: int
    is_active: bool
