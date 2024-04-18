from datetime import date
from pydantic import BaseModel

class ActiveTeoricSchema(BaseModel):
    bar_code: str
    acquisition_date: str
    description: str
    valor_adq: str
    valor_cont: str
