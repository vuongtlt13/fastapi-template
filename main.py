import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core import response
from app.core.config import settings
from app.core.response import SuccessResponseSchema, ErrorResponseSchema
from app.routers.api import api_router

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_STR}/openapi.json",
    responses={
        '200': {
            "model": SuccessResponseSchema
        },
        '400': {
            "model": ErrorResponseSchema
        },
        '401': {
            "model": ErrorResponseSchema
        },
        '403': {
            "model": ErrorResponseSchema
        },
        '422': {
            "model": ErrorResponseSchema
        }
    }
)

response.init_app(app)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_STR)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
