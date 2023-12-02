from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')

print("user-schema")  # Añade esta líne

class Response(BaseModel, Generic[T]):
    code: str
    message: str
    result: Optional[T]

class UserSchema(BaseModel):
    id: Optional[int] = None
    firstName: str = None
    secondName: Optional[str] = None
    lastName: str = None
    secondLastName: Optional[str] = None
    email: str
    password: str
    rut: str = None
    company_id: int
    profile_id: int

class UserEditSchema(BaseModel):
    firstName: Optional[str]
    secondName: Optional[str]
    lastName: Optional[str]
    secondLastName: Optional[str]
    email: Optional[str]
    password: Optional[str]


class UserSchemaTest(BaseModel):
    username: str
    password: str
