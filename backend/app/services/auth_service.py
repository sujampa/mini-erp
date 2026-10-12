from sqlmodel import Session, select

from app.models.user import User
from app.schemas.user import UserRegister
from app.auth.security import hash_password, verify_password


def register_user(
    session: Session,
    user_data: UserRegister,
) -> User:
    existing_user = session.exec(
        select(User).where(User.username == user_data.username)
    ).first()

    if existing_user:
        raise ValueError("Username already exists")

    existing_email = session.exec(
        select(User).where(User.email == str(user_data.email))
    ).first()

    if existing_email:
        raise ValueError("Email already exists")

    user = User(
        username=user_data.username,
        email=str(user_data.email),
        hashed_password=hash_password(user_data.password),
        role="staff",
        is_active=True,
    )

    try:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except Exception:
        session.rollback()
        raise


def authenticate_user(
    session: Session,
    username: str,
    password: str,
) -> User | None:
    user = session.exec(
        select(User).where(User.username == username)
    ).first()

    if not user:
        return None

    if not user.is_active:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user