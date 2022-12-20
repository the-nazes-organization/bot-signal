from pydantic import BaseModel, Field


class BotProperties(BaseModel):
    account: str = Field(
        description="Number of the phone for the account to apply properties on",
        regex=r"^\+[0-9]*$",
    )
    receiver_type: str = Field(
        default=None, description="Receiver type : two types allowed 'recipient' aka phone_number and 'group_id'"
    )
    receiver: str = Field(
        default=None, description="Receiver data based on the type"
    )
