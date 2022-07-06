from typing import Any, Optional
from typing import Dict

from fastapi import FastAPI, Request, status, Response
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException


class VHTTPException(Exception):
    def __init__(self, status_code: int, message: str = None, errors: Any = None) -> None:
        self.status_code = status_code
        self.message = message
        self.errors = errors

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r}, message={self.message!r})"


class BadPayloadException(VHTTPException):
    def __init__(self, message: str, errors: Any = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            errors=errors
        )


def success_response(response: Response, message: str, data: Any, errors: Any = None,
                     status_code: int = status.HTTP_200_OK) -> Dict:
    response.status_code = status_code
    return {
        "success": True,
        "message": message,
        "data": data,
        "errors": errors,
    }


def error_response(response: Response, message: str, data: Any = None, errors: Any = None,
                   status_code: int = status.HTTP_400_BAD_REQUEST) -> Dict:
    response.status_code = status_code
    return {
        "success": False,
        "message": message,
        "data": data,
        "errors": errors,
    }


def init_app(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def custom_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder({
                "message": exc.detail,
                "success": False,
                "data": None,
                "errors": []
            }),
        )

    @app.exception_handler(IntegrityError)
    async def custom_exception_handler(request: Request, exc: IntegrityError):
        if "duplicate entry" in str(exc).lower():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=jsonable_encoder({
                    "message": "Data existed! Must change!",
                    "success": False,
                    "data": None,
                    "errors": []
                }),
            )
        raise

    @app.exception_handler(VHTTPException)
    async def custom_exception_handler(request: Request, exc: VHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder({
                "message": exc.message,
                "success": False,
                "data": None,
                "errors": exc.errors
            }),
        )

    @app.exception_handler(RequestValidationError)
    async def custom_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({
                "message": exc.errors()[0]['msg'],
                "success": False,
                "data": None,
                "errors": exc.errors()
            }),
        )

    # @app.exception_handler(Exception)
    # async def custom_exception_handler(request: Request, exc: Exception):
    #     return JSONResponse(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         content=jsonable_encoder({
    #             "message": str(exc),
    #             "success": False,
    #             "data": None,
    #             "errors": None
    #         }),
    #     )


class ResponseSchema(BaseModel):
    success: bool
    message: str
    data: Optional[Any]
    errors: Optional[Any]


class SuccessResponseSchema(BaseModel):
    success: bool = True
    message: str
    data: Optional[Any]
    errors: Optional[Any]


class ErrorResponseSchema(BaseModel):
    success: bool = False
    message: str
    data: Optional[Any]
    errors: Optional[Any]
