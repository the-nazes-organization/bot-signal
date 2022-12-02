from google.oauth2 import id_token
from google.auth import exceptions
from google.auth.transport import requests
from google_auth_oauthlib.flow import Flow

from fastapi import Header, HTTPException, status, Depends

import logging

from signal_bot.backend.core.config import get_settings
from signal_bot.backend.core.data import get_google_config
from signal_bot.backend.db import ObjectStorage
from signal_bot.backend.dependencies import get_user_db, get_state_db

settings = get_settings()
logger = logging.getLogger(__name__)

class Auth:
    """
    This class is used to manage the authentication of the user
    """

    def __init__(
        self,
        user_db: ObjectStorage = Depends(get_user_db),
        state_db: ObjectStorage = Depends(get_state_db)
    ) -> None:
        self.user_db = user_db
        self.state_db = state_db

    def is_user_whitelisted(self, info: str) -> bool :
        whitelist_obj = self.user_db.get(info)
        return True if whitelist_obj else False

    def is_id_token_valid(self, token : str):
        request = requests.Request()
        flow = Flow.from_client_config(get_google_config(), settings.GOOGLE.SCOPES)
        try:
            token_info = id_token.verify_oauth2_token(
                token,
                request,
                flow.client_config["client_id"]
            )
        except (exceptions.GoogleAuthError, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized authentication, token is invalid"
            ) from exc

        if not self.is_user_whitelisted(token_info["email"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden authentication, user is not whitelisted"
            )


    def inject_or_delete_state_token(self, state: str, flag: str = "inject") -> bool :
        modif = False

        antiforgery_obj = self.state_db.get(state)

        if flag == "inject":
            if antiforgery_obj is None:
                self.state_db.put(state, "1")
                logger.info("State token injected")
                modif = True

        elif flag == "delete":
            if antiforgery_obj is not None:
                self.state_db.delete(state)
                logger.info("State token deleted")
                modif = True

        return modif