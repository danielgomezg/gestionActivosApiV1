from typing import Generic, TypeVar, Optional
#from pydantic.generics import GenericModel
from pydantic import BaseModel, Field

T = TypeVar('T')

class Response(BaseModel, Generic[T]):
    code: str
    status: str
    message: str
    result: Optional[T]

class UserSchema(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    email: Optional[str] = None

class UserRequest(BaseModel):
    parameter: UserSchema = Field(...)