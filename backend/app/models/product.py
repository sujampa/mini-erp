from sqlmodel import Field, SQLModel


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: int | None = Field(default=None, primary_key=True)
    sku: str = Field(index=True, unique=True)
    name: str
    description: str | None = None
    price: float = Field(default=0.0)
    quantity: int = Field(default=0)
    is_active: bool = Field(default=True)
