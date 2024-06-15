import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from database import Base
from sqlalchemy.orm import relationship
from datetime import date

class ActiveGroup(Base):
    __tablename__ = 'grupoActivo'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    creation_date = Column(Date, default=date.today, nullable=False)
    removed = Column(Integer, default=0, nullable=False)

    # Relacion con tabla intermedia activeGroup_active
    activeGroup_active = relationship('Active_GroupActive', back_populates='activeGroup')