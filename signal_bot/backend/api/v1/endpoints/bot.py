from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder

from signal_bot.backend import schemas
from signal_bot.backend import errors
from signal_bot.backend.message_client.Signal import SignalBotProcess

router = APIRouter()

@router.post("/start", response_model=schemas.BotProcessResponse)
async def start_bot(properties: schemas.BotProperties):
    bot = SignalBotProcess()
    try:
        pid = bot.start_bot_daemon(jsonable_encoder(properties))
    except errors.SignalBotProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    return schemas.BotProcessResponse(pid=pid)

@router.post("/stop", response_model=schemas.BotProcessResponse)
async def stop_bot():
    bot = SignalBotProcess()
    try:
        bot.stop_bot_daemon()
    except errors.SignalBotProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return schemas.BotProcessResponse()