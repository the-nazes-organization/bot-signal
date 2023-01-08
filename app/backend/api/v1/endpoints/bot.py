import sys
from typing import List

import psutil
from fastapi import APIRouter, Depends, HTTPException, status

from app.backend.schemas.bot import BotProperties
from app.backend.schemas.number_map import NumberMap, NumberMapUpdate
from app.backend.api.dependencies import (
    check_path_number,
    get_number_map_db,
    get_process_db,
)
from app.backend.core.process_handler import ProcessHandler
from app.config import get_settings
from app.db.object_storage import ObjectStorage

settings = get_settings()

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def start_bot(
    properties: BotProperties,
    handler: ProcessHandler = Depends(),
    db: ObjectStorage = Depends(get_process_db),
):
    pid = db.get("bot")
    if pid is not None:
        if handler.is_process_alive(pid):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No duplicate process allowed",
            )
        print("Process not found, starting new one")
        db.delete("bot")
    process = handler.start_process(
        [
            sys.executable,
            settings.PYTHON_BOT_FILE,
            "--account",
            properties.account,
            "--receiver_type",
            properties.receiver_type,
            "--receiver",
            properties.receiver,
        ],
        True,
    )
    handler.log_process(process)
    db.put("bot", process.pid)


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


@router.get("/numbermap", response_model=List[NumberMap])
async def read_numbers_map(
    db: ObjectStorage = Depends(get_number_map_db),
) -> NumberMap:
    return [
        NumberMap(number=key, name=value) for key, value in db.get_all().items()
    ]


@router.post("/numbermap", response_model=NumberMap)
async def create_number_map(
    obj: NumberMap, db: ObjectStorage = Depends(get_number_map_db)
) -> NumberMap:
    if db.get(obj.number) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Number already in used"
        )

    db.put(obj.number, obj.name)
    return obj


@router.put("/numbermap/{number}", response_model=NumberMap)
async def update_number_map(
    obj: NumberMapUpdate,
    number: str = Depends(check_path_number),
    db: ObjectStorage = Depends(get_number_map_db),
) -> NumberMap:
    if db.get(number) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Number not found"
        )

    db.put(number, obj.name)
    return NumberMap(number=number, name=obj.name)


@router.get("/numbermap/{number}", response_model=NumberMap)
async def read_number_map(
    number: str = Depends(check_path_number),
    db: ObjectStorage = Depends(get_number_map_db),
) -> NumberMap:
    name = db.get(number)
    if name is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Number not found"
        )
    return NumberMap(number=number, name=name)


@router.delete("/numbermap/{number}", response_model=NumberMap)
async def delete_number_map(
    number: str = Depends(check_path_number),
    db: ObjectStorage = Depends(get_number_map_db),
) -> NumberMap:
    name = db.get(number)
    if name is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Number not found"
        )

    db.delete(number)
    return NumberMap(number=number, name=name)
