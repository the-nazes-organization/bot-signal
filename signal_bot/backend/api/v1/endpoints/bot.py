from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder

from signal_bot.backend import schemas
from signal_bot.backend import errors
from signal_bot.backend.message_client.Signal import SignalBotProcess

router = APIRouter()

@router.put("/", response_model=schemas.BotProcessResponse)
async def start_bot(
    properties: schemas.BotProperties,
    bot: SignalBotProcess = Depends()
):
    try:
        pid = bot.start_bot_daemon(jsonable_encoder(properties))
    except errors.SignalBotProcessError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc)
        ) from exc
    return schemas.BotProcessResponse(pid=pid)


@router.delete("/", response_model=schemas.BotProcessResponse)
async def stop_bot(bot: SignalBotProcess = Depends()):
    try:
        bot.stop_bot_daemon()
    except errors.SignalBotProcessError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        ) from exc
    return schemas.BotProcessResponse()