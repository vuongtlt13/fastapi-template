from typing import Optional, List

from pydantic import BaseModel, EmailStr

from app.core.datatable import DataTableResult
from app.core.response import ResponseSchema


# Shared properties
class UserBase(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_admin: Optional[bool] = False


class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class UserInfo(UserInDBBase):
    pass


# region Request/Response Schema
# Properties to receive via API on creation
class UserCreateRequest(UserBase):
    username: str
    password: str
    full_name: str


# Properties to receive via API on update
class UserUpdateRequest(UserBase):
    password: Optional[str] = None


# Response Schema
class UserResponse(ResponseSchema):
    data: Optional[UserInfo]


# endregion

# region datatable
class UserRecord(UserInfo):
    full_name_extra: Optional[str]
    stt: int


class UserDataTableResult(DataTableResult):
    items: List[UserRecord]


class UserDatatableResponse(ResponseSchema):
    data: UserDataTableResult
# endregion
