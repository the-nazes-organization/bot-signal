from enum import Enum

from pydantic import BaseModel, Field

from signal_bot.backend.core.config import get_settings

settings = get_settings()

class ReceiverType(str, Enum):
    RECIPIENT = "recipient"
    GROUP_ID = "group_id"

class BotProperties(BaseModel):
    account: str = Field(
        description="Number of the phone for the account to apply properties on",
        regex=settings.NUMBER_FORMAT_REGEX,
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
