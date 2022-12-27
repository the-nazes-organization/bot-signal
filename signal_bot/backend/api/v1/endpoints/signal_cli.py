import psutil
from fastapi import APIRouter, Depends, HTTPException, status

from signal_bot.backend import schemas
from signal_bot.backend.core.config import get_settings, get_signal_cli_config_path
from signal_bot.backend.core.process_handler import ProcessHanlder
from signal_bot.backend.db.object_storage import ObjectStorage
from signal_bot.backend.dependencies import check_account_number, get_process_db

settings = get_settings()

router = APIRouter()


@router.put("/", status_code=status.HTTP_201_CREATED)
async def put_signal_cli(
    handler: ProcessHanlder = Depends(), db: ObjectStorage = Depends(get_process_db)
):
    if db.get("cli") is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No duplicate process allowed",
        )
    process = handler.start_process(
        [
            "signal-cli",
            "--config",
            get_signal_cli_config_path(),
            "daemon",
            "--socket",
            settings.SOCKET_FILE,
            "--ignore-attachments",
            "--ignore-stories",
            "--send-read-receipts",
            "--no-receive-stdout",
        ],
        True,
    )
    db.put("cli", process.pid)


@router.delete("/")
async def stop_signal_cli(
    handler: ProcessHanlder = Depends(), db: ObjectStorage = Depends(get_process_db)
):
    pid = db.get("cli")
    if pid is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No pid found"
        )
    try:
        handler.stop_process(pid)
    except psutil.NoSuchProcess as exc:
        db.delete("cli")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Process found not alive"
        )
    db.delete("cli")


@router.put("/register", response_model=schemas.SignalCliRegisterResponse)
async def register_account_signal(
    register: schemas.SignalRegister,
    account: str = Depends(check_account_number),
    handler: ProcessHanlder = Depends(),
):
    process = handler.start_process(
        [
            "signal-cli",
            "--config",
            get_signal_cli_config_path(),
            "-a",
            account,
            "register",
            "--captcha",
            register.captcha_token
        ]
    )
    output = process.stdout.read()
    return schemas.SignalCliRegisterResponse(
        information_cli=output, exit_code=process.returncode
    )


@router.put("/register/verify", response_model=schemas.SignalCliRegisterResponse)
async def verify_account_signal(
    verify: schemas.SignalRegisterVerify,
    account: str = Depends(check_account_number),
    handler: ProcessHanlder = Depends(),
):
    process = handler.start_process(
        [
            "signal-cli",
            "--config",
            get_signal_cli_config_path(),
            "-a",
            account,
            "verify",
            verify.code
        ]
    )
    output = process.stdout.read()
    return schemas.SignalCliRegisterResponse(
        information_cli=output, exit_code=process.returncode
    )
