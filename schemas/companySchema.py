from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')

print("compania-schema")  # Añade esta líne

class Response(BaseModel, Generic[T]):
    code: str
    message: str
    result: Optional[T]

class CompanySchema(BaseModel):
    id: Optional[int] = None
    name: str
    rut: str
    country: str
