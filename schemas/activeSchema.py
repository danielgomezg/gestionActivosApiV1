from typing import TypeVar, Optional
from pydantic import BaseModel
from datetime import date

T = TypeVar('T')

class ActiveSchema(BaseModel):
    bar_code: str
    virtual_code: Optional[str] = None
    comment: Optional[str] = None
    acquisition_date: date
    accounting_document: Optional[str] = None
    accounting_record_number: Optional[str] = None
    name_in_charge_active: Optional[str] = None
    rut_in_charge_active: Optional[str] = None
    serie: str
    model: str
    state: str
    brand: str
    photo1: Optional[str] = None
    photo2: Optional[str] = None
    photo3: Optional[str] = None
    photo4: Optional[str] = None
    office_id: int
    article_id: int
    maintenance_days: Optional[int] = None
    parent_code: Optional[str] = None

class ActiveEditSchema(BaseModel):
    bar_code: str
    virtual_code: Optional[str] = None
    comment: Optional[str] = None
    acquisition_date: date
    accounting_document: Optional[str] = None
    accounting_record_number: Optional[str] = None
    name_in_charge_active: Optional[str] = None
    rut_in_charge_active: Optional[str] = None
    serie: str
    model: str
    state: str
    brand: str
    photo1: Optional[str] = None
    photo2: Optional[str] = None
    photo3: Optional[str] = None
    photo4: Optional[str] = None
    office_id: int
    article_id: int
    maintenance_days: Optional[int] = None
    parent_code: Optional[str] = None