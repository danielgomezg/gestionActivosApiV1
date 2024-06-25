from sqlalchemy import Column, Integer
from database import Base

class SecuenciaVT(Base):
    __tablename__ = 'secuencia_vt'
    id = Column(Integer, primary_key=True, autoincrement=True)
    current_value = Column(Integer, nullable=False)