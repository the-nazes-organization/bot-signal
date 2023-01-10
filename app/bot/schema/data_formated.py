from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class User(BaseModel):
    nickname: str | None = None
    phone: str = Field(regex=r"^\+[0-9]{7,15}$")
    db_name: str | None = None


class AttachmentData(BaseModel):
    content_type: str
    filename: str
    size: int


class TypingStatus(str, Enum):
    STARTED = "STARTED"
    STOPPED = "STOPPED"


class Typing(BaseModel):
    status: TypingStatus


class Mention(BaseModel):
    user: User
    start: int
    length: int


class QuotedMessage(BaseModel):
    text: str
    author: User
    mentions: List[Mention] | None = None


class Message(BaseModel):
    text: str
    quote: QuotedMessage | None = None
    mentions: List[Mention] | None = None


class Reaction(BaseModel):
    reaction: str
    target_author: User
    sent_at: datetime


class DataFormated(BaseModel):
    id: str
    user: User
    sent_at: datetime
    message: Message | None = None
    typing: Typing | None = None
    reaction: Reaction | None = None
    attachments: List[AttachmentData] | None = None
