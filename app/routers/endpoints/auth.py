from app.core.auth import make_auth_router

router = make_auth_router(
    reset_password=False,
)
