from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base
from sqlalchemy.orm import relationship

class Office(Base):
    __tablename__ = 'oficina'
    id = Column(Integer, primary_key=True, autoincrement=True)
    description= Column(String, nullable=True)
    floor = Column(Integer, nullable=False)
    name_in_charge = Column(String, nullable=False)
    removed = Column(Integer, default=0, nullable=False)

    sucursal_id = Column(Integer, ForeignKey('sucursal.id'))

    sucursal = relationship('Sucursal', back_populates='office')

    actives = relationship('Active', back_populates='office')

    # Relacion con historial
    historial = relationship('History', back_populates='office')


