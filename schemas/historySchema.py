from typing import TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')

class HistorySchema(BaseModel):
    id: Optional[int] = None
    description: Optional[str] = None
    company_id: Optional[int] = None
    sucursal_id: Optional[int] = None
    office_id: Optional[int] = None
    article_id: Optional[int] = None
    active_id: Optional[int] = None
    user_id: Optional[int] = None