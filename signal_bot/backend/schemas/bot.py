from pydantic import BaseModel, Field
from enum import Enum

class ReceiverType(str, Enum):
    recipient = "recipient"
    group_id = "group_id"

class BotProperties(BaseModel):
    account: str = Field(
        description="Number of the phone for the account to apply properties on",
        regex=r"^\+[0-9]{7,15}$",
    )
    receiver_type: ReceiverType = Field(
        description=(
            "Receiver type : two types allowed 'recipient' aka phone_number and"
            " 'group_id'"
        ),
    )
    receiver: str = Field(
        description="Receiver data, can be a phone number for recipient or a string of the group_id"
    )
