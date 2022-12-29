from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from signal_bot.backend import schemas
from signal_bot.backend.db.object_storage import ObjectStorage
from signal_bot.backend.api.dependencies import get_number_map_db

router = APIRouter()


@router.get("/", response_model=List[schemas.NumberMap])
async def read_numbers_map(
    db: ObjectStorage = Depends(get_number_map_db)
) -> schemas.NumberMap:
    return [schemas.NumberMap(name=key, number=value) for key, value in db.get_all().items()]


@router.post("/", response_model=schemas.NumberMap)
async def create_number_map(
    obj: schemas.NumberMap,
    db: ObjectStorage = Depends(get_number_map_db)
) -> schemas.NumberMap:
    if db.get(obj.name) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name already in used"
        )

    db.put(obj.name, obj.number)
    return obj


@router.put("/{name}", response_model=schemas.NumberMap)
async def update_number_map(
    name: str,
    obj: schemas.NumberMapUpdate,
    db: ObjectStorage = Depends(get_number_map_db)
) -> schemas.NumberMap:
    if db.get(name) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Name not found"
        )

    db.put(name, obj.number)
    return schemas.NumberMap(name=name, number=obj.number)


@router.get("/{name}", response_model=schemas.NumberMap)
async def read_number_map(
    name: str,
    db: ObjectStorage = Depends(get_number_map_db)
) -> schemas.NumberMap:
    number = db.get(name)
    if number is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Name not found"
        )
    return schemas.NumberMap(name=name, number=number)


@router.delete("/{name}", response_model=schemas.NumberMap)
async def delete_number_map(
    name: str,
    db: ObjectStorage = Depends(get_number_map_db)
) -> schemas.NumberMap:
    number = db.get(name)
    if number is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Name not found"
        )

    db.delete(name)
    return schemas.NumberMap(name=name, number=number)
