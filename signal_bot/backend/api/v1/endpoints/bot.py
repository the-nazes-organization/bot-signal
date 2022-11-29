from fastapi import APIRouter

from signal_bot.backend import schemas
from signal_bot.backend.message_client.Signal import SignalCliProcess

router = APIRouter()

@router.post("/start", response_model=schemas)
async def start_signal_cli(account: str):
    return {}

@router.post("/stop", response_model=schemas)
async def stop_signal_cli(account: str):
    return {}

@router.get("/list", response_model=schemas)
async def register_account_signal(account: str):
    return {}