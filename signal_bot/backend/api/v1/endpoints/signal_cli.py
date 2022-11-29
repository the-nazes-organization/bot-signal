from fastapi import APIRouter

from signal_bot.backend import schemas
from signal_bot.backend.message_client.Signal import SignalCliProcess

router = APIRouter()

@router.post("/start", response_model=schemas.SignalCliProcessInfo)
async def start_signal_cli(account: str):
    signal = SignalCliProcess(account=account)
    return signal.start_cli_daemon()

@router.post("/stop", response_model=schemas.SignalCliProcessInfo)
async def stop_signal_cli(account: str):
    signal = SignalCliProcess(account=account)
    return signal.stop_cli_daemon()

@router.post("/register", response_model=schemas.SignalBasicResponse)
async def register_account_signal(account: str, register: schemas.SignalRegister):
    signal = SignalCliProcess(account=account)
    return signal.register(register.captcha_token)

@router.post("/register/verify", response_model=schemas.SignalBasicResponse)
async def verify_account_signal(account: str, verify: schemas.SignalRegisterVerify):
    signal = SignalCliProcess(account=account)
    return signal.verify(verify.code)