from datetime import timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.core.mail import send_reset_password_email
from app.core.model import AuthenticatableModel
from app.core.repository import BaseRepository
from app.core.response import ResponseSchema
from app.core.security import generate_password_reset_token, verify_password_reset_token, get_password_hash, \
    verify_password
from app.dependency import common
from app.schemas.token import Token


def authenticate(
        db: Session,
        *,
        username: str,
        password: str,
        auth_repository: BaseRepository
) -> Optional[AuthenticatableModel]:
    user = db.query(auth_repository.model).filter_by(
        **{auth_repository.model.username_column(): username}
    ).first()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def make_auth_router(
        reset_password: bool = True,
        repository: BaseRepository = None,
        **kwargs
) -> APIRouter:
    router = APIRouter(**kwargs)
    from app.repositories.user import user_repo
    auth_repository = repository or user_repo
    if not hasattr(auth_repository.model, 'is_authenticatable') or not auth_repository.model.is_authenticatable:
        raise ValueError(f"Model `{auth_repository.model.__name__}` can't authenticate!")

    @router.post("/login", response_model=Token)
    # @router.post("/login", response_model=TokenSchema, responses={'422': {"model": ResponseSchema}})
    def login_access_token(
            db: Session = Depends(common.get_db),
            form_data: OAuth2PasswordRequestForm = Depends()
    ) -> Any:
        """
        OAuth2 compatible token login, find an access token for future requests
        """
        user = authenticate(
            db,
            username=form_data.username,
            password=form_data.password,
            auth_repository=auth_repository,
        )
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return {
            "access_token": security.create_access_token(
                user.id,
                expires_delta=access_token_expires
            ),
            "token_type": "bearer",
        }

    if reset_password:
        @router.post("/password-recovery/{email}", response_model=ResponseSchema)
        def recover_password(email: str, db: Session = Depends(common.get_db)) -> Any:
            """
            Password Recovery
            """
            user = auth_repository.get_by_email(db, email=email)

            if not user:
                raise HTTPException(
                    status_code=404,
                    detail="The user with this username does not exist in the system.",
                )
            password_reset_token = generate_password_reset_token(email=email)
            send_reset_password_email(
                email_to=user.email, email=email, token=password_reset_token
            )
            return {"msg": "Password recovery email sent"}

        @router.post("/reset-password/", response_model=ResponseSchema)
        def reset_password(
                token: str = Body(...),
                new_password: str = Body(...),
                db: Session = Depends(common.get_db),
        ) -> Any:
            """
            Reset password
            """
            email = verify_password_reset_token(token)
            if not email:
                raise HTTPException(status_code=400, detail="Invalid token")
            user = auth_repository.get_by_email(db, email=email)
            if not user:
                raise HTTPException(
                    status_code=404,
                    detail="The user with this username does not exist in the system.",
                )
            elif not auth_repository.is_active(user):
                raise HTTPException(status_code=400, detail="Inactive user")
            hashed_password = get_password_hash(new_password)
            user.hashed_password = hashed_password
            db.add(user)
            db.commit()
            return {"msg": "Password updated successfully"}

    return router
