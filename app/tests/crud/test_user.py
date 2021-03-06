from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import repositories
from app.core.security import verify_password
from app.schemas.user import UserCreateRequest, UserUpdateRequest
from app.tests.utils.utils import random_email, random_lower_string


def test_create_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreateRequest(email=email, password=password)
    user = repositories.user.create(db, obj_in=user_in)
    assert user.email == email
    assert hasattr(user, "hashed_password")


def test_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreateRequest(email=email, password=password)
    user = repositories.user.create(db, obj_in=user_in)
    authenticated_user = repositories.user.authenticate(db, email=email, password=password)
    assert authenticated_user
    assert user.email == authenticated_user.email


def test_not_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user = repositories.user.authenticate(db, email=email, password=password)
    assert user is None


def test_check_if_user_is_active(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreateRequest(email=email, password=password)
    user = repositories.user.create(db, obj_in=user_in)
    is_active = repositories.user.is_active(user)
    assert is_active is True


def test_check_if_user_is_active_inactive(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreateRequest(email=email, password=password, disabled=True)
    user = repositories.user.create(db, obj_in=user_in)
    is_active = repositories.user.is_active(user)
    assert is_active


def test_check_if_user_is_superuser(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreateRequest(email=email, password=password, is_superuser=True)
    user = repositories.user.create(db, obj_in=user_in)
    is_superuser = repositories.user.is_superuser(user)
    assert is_superuser is True


def test_check_if_user_is_superuser_normal_user(db: Session) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreateRequest(email=username, password=password)
    user = repositories.user.create(db, obj_in=user_in)
    is_superuser = repositories.user.is_superuser(user)
    assert is_superuser is False


def test_get_user(db: Session) -> None:
    password = random_lower_string()
    username = random_email()
    user_in = UserCreateRequest(email=username, password=password, is_superuser=True)
    user = repositories.user.create(db, obj_in=user_in)
    user_2 = repositories.user.find(db, id=user.id)
    assert user_2
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


def test_update_user(db: Session) -> None:
    password = random_lower_string()
    email = random_email()
    user_in = UserCreateRequest(email=email, password=password, is_superuser=True)
    user = repositories.user.create(db, obj_in=user_in)
    new_password = random_lower_string()
    user_in_update = UserUpdateRequest(password=new_password, is_superuser=True)
    repositories.user.update(db, db_obj=user, obj_in=user_in_update)
    user_2 = repositories.user.find(db, id=user.id)
    assert user_2
    assert user.email == user_2.email
    assert verify_password(new_password, user_2.hashed_password)
