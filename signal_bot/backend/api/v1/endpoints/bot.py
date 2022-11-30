from fastapi import APIRouter

from signal_bot.backend import schemas
from signal_bot.backend.message_client.Signal import SignalCliProcess

router = APIRouter()

@router.post("/start", response_model=schemas)
async def start_bot(account: str):
    return {}

@router.post("/stop/{bot_id}", response_model=schemas)
async def stop_bot(bot_id: str, account: str):
    return {}

@router.get("/list", response_model=schemas)
async def register_account_signal(account: str):
    return {}