from typing import Any, List

from fastapi import Body, Depends, HTTPException, APIRouter, status
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.mail import send_new_account_email
from app.dependency import common
from app.models.user import User
from app.repositories.user import user_repo
from app.schemas.user import UserUpdate, UserSchema, UserCreate

router = APIRouter()


@router.get("/", response_model=List[UserSchema])
def read_users(
        db: Session = Depends(common.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(common.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = user_repo.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=UserSchema)
def create_user(
        *,
        db: Session = Depends(common.get_db),
        user_in: UserCreate,
        current_user: User = Depends(common.get_current_active_superuser),
) -> Any:
    """
    Create new user.
    """
    user = user_repo.find_by_columns(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this username already exists in the system.",
        )
    user = user_repo.create(db, obj_in=user_in)
    if settings.EMAILS_ENABLED and user_in.email:
        send_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
    return user


@router.put("/me", response_model=UserSchema)
def update_user_me(
        *,
        db: Session = Depends(common.get_db),
        password: str = Body(None),
        full_name: str = Body(None),
        email: EmailStr = Body(None),
        current_user: User = Depends(common.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    user = user_repo.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/me", response_model=UserSchema)
def read_user_me(
        db: Session = Depends(common.get_db),
        current_user: User = Depends(common.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.post("/open", response_model=UserSchema)
def create_user_open(
        *,
        db: Session = Depends(common.get_db),
        password: str = Body(...),
        email: EmailStr = Body(...),
        full_name: str = Body(None),
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=403,
            detail="Open user registration is forbidden on this server",
        )
    user = user_repo.get_by_email(db, email=email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    user_in = UserCreate(password=password, email=email, full_name=full_name)
    user = user_repo.create(db, obj_in=user_in)
    return user


@router.get("/{user_id}", response_model=UserSchema)
def read_user_by_id(
        user_id: int,
        current_user: User = Depends(common.get_current_active_user),
        db: Session = Depends(common.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = user_repo.find(db, id=user_id)
    if user == current_user:
        return user
    if not user_repo.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user


@router.put("/{user_id}", response_model=UserSchema)
def update_user(
        *,
        db: Session = Depends(common.get_db),
        user_id: int,
        user_in: UserUpdate,
        current_user: User = Depends(common.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    user = user_repo.find(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = user_repo.update(db, db_obj=user, obj_in=user_in)
    return user
