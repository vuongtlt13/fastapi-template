from typing import Any, Dict, Union

from sqlalchemy.orm import Session

from app.core.repository import BaseRepository
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreateRequest, UserUpdateRequest


class UserRepository(BaseRepository[User, UserCreateRequest, UserUpdateRequest], ):
    def create(self, db: Session, *, obj_in: UserCreateRequest) -> User:
        if obj_in.password:
            obj_in.password = get_password_hash(obj_in.password)

        return super().create(db, obj_in=obj_in)

    def update(
            self, db: Session, *, db_obj: User, obj_in: Union[UserUpdateRequest, Dict[str, Any]]
    ) -> User:
        if obj_in.password:
            obj_in.password = get_password_hash(obj_in.password)

        return super().update(db, db_obj=db_obj, obj_in=obj_in)

    def is_admin(self, user: User) -> bool:
        return user.is_admin


user_repo: UserRepository = UserRepository(User)
