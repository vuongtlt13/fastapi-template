from typing import Any, Dict, Union

from inflection import underscore, pluralize
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    id: Any
    __name__: str

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(self) -> str:
        return underscore(pluralize(self.__name__))

    @declared_attr
    def created_at(self):
        return Column(DateTime(timezone=True),
                      server_default=func.now(), default=func.now(),
                      nullable=False)

    @declared_attr
    def updated_at(self):
        return Column(DateTime(timezone=True), server_default=func.now(),
                      default=func.now(), nullable=False, onupdate=func.now())

    def fill(self, data: Union[Dict, BaseModel]):
        if isinstance(data, BaseModel):
            data = data.dict(exclude_unset=True)
        for field, value in data.items():
            if hasattr(self, field):
                setattr(self, field, value)


class AuthenticatableModel:
    id: Any
    password: Any

    @declared_attr
    def is_authenticatable(self) -> bool:
        return True

    @staticmethod
    def username_column() -> str:
        return "email"

    @declared_attr
    def username(self) -> str:
        return getattr(self, self.username_column())
