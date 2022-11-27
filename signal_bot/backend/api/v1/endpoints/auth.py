from fastapi import APIRouter, HTTPException, status

from google_auth_oauthlib.flow import Flow

import json

from signal_bot.backend.core.config import get_settings
from signal_bot.backend.core.security import is_id_token_valid
from signal_bot.backend import schemas

settings = get_settings()
logger = logging.getLogger(__name__)


router = APIRouter()

def inject_or_delete_state_token(state: str, type: str = "inject") -> bool :
    modif = False

    with open(settings.GOOGLE.AUTH_ANTIFORGERY_FILE, "r+") as antiforgery_file:
        antiforgery_obj = json.load(antiforgery_file)

    if type == "inject":
        if antiforgery_obj.get(state) == None:
            antiforgery_obj[state] = True
            modif = True
            logger.info("State token injected")
        
    elif type == "delete":
        if antiforgery_obj.get(state, None) != None:
            del antiforgery_obj[state]
            modif = True
            logger.info("State token deleted")

    if modif:
        with open(settings.GOOGLE.AUTH_ANTIFORGERY_FILE, "w") as antiforgery_file:
            json.dump(antiforgery_obj, antiforgery_file)

    return modif



@router.get("/", response_model=schemas.AuthRedirect) 
async def google_auth() -> schemas.AuthRedirect :

    flow = Flow.from_client_secrets_file(settings.GOOGLE.CLIENT_SECRET_FILE, settings.GOOGLE.SCOPES)
    flow.redirect_uri = settings.GOOGLE.CALLBACK_URL
    auth_url, state = flow.authorization_url()

    if inject_or_delete_state_token(state) == False:
        logger.info("State token already exists")

    return {"redirect_url": auth_url}

@router.get("/callback", response_model=schemas.AuthIdToken)
async def google_auth_callback(state: str, code: str) -> schemas.AuthIdToken :

    if inject_or_delete_state_token(state, "delete") == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unknown state token"
        )

    flow = Flow.from_client_secrets_file(settings.GOOGLE.CLIENT_SECRET_FILE, settings.GOOGLE.SCOPES, state=state)
    flow.redirect_uri = settings.GOOGLE.CALLBACK_URL

    flow.fetch_token(code=code)

    credentials = flow.credentials
    is_id_token_valid(credentials.id_token)

    return {"id_token": credentials.id_token}