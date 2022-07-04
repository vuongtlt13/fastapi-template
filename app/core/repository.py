import inspect
import logging
from typing import Any, Dict, Generic, List, Optional, Type, Union
from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy import and_
from sqlalchemy.orm import Session, Query

from app.core.model import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

logger = logging.getLogger("uvicorn")


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def find(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def find_by_columns(self, db: Session, **kwargs) -> Optional[ModelType]:
        attributes = inspect.getmembers(self.model, lambda a: not (inspect.isroutine(a)))
        attr = {a[0]: a[1] for a in attributes if not (a[0].startswith('__') and a[0].endswith('__'))}
        filter_condition = and_(*[attr[column] == value for column, value in kwargs.items()])
        return db.query(self.model).filter(filter_condition).first()

    def get_multi(
            self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        try:
            db_obj: Base = self.model()
            db_obj.fill(obj_in)
            db.add(db_obj)
            db.commit()
            return db_obj
        except Exception as e:
            logger.error(str(e))
            db.rollback()
            raise

    def update(
            self,
            db: Session,
            *,
            db_obj: ModelType,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        try:
            db_obj.fill(obj_in)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            logger.error(str(e))
            db.rollback()
            return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def filter_by(self, db: Session, clauses: Dict[str, Any]) -> Query:
        query = db.query(self.model)
        query.filter_by(**clauses)
        print(clauses)
        return query
