from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')


class CategorySchema(BaseModel):
    level: str
    description: str
    father_id: str
    client_code: Optional[str] = None

class CategoryEditSchema(BaseModel):
    description: str
    client_code: Optional[str] = None
