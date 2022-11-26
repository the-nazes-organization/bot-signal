from fastapi import APIRouter

from signal_bot.backend import schemas

router = APIRouter()

@router.get("/", response_model=schemas.Test)
def test_hello():
    return {"hello": "jojo", "world": True}
