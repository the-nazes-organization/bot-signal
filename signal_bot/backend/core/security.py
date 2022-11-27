from google.oauth2 import id_token
from google.auth import exceptions
from google.auth.transport import requests
from google_auth_oauthlib.flow import Flow

from fastapi import Depends, Header, HTTPException, status

import json, sys

from signal_bot.backend.core.config import get_settings

settings = get_settings()

def is_user_whitelisted(type: str, info: str) -> bool:
    with open(settings.WHITELIST_FILE, "r") as whitelist_file:
        whitelist_obj = json.load(whitelist_file)
        whitelisted_infos : list = whitelist_obj[type]
        try:
            whitelisted_infos.index(info)
            return True
        except ValueError:
            pass
    return False

def is_id_token_valid(token : str):
    invalidTokenException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized authentication"
    )

    request = requests.Request()
    flow = Flow.from_client_secrets_file(settings.GOOGLE.CLIENT_SECRET_FILE, settings.GOOGLE.SCOPES)
    try:
        token_info = id_token.verify_oauth2_token(token, request, flow.client_config["client_id"])
    except (exceptions.GoogleAuthError, ValueError):
        raise invalidTokenException

    # To check sub value for everybody account because sub is unique email can change
    # sys.stdout.write(json.dumps(token_info))
    if is_user_whitelisted("email", token_info["email"]) == False:
        raise invalidTokenException

def get_auth_user(authorization: str = Header()):
    header_shredded = authorization.split("Bearer ")
    is_id_token_valid(header_shredded[1])

def get_file_secret():
    return {
	    "web": {
		    "client_id": settings.GOOGLE.CLIENT_ID,
		    "project_id": "signal-bot-368420",
		    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
		    "token_uri": "https://oauth2.googleapis.com/token",
		    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
		    "client_secret": settings.GOOGLE.CLIENT_SECRET,
		    "redirect_uris": [
			    "http://127.0.0.1:8000"
		    ]
	    }
    }