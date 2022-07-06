from typing import List

from sqlalchemy.orm import Query as SQLQuery

from app.core.datatable import BaseDataTable, DataTableColumn
from app.models.user import User


class UserDataTable(BaseDataTable):
    def modified_datatable(self):
        (
            self
            .filter_column('full_name', lambda keyword: User.full_name.ilike(f"%{keyword}1%"))
            .add_column('full_name_extra', lambda record: record.full_name + "extra")
            .add_index_column('stt')
        )

    def query(self) -> SQLQuery:
        return self.session.query(User).filter(User.is_admin != True)

    @staticmethod
    def get_columns() -> List[DataTableColumn]:
        return [
            DataTableColumn(
                data=User.id,
                orderable=True,
            ),
            DataTableColumn(
                data=User.full_name,
                searchable=True,
            ),
            DataTableColumn(
                data=User.phone,
                searchable=True,
            ),
            DataTableColumn(
                data=User.email,
                searchable=True,
            )
        ]
