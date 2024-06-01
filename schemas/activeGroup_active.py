from typing import TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')

class ActiveGroup_ActiveSchema(BaseModel):
    activeGroup_id: int
    active_id: int