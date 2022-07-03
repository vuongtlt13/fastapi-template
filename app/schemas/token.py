from typing import Optional, Union

from pydantic import BaseModel

from app.core.response import ResponseSchema


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenSchema(ResponseSchema):
    data: Token


class TokenPayload(BaseModel):
    sub: Optional[Union[int, str]] = None


class TokenPayloadSchema(ResponseSchema):
    data: TokenPayload
