from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')


class Response(BaseModel, Generic[T]):
    code: str
    message: str
    result: Optional[T]

class ResponseGet(BaseModel, Generic[T]):
    code: str
    result: Optional[T]
    count: int
    limit: int
    offset: int


class UserSchema(BaseModel):
    id: Optional[int] = None
    firstName: str = None
    secondName: Optional[str] = None
    lastName: str = None
    secondLastName: Optional[str] = None
    email: str
    password: str
    rut: str = None
    company_id: Optional[int] = None
    profile_id: int

class UserEditSchema(BaseModel):
    firstName: Optional[str]
    secondName: Optional[str]
    lastName: Optional[str]
    secondLastName: Optional[str]
    email: Optional[str]
    #password: Optional[str]


class UserSchemaLogin(BaseModel):
    email: str
    password: str
