from typing import Generic, TypeVar, Optional
#from pydantic.generics import GenericModel
from pydantic import BaseModel, Field

T = TypeVar('T')

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

class UserRequest(BaseModel):
    parameter: UserSchema = Field(...)