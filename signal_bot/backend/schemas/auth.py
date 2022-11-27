from pydantic import BaseModel


class AuthRedirect(BaseModel):
    redirect_url: str

class AuthToken(BaseModel):
    access_token: str
    type: str