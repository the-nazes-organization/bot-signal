from pydantic import BaseModel, Field


class NumberMap(BaseModel):
    number: str = Field(
            description="Phone number of the associated name",
            regex=r"^\+[0-9]{7,15}$"
        )
    name: str = Field(description="Name associated to the number")


class NumberMapUpdate(BaseModel):
    name: str = Field(description="Name associated to the number")
