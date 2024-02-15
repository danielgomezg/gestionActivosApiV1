from typing import TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')



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
    password: Optional[str] = None
    company_id: Optional[int] = None
    profile_id: Optional[int]


class UserSchemaLogin(BaseModel):
    email: str
    password: str
