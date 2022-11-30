from google.oauth2 import id_token
from google.auth import exceptions
from google.auth.transport import requests
from google_auth_oauthlib.flow import Flow

from fastapi import HTTPException, status

import sys

from signal_bot.backend.core.config import get_settings
from signal_bot.backend.core.data import get_google_config
from signal_bot.backend.db import DbManager

settings = get_settings()

def is_user_whitelisted(type: str, info: str) -> bool :
    db = DbManager.Db()
    whitelist_obj = db.get_users_whitelisted()
    return True if whitelist_obj[type].get(info, False) else False

def is_id_token_valid(token : str):
    invalidTokenException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized authentication"
    )

    request = requests.Request()
    flow = Flow.from_client_config(get_google_config(), settings.GOOGLE.SCOPES)
    try:
        token_info = id_token.verify_oauth2_token(token, request, flow.client_config["client_id"])
    except (exceptions.GoogleAuthError, ValueError):
        raise invalidTokenException

    # To check sub value for everybody account because sub is unique email can change
    # sys.stdout.write(json.dumps(token_info))
    if not is_user_whitelisted("email", token_info["email"]):
        raise invalidTokenException