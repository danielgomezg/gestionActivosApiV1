from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class Action(Base):
    __tablename__ = 'accion'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    removed = Column(Integer, default=0, nullable=False)

    # Relacion con sucursales
    profileActions = relationship('ProfileAction', back_populates='action')