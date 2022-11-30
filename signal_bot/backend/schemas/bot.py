from pydantic import BaseModel

class BotProperties(BaseModel):
    group_id: int | None = None