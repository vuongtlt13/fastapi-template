from fastapi import APIRouter

# region import router
from app.routers.endpoints import users
from app.routers.endpoints import auth
# endregion

api_router = APIRouter()

# region include routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
# endregion

