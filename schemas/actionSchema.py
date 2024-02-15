from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')


class ActionSchema(BaseModel):
    id: Optional[int] = None
    name: str