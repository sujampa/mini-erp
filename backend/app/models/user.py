from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)

    username: str = Field(
        sa_column=Column(
            String(50),
            unique=True,
            index=True,
            nullable=False,
        )
    )

    email: str = Field(
        sa_column=Column(
            String(255),
            unique=True,
            index=True,
            nullable=False,
        )
    )

    hashed_password: str = Field(nullable=False)

    role: str = Field(default="staff", max_length=20)

    is_active: bool = Field(default=True)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )