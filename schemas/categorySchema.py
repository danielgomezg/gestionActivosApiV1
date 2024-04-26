from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')


class CategorySchema(BaseModel):
    #level: str
    description: str
    code: str
    parent_id: int
    #client_code: Optional[str] = None

class CategoryEditSchema(BaseModel):
    description: str
    code: str
    #client_code: Optional[str] = None
