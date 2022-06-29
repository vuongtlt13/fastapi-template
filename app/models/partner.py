from sqlalchemy import Boolean, Column, String, BigInteger, TIMESTAMP, Text
from sqlalchemy.dialects.mysql import DOUBLE

from app.db.base_class import Base


class Partner(Base):
    id = Column(BigInteger, primary_key=True)

    code = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)

    tax_code = Column(String(255), unique=True, nullable=False)
    description = Column(Text(), nullable=True)

    api_key = Column(String(255), unique=True, nullable=False)
    api_secret = Column(String(255), nullable=False)
