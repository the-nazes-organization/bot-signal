from pydantic import BaseModel, Field


class BotProperties(BaseModel):
    account: str = Field(
        description="Number of the phone for the account to apply properties on",
        regex=r"^\+[0-9]*$",
    )
    group_id: int | None = Field(
        default=None, description="Group id in which the commands will take action"
    )
