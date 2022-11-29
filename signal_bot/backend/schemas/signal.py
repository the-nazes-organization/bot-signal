from pydantic import BaseModel


class SignalRegister(BaseModel):
    captcha_token: str

class SignalRegisterVerify(BaseModel):
    code: str

class SignalBasicResponse(BaseModel):
    information_cli: str
    exit_code: int

class SignalCliProcessInfo(BaseModel):
    pid: int
    status: str