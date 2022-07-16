import abc
import logging
import random
from dataclasses import dataclass, field
from enum import Enum
from logging import Logger
from typing import TypeVar, List, Any, Dict, Optional, Type, Callable, Union, Tuple

from fastapi import Response, Request, Query
from pydantic import BaseModel
from sqlalchemy import Column, or_
from sqlalchemy.orm import Session, Query as SQLQuery
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.core.logger import LOGGER
from app.core.response import BadPayloadException, success_response

ModelType = TypeVar("ModelType")
DEFAULT_LIMIT = 25
MAX_LIMIT = 100
ROW_INDEX_COLUMN_NAME_DEFAULT = "DT_RowIndex"

FilterColumnFunc = Callable[[str], Any]

local_logger = logging.getLogger("Datatable")


class DataTableColumn:
    def __init__(
            self,
            data: Union[Column, str],
            title: str = None,
            searchable: bool = False,
            orderable: bool = False,
            exportable: bool = False,
            printable: bool = False,
            class_name: str = '',
    ):
        title_from_data = data.key if isinstance(data, InstrumentedAttribute) else data
        self.title: str = title or title_from_data
        self.data = data
        self.searchable = searchable
        self.orderable = orderable
        self.exportable = exportable
        self.printable = printable
        self.class_name = class_name

        # closures
        self.filter: Optional[FilterColumnFunc] = None


class Action(str, Enum):
    AJAX = "ajax"
    EXCEL = "excel"
    # CSV = "csv"
    # PDF = "pdf"


class DataTableResult(BaseModel):
    totalRecords: int
    filteredRecords: int
    items: List[Any]
    others: Dict[str, Any]


@dataclass
class DataTableOption:
    request: Request
    keyword: str = ""
    page: int = 1
    limit: int = DEFAULT_LIMIT
    action: Action = Action.AJAX
    others: Dict[str, Any] = field(default_factory=dict)


class IBaseDataTable:
    def __init__(self):
        self.column_defs: Dict[str, DataTableColumn] = {}


class IModifiedDatatableAction:
    @abc.abstractmethod
    def add_column(self, column_name, producer: Callable[..., Any]):
        return self

    @abc.abstractmethod
    def filter_column(self, column_name: Union[str, Column], producer: FilterColumnFunc):
        return self

    @abc.abstractmethod
    def add_index_column(self, column_name: str = ROW_INDEX_COLUMN_NAME_DEFAULT):
        return self


class ModifiedDatatableAction(IModifiedDatatableAction, IBaseDataTable):
    def add_index_column(self, column_name: str = ROW_INDEX_COLUMN_NAME_DEFAULT):
        self.include_index = (True, column_name,)

    def __init__(self):
        super().__init__()
        self.additional_cols: List[Tuple[str, Callable]] = []
        self.include_index: Tuple[bool, Optional[str]] = (False, None,)

    def add_column(self, column_name: str, producer: Callable[..., Any]) -> IModifiedDatatableAction:
        self.additional_cols.append((column_name, producer,))
        return self

    def filter_column(self, column_name: Union[str, Column], producer: FilterColumnFunc) -> IModifiedDatatableAction:
        if isinstance(column_name, InstrumentedAttribute):
            column_name = column_name.key

        if column_name in self.column_defs:
            self.column_defs[column_name].filter = producer

        return self


class BaseDataTable(ModifiedDatatableAction):
    def __init__(
            self,
            max_limit: int = DEFAULT_LIMIT,
            smart_search: bool = True,
            logger: Logger = local_logger,
            **kwargs
    ):
        super().__init__()
        self._id = random.randint(1, 1000000000)
        self.logger = logger
        self.max_limit = max_limit
        self.smart_search = smart_search
        self.option: DataTableOption = DataTableOption(**kwargs)
        self.session: Optional[Session] = None

        # state
        self.column_defs: Dict[str, DataTableColumn] = {
            column.data.key: column
            for column in self.get_columns()
        }
        self.modified_datatable()
        self.query_statement: Optional[SQLQuery] = None

        # result
        self.prepared = False
        self.total_record: Optional[int] = None
        self.filtered_record: Optional[int] = None

    @staticmethod
    @abc.abstractmethod
    def get_columns() -> List[DataTableColumn]:
        pass

    @abc.abstractmethod
    def query(self) -> SQLQuery:
        raise NotImplementedError

    @abc.abstractmethod
    def modified_datatable(self):
        raise NotImplementedError

    async def render(self, db: Session, response: Response, extra: Dict = None) -> Any:
        # before call action
        self.session = db
        self.query_statement = self.query()

        # call action and get result
        if self.option.action == Action.AJAX:
            result = await self._call_ajax(
                response=response,
                extra=extra
            )
        else:
            result = []

        # after call action, clear init data
        self.session = None
        self.query_statement = None
        return result

    async def _call_ajax(self, response: Response, extra: Dict = None) -> Dict:
        try:
            self._prepare_query()
            result = await self._results()
            result = await self._process_result(result)
            return self._render_result(result, response=response, extra=extra)
        except Exception as e:
            LOGGER.error(str(e))
            raise BadPayloadException(
                message=f"Error when querying data!"
            )

    def _prepare_query(self):
        if not self.prepared:
            self.total_record = self._count_total()

            if self.total_record:
                self._filter_records()
                # self.ordering()
                self._paginate()

        self.prepared = True

    def _count_total(self) -> int:
        if self.total_record is None:
            return self._count()

        return self.total_record

    def _count(self):
        return self._prepare_count_query().count()

    def _prepare_count_query(self) -> SQLQuery:
        return self.query_statement

    def _filter_records(self):
        if self.smart_search:
            return self._do_smart_search()

        return self._do_search([self.option.keyword])

    def _do_smart_search(self):
        keywords = self.option.keyword.split(" ")
        keywords = list(filter(lambda x: x != "", keywords))
        return self._do_search(keywords)

    def _do_search(self, keywords: List[str]):
        keywords = list(set(keywords))
        searchable_cols = self._searchable_columns()
        filter_conditions = []
        for keyword in keywords:
            if keyword == "":
                continue
            for column in searchable_cols:
                if column.filter:
                    if keyword:
                        filter_conditions.append(column.filter(keyword))
                else:
                    if keyword and isinstance(column.data, InstrumentedAttribute):
                        filter_conditions.append(column.data.ilike(f'%{keyword}%'))
        if len(filter_conditions) > 0:
            self.query_statement = self.query_statement.filter(or_(*filter_conditions))

    def _searchable_columns(self) -> List[DataTableColumn]:
        return list(filter(lambda col: col.searchable, list(self.column_defs.values())))

    def _paginate(self):
        offset = self._start_index
        if offset > 0:
            self.query_statement = self.query_statement.offset(offset)
        self.query_statement = self.query_statement.limit(self.option.limit)

    async def _results(self) -> List[Any]:
        self.filtered_record = self.query_statement.count()
        return self.query_statement.all()

    def _render_result(self, result, response: Response, extra: Dict = None):
        if extra is None:
            extra = {}
        return success_response(
            response=response,
            data={
                "totalRecords": self.total_record,
                "filteredRecords": self.filtered_record,
                "items": result,
                "others": extra
            },
            message=""
        )

    async def _process_result(self, records: List):
        start = self._start_index
        for record in records:
            await self._add_column(record)
            if self.include_index[0]:
                start += 1
                setattr(record, self.include_index[1], start)

        return records

    async def _add_column(self, record):
        for column_name, producer in self.additional_cols:
            value = producer(record)
            setattr(record, column_name, value)

    @property
    def _start_index(self) -> int:
        return (self.option.page - 1) * self.option.limit


class UseDatatable:
    def __init__(
            self,
            base_cls: Type[BaseDataTable],
            max_limit: int = DEFAULT_LIMIT,
            smart_search: bool = True,
            logger: Logger = local_logger,
            **kwargs
    ):
        self.base_cls = base_cls
        self.max_limit = max_limit
        self.smart_search = smart_search
        self.logger = logger
        self.config = kwargs

    def __call__(
            self,
            request: Request,
            k: Optional[str] = Query(description="keyword for searching", default=""),
            p: Optional[int] = Query(description="Page", default=1, ge=1),
            ipp: Optional[int] = Query(description="Limit", default=DEFAULT_LIMIT, gt=0),
            action: Optional[Action] = Query(description="Action Type", default=Action.AJAX)
    ) -> BaseDataTable:
        if ipp > self.max_limit:
            raise BadPayloadException(
                message="Invalid `limit` params! Reach max limit!",
            )
        return self.base_cls(
            max_limit=self.max_limit,
            smart_search=self.smart_search,
            logger=self.logger,
            request=request,
            keyword=k.lower(),
            page=p,
            limit=ipp,
            action=action,
            **self.config
        )
