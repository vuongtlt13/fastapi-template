from typing import Optional

from pydantic import BaseModel


# Shared properties
class GroupBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    is_active: Optional[bool] = True
    is_supergroup: Optional[bool] = False


# Properties to receive via API on creation
class GroupCreate(GroupBase):
    name: str
    code: str
    description: Optional[str]


# Properties to receive via API on update
class GroupUpdate(GroupBase):
    name: str
    description: Optional[str]


class GroupInDBBase(GroupBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Group(GroupInDBBase):
    pass


# Additional properties stored in DB
class GroupInDB(GroupInDBBase):
    pass
