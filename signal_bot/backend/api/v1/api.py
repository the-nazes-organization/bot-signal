from fastapi import APIRouter, Depends

from signal_bot.backend.api.v1.endpoints import (
    auth,
    test
)

from signal_bot.backend.core.security import get_auth_user

api_router = APIRouter()
api_router.include_router(test.router, prefix="/test", tags=["test"], dependencies=[Depends(get_auth_user)])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])