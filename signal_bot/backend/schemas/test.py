from typing import Optional

from pydantic import BaseModel


class Test(BaseModel):
    hello: Optional[str] = None
    world: Optional[bool] = True
