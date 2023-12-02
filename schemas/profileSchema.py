from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')

print("profile-schema")  # Añade esta líne

class Response(BaseModel, Generic[T]):
    code: str
    message: str
    result: Optional[T]

class ProfileSchema(BaseModel):
    id: Optional[int] = None
    name: str
    description: str

class ProfileEditSchema(BaseModel):
    name: str
    description: str

