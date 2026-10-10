from datetime import datetime, timezone

from sqlmodel import SQLModel, Field


class Supplier(SQLModel, table=True):
    __tablename__ = "suppliers"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=200)
    contact_person: str | None = Field(default=None, max_length=200)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = Field(default=None, max_length=500)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )