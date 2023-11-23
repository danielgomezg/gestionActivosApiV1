from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')

class Response(BaseModel, Generic[T]):
    code: str
    message: str
    result: Optional[T]

class OfficeSchema(BaseModel):
    id: Optional[int] = None
    description: str
    floor: int
    sucursal_id: int

class OfficeRequest(BaseModel):
    parameter: OfficeSchema = Field(...)