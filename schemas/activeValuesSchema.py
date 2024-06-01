from typing import TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')

class ActiveValuesSchema(BaseModel):
    adq_value: int
    real_value: int
    useful_life: int
    active_id: Optional[int]

class ActiveValuesEditSchema(BaseModel):
    adq_value: int
    real_value: int
    useful_life: int
