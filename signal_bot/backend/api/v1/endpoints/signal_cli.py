from fastapi import APIRouter, Query, HTTPException, status, Depends

from signal_bot.backend.dependencies import check_account_number
from signal_bot.backend import schemas
from signal_bot.backend import errors
from signal_bot.backend.message_client.Signal import SignalCliProcess

router = APIRouter()

@router.put("/", response_model=schemas.SignalCliProcessResponse, )
async def start_signal_cli(signal: SignalCliProcess = Depends()):
    try:
        pid = signal.start_cli_daemon()
    except errors.SignalCliProcessError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc)
        ) from exc
    return schemas.SignalCliProcessResponse(pid=pid)

@router.delete("/", response_model=schemas.SignalCliProcessResponse)
async def stop_signal_cli(signal: SignalCliProcess = Depends()):
    try:
        signal.stop_cli_daemon()
    except errors.SignalCliProcessError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        ) from exc
    return schemas.SignalCliProcessResponse()

@router.put("/register", response_model=schemas.SignalCliRegisterResponse)
async def register_account_signal(
    register: schemas.SignalRegister,
    account: str = Depends(check_account_number),
    signal: SignalCliProcess = Depends()
):
    try:
        output, code = signal.register(account, register.captcha_token)
    except errors.SignalCliError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        ) from exc
    return schemas.SignalCliRegisterResponse(information_cli=output, exit_code=code)

@router.put("/register/verify", response_model=schemas.SignalCliRegisterResponse)
async def verify_account_signal(
    verify: schemas.SignalRegisterVerify,
    account: str = Depends(check_account_number),
    signal: SignalCliProcess = Depends()
):
    try:
        output, code = signal.verify(account, verify.code)
    except errors.SignalCliError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        ) from exc
    return schemas.SignalCliRegisterResponse(information_cli=output, exit_code=code)