from pydantic import BaseModel, Field

class NumberMap(BaseModel):
    name: str = Field(
        description="Name associated to the number"
    )
    number: str = Field(
        description="Phone number of the associated name",
        regex=r"^\+[0-9]{7,15}$"
    )

class NumberMapUpdate(BaseModel):
    number: str = Field(
        description="Phone number of the associated name",
        regex=r"^\+[0-9]{7,15}$"
    )