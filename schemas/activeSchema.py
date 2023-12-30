from typing import TypeVar, Optional
from pydantic import BaseModel
from datetime import date

T = TypeVar('T')

class ActiveSchema(BaseModel):
    #id: Optional[int] = None
    bar_code: str
    comment: Optional[str] = None
    acquisition_date: date
    accounting_document: Optional[str] = None
    accounting_record_number: str
    name_in_charge_active: str
    rut_in_charge_active: str
    serie: str
    model: str
    state: str
    #creation_date: date
    office_id: int
    article_id: int

class ActiveEditSchema(BaseModel):
    bar_code: str
    comment: Optional[str] = None
    acquisition_date: date
    accounting_document: Optional[str] = None
    accounting_record_number: str
    name_in_charge_active: str
    rut_in_charge_active: str
    serie: str
    model: str
    state: str
    #creation_date: datetime
    office_id: int
    #article_id: int