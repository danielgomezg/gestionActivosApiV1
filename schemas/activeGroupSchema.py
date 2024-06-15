from typing import TypeVar
from pydantic import BaseModel

T = TypeVar('T')

class ActiveGroupSchema(BaseModel):
    name: str

class CollectionSchema(BaseModel):
    name: str
    activesId: list[int]