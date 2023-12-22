from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')

class ProfileActionSchema(BaseModel):
    id: Optional[int] = None
    action_id: int
    profile_id: int