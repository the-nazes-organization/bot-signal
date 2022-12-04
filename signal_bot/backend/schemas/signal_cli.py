from pydantic import BaseModel, Field


class SignalRegister(BaseModel):
    captcha_token: str = Field(
        description="Token created on https://signalcaptchas.org/registration/generate.html or \
        for staging https://signalcaptchas.org/staging/registration/generate.html, after completion the token is found \
        in the url link, the part after signalcaptcha:// is the token."
    )


class SignalRegisterVerify(BaseModel):
    code: str = Field(
        description="Code received through a text message on the mobile for the account",
        regex="^[0-9]{6}$",
    )


class SignalCliRegisterResponse(BaseModel):
    information_cli: str = Field(description="Output from signal-cli")
    exit_code: int = Field(description="Exit code from signal-cli")
