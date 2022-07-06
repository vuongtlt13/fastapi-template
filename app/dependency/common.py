from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User
from app.repositories.user import user_repo
from app.schemas.token import TokenPayload

# define token URL for docs
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_STR}/auth/login"
)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        # noinspection PyUnboundLocalVariable
        db.close()


def get_current_user(
        db: Session = Depends(get_db),
        token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    user = user_repo.find_by_columns(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


def get_current_active_user(
        current_user: User = Depends(get_current_user),
) -> User:
    # if not user_repo.is_active(current_user):
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
        current_user: User = Depends(get_current_user),
) -> User:
    if not user_repo.is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="The user doesn't have enough privileges"
        )
    return current_user
