import json
import sys

import psutil
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder

from signal_bot.backend import schemas
from signal_bot.backend.core.config import get_settings
from signal_bot.backend.core.process_handler import ProcessHanlder
from signal_bot.backend.db.object_storage import ObjectStorage
from signal_bot.backend.dependencies import get_process_db

settings = get_settings()

router = APIRouter()


@router.put("/", status_code=status.HTTP_201_CREATED)
async def start_bot(
    properties: schemas.BotProperties,
    handler: ProcessHanlder = Depends(),
    db: ObjectStorage = Depends(get_process_db),
):
    if db.get("bot") is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No duplicate process allowed",
        )
    process = handler.start_process([sys.executable, settings.PYTHON_BOT_FILE], True)
    db.put("bot", process.pid)
    properties = jsonable_encoder(properties)
    properties["socket_file"] = settings.SOCKET_FILE
    process.stdin.write(json.dumps(properties).encode("utf-8"))
    process.stdin.close()


@router.delete("/")
async def stop_bot(
    handler: ProcessHanlder = Depends(), db: ObjectStorage = Depends(get_process_db)
):
    pid = db.get("bot")
    if pid is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No pid found"
        )
    try:
        handler.stop_process(pid)
    except psutil.NoSuchProcess as exc:
        db.delete("bot")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Process found not alive"
        )
    db.delete("bot")
