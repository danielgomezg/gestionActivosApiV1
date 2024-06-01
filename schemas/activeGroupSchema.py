from typing import TypeVar
from pydantic import BaseModel

T = TypeVar('T')

class ActiveGroupSchema(BaseModel):
    name: str
