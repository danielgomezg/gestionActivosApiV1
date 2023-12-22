from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')


class CompanySchema(BaseModel):
    name: str
    rut: str
    country: str
    contact_name: str
    contact_phone: str
    contact_email: str

class CompanyEditSchema(BaseModel):
    name: str
    contact_name: str
    contact_phone: str
    contact_email: str

class CompanySchemaIdName(BaseModel):
    id: Optional[int] = None
    name: str

