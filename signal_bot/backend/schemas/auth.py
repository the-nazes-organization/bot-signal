from pydantic import BaseModel


class AuthRedirect(BaseModel):
    redirect_url: str

class AuthIdToken(BaseModel):
    id_token: str