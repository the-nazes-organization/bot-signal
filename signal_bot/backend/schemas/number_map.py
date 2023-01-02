from pydantic import BaseModel, Field

from signal_bot.backend.core.config import get_settings

settings = get_settings()

class NumberMap(BaseModel):
    number: str = Field(
        description="Phone number of the associated name",
        regex=settings.NUMBER_FORMAT_REGEX
    )
    name: str = Field(
        description="Name associated to the number"
    )

class NumberMapUpdate(BaseModel):
    name: str = Field(
        description="Name associated to the number"
    )
