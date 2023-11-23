from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')

class Response(BaseModel, Generic[T]):
    code: str
    message: str
    result: Optional[T]

class SucursalSchema(BaseModel):
    id: Optional[int] = None
    description: str
    number: str = None
    address: str
    city: str = None
    commune: str = None
    company_id: int

class SucursalRequest(BaseModel):
    parameter: SucursalSchema = Field(...)