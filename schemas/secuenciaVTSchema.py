from typing import TypeVar
from pydantic import BaseModel

T = TypeVar('T')


class SecuenciaVTSchema(BaseModel):
    current_value: int