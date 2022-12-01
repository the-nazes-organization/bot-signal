from fastapi import APIRouter, Query, HTTPException, status, Depends

from signal_bot.backend import schemas
from signal_bot.backend import errors
from signal_bot.backend.api import deps
from signal_bot.backend.message_client.Signal import SignalCliProcess

router = APIRouter()

@router.post("/start", response_model=schemas.SignalCliProcessResponse)
async def start_signal_cli():
    signal = SignalCliProcess()
    try:
        pid = signal.start_cli_daemon()
    except errors.SignalCliProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    return schemas.SignalCliProcessResponse(pid=pid)

@router.post("/stop", response_model=schemas.SignalCliProcessResponse)
async def stop_signal_cli():
    signal = SignalCliProcess()
    try:
        signal.stop_cli_daemon()
    except errors.SignalCliProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return schemas.SignalCliProcessResponse()

@router.post("/register", response_model=schemas.SignalCliRegisterResponse)
async def register_account_signal(register: schemas.SignalRegister, account: str = Depends(deps.check_account_number)):
    signal = SignalCliProcess()
    try:
        output, code = signal.register(account, register.captcha_token)
    except errors.SignalCliError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return schemas.SignalCliRegisterResponse(information_cli=output, exit_code=code)

@router.post("/register/verify", response_model=schemas.SignalCliRegisterResponse)
async def verify_account_signal(verify: schemas.SignalRegisterVerify, account: str = Depends(deps.check_account_number)):
    signal = SignalCliProcess()
    try:
        output, code = signal.verify(account, verify.code)
    except errors.SignalCliError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return schemas.SignalCliRegisterResponse(information_cli=output, exit_code=code)