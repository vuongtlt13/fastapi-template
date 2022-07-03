from sqlalchemy import Boolean, Column, String, BigInteger

from app.core.auth import AuthenticatableModel
from app.core.model import Base


class User(Base, AuthenticatableModel):
    id = Column(BigInteger, primary_key=True)

    # authentication info
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    phone = Column(String(255), unique=True, nullable=True)
    is_admin = Column(Boolean(), nullable=False, default=False)

    # relationships

    # others
    @staticmethod
    def username_column() -> str:
        return "username"
