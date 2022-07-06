from fastapi import APIRouter, Depends

from app.dependency.common import get_current_user
from app.routers.endpoints import auth
# region import router
from app.routers.endpoints import users

# endregion

api_router = APIRouter()

# region include routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"], dependencies=[
    Depends(get_current_user)
])
# api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
# endregion
