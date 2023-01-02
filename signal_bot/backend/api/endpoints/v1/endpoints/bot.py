from typing import List
import json
import sys

import psutil
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder

from signal_bot.backend import schemas
from signal_bot.backend.core.config import get_settings
from signal_bot.backend.core.process_handler import ProcessHandler
from signal_bot.backend.db.object_storage import ObjectStorage
from signal_bot.backend.api.dependencies import get_process_db, get_number_map_db, check_path_number

settings = get_settings()

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def start_bot(
    properties: schemas.BotProperties,
    handler: ProcessHandler = Depends(),
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
    process.stdin.write(json.dumps(properties).encode("utf-8"))
    process.stdin.close()


@router.delete("/")
async def stop_bot(
    handler: ProcessHandler = Depends(), db: ObjectStorage = Depends(get_process_db)
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
        ) from exc
    db.delete("bot")



@router.get("/numbermap", response_model=List[schemas.NumberMap])
async def read_numbers_map(
    db: ObjectStorage = Depends(get_number_map_db)
) -> schemas.NumberMap:
    return [schemas.NumberMap(number=key, name=value) for key, value in db.get_all().items()]


@router.post("/numbermap", response_model=schemas.NumberMap)
async def create_number_map(
    obj: schemas.NumberMap,
    db: ObjectStorage = Depends(get_number_map_db)
) -> schemas.NumberMap:
    if db.get(obj.number) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Number already in used"
        )

    db.put(obj.number, obj.name)
    return obj


@router.put("/numbermap/{number}", response_model=schemas.NumberMap)
async def update_number_map(
    obj: schemas.NumberMapUpdate,
    number: str = Depends(check_path_number),
    db: ObjectStorage = Depends(get_number_map_db)
) -> schemas.NumberMap:
    if db.get(number) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Number not found"
        )

    db.put(number, obj.name)
    return schemas.NumberMap(number=number, name=obj.name)


@router.get("/numbermap/{number}", response_model=schemas.NumberMap)
async def read_number_map(
    number: str = Depends(check_path_number),
    db: ObjectStorage = Depends(get_number_map_db)
) -> schemas.NumberMap:
    name = db.get(number)
    if name is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Number not found"
        )
    return schemas.NumberMap(number=number, name=name)


@router.delete("/numbermap/{number}", response_model=schemas.NumberMap)
async def delete_number_map(
    number: str = Depends(check_path_number),
    db: ObjectStorage = Depends(get_number_map_db)
) -> schemas.NumberMap:
    name = db.get(number)
    if name is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Number not found"
        )

    db.delete(number)
    return schemas.NumberMap(number=number, name=name)
