from fastapi import APIRouter, Depends

from app.backend.api.v1.endpoints import auth, bot, signal_cli
from app.backend.core.security import get_auth_user

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

api_router.include_router(
    signal_cli.router,
    prefix="/signalcli",
    tags=["signalcli"],
    dependencies=[Depends(get_auth_user)],
)

api_router.include_router(
    bot.router, prefix="/bot", tags=["bot"], dependencies=[Depends(get_auth_user)]
)
