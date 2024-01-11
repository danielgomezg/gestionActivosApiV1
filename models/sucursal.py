from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base



class Sucursal(Base):
    __tablename__ = 'sucursal'
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String, nullable=False)
    number = Column(String, nullable=False)
    address = Column(String, nullable=False)
    region = Column(String, nullable=False)
    city = Column(String, nullable=True)
    commune = Column(String, nullable=False)
    removed = Column(Integer, default=0, nullable=False)

    company_id = Column(Integer, ForeignKey('compania.id'))
    company = relationship('Company', back_populates='sucursales')

    #Relacion con la tabla office
    office = relationship('Office', back_populates='sucursal')

    # Relacion con historial
    historial = relationship('History', back_populates='sucursal')


