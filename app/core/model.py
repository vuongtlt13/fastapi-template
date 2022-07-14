from typing import Any, Dict, Union

from inflection import underscore, pluralize
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, func, inspect
from sqlalchemy.ext.declarative import as_declarative, declared_attr


class ModelHelper:
    def __init__(self):
        self.v_dirty_columns: Dict[str, Any] = {}

    @declared_attr
    def v_dirty_columns(self) -> Dict[str, Any]:
        return {}

    def columns(self):
        return inspect(self.__class__).c

    def fill(self, data: Union[Dict, BaseModel]):
        if isinstance(data, BaseModel):
            data = data.dict(exclude_unset=True)
        for field, value in data.items():
            if hasattr(self, field):
                setattr(self, field, value)

    def is_dirty(self, colum_name: str = None) -> bool:
        if colum_name:
            return colum_name in self.v_dirty_columns

        return len(self.v_dirty_columns.keys()) > 0

    def get_origin(self, column_name: str) -> Any:
        if column_name in self.v_dirty_columns:
            return self.v_dirty_columns[column_name]

        if column_name in self.columns():
            return getattr(self, column_name)

        raise ValueError(f"Column `{column_name}` not found in `{self.__class__}`")

    def __setattr__(self, key, value):
        if hasattr(self, 'v_dirty_columns'):
            try:
                origin_value = getattr(self, key)
            except AttributeError:
                origin_value = None

            new_value = value
            is_changed = new_value != origin_value
            is_column = key in self.columns()
            if is_column and is_changed:
                self.v_dirty_columns[key] = origin_value

        super().__setattr__(key, value)


@as_declarative()
class Base(ModelHelper):
    id: Any
    __name__: str

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        super().__init__()

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


class AuthenticatableModel:
    id: Any
    password: Any

    @declared_attr
    def is_authenticatable(self) -> bool:
        return True

    @staticmethod
    def username_column() -> str:
        return "email"

    # @declared_attr
    # def username(self) -> str:
    #     return getattr(self, self.username_column())
