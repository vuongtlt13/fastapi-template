from sqlalchemy import Boolean, Column, String, BigInteger, TIMESTAMP
from sqlalchemy.dialects.mysql import DOUBLE

from app.db.base_class import Base


class User(Base):
    id = Column(BigInteger, primary_key=True)

    # authentication info
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    # general info
    full_name = Column(String(255), nullable=False)
    email_activated_at = Column(TIMESTAMP)

    # client info
    client_key = Column(String(255), nullable=False, unique=True)
    client_secret = Column(String(255), nullable=False, unique=True)
    is_client = Column(Boolean(), server_default="1")

    # status info
    balance = Column(DOUBLE(), server_default="0.0")
    is_active = Column(Boolean(), server_default="1")

    # relationships
