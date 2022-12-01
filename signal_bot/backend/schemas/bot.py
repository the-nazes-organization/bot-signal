from pydantic import BaseModel, Field

class BotProcessResponse(BaseModel):
    information: str = Field(
        default="",
        description="Information about bot process"
    )
    pid: int = Field(
        default=0,
        description="Pid of bot process"
    )

class BotProperties(BaseModel):
    account: str = Field(
        description="Number of the phone for the account to apply properties on",
        regex="^\+[0-9]*$"
    )
    group_id: int | None = Field(
        default=None,
        description="Group id in which the commands will take action"
    )