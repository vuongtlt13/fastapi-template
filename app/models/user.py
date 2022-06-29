from sqlalchemy import Boolean, Column, String, BigInteger, TIMESTAMP
from sqlalchemy.dialects.mysql import DOUBLE

from app.db.base_class import Base


class User(Base):
    id = Column(BigInteger, primary_key=True)

    # authentication info
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    # general info
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    phone = Column(String(255), unique=True, nullable=True)
    email_activated_at = Column(TIMESTAMP)

    # relationships
