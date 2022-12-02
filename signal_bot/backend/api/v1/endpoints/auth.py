from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.responses import RedirectResponse

from google_auth_oauthlib.flow import Flow

import logging

from signal_bot.backend.core.config import get_settings
from signal_bot.backend.core.security import Auth
from signal_bot.backend.core.data import get_google_config

from signal_bot.backend import schemas

settings = get_settings()
logger = logging.getLogger(__name__)


router = APIRouter()

@router.get("/") 
async def google_auth(
    request: Request,
    auth: Auth = Depends()
    ) -> RedirectResponse :

    flow = Flow.from_client_config(get_google_config(), settings.GOOGLE.SCOPES)
    flow.redirect_uri = request.url_for("google_auth_callback")
    auth_url, state = flow.authorization_url()

    if auth.inject_or_delete_state_token(state) is False:
        logger.info("State token already exists")

    return RedirectResponse(auth_url)


@router.get("/callback", response_model=schemas.AuthToken)
async def google_auth_callback(
    request: Request,
    state: str,
    code: str,
    auth: Auth = Depends()
) -> schemas.AuthToken :

    if auth.inject_or_delete_state_token(state, "delete") is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unknown state token"
        )

    flow = Flow.from_client_config(get_google_config(), settings.GOOGLE.SCOPES, state=state)
    flow.redirect_uri = request.url_for("google_auth_callback")
    flow.fetch_token(code=code)

    credentials = flow.credentials
    auth.is_id_token_valid(credentials.id_token)

    return schemas.AuthToken(access_token=credentials.id_token, token_type="bearer")
