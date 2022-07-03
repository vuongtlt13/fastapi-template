from typing import Optional

from pydantic import BaseModel, EmailStr


# Shared properties
class UserBase(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_admin: Optional[bool] = False


# Properties to receive via API on creation
class UserCreate(UserBase):
    username: str
    password: str
    full_name: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class UserSchema(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
