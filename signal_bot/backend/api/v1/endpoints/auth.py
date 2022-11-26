from fastapi import APIRouter, HTTPException, status

from google_auth_oauthlib.flow import Flow

import json

from signal_bot.backend.core.config import get_settings
from signal_bot.backend.core.security import is_id_token_valid
from signal_bot.backend import schemas

settings = get_settings()

router = APIRouter()

def inject_or_delete_state_token(state: str, type: str = "inject") -> bool :
    modif = False

    with open(settings.GOOGLE.AUTH_ANTIFORGERY_FILE, "r+") as antiforgery_file:

        antiforgery_obj = json.load(antiforgery_file)
        antiforgery_tokens : list = antiforgery_obj["tokens"]

        try:
            index_state = antiforgery_tokens.index(state)

            if type == "delete":
                antiforgery_tokens.pop(index_state)
                modif = True
    
        except ValueError:
            if type == "inject":
                antiforgery_tokens.append(state)
                modif = True

        if modif == True:
            antiforgery_file.seek(0)
            json.dump(antiforgery_obj, antiforgery_file)
            antiforgery_file.truncate()

    return modif



@router.get("/", response_model=schemas.AuthRedirect) 
async def google_auth() -> schemas.AuthRedirect :

    flow = Flow.from_client_secrets_file(settings.GOOGLE.CLIENT_SECRET_FILE, settings.GOOGLE.SCOPES)
    flow.redirect_uri = settings.GOOGLE.CALLBACK_URL
    auth_url, state = flow.authorization_url()

    if inject_or_delete_state_token(state) == False:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Couldnt store state token for securing Google Authent connection"
        )
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