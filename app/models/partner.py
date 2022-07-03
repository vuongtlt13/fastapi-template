from sqlalchemy import Column, String, BigInteger, Text

from app.core.model import Base
from app.core.string import random_string


class Partner(Base):
    id = Column(BigInteger, primary_key=True)

    code = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)

    tax_code = Column(String(255), unique=True, nullable=False)
    description = Column(Text(), nullable=True)

    api_key = Column(String(255), unique=True, nullable=False, default=random_string)
    api_secret = Column(String(255), nullable=False, default=random_string)
