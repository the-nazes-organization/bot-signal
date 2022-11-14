from pydantic import BaseModel
from typing import Optional


class Test(BaseModel):
    hello: Optional[str] = None
    world: Optional[bool] = True
