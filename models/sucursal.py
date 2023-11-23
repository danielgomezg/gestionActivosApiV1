from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, validates
from sqlalchemy.orm.exc import NoResultFound
from database import Base
from models.company import Company

from api.endpoints.company import get_company
from crud.company import get_company_by_id
from fastapi import Depends
from database import get_db


class Sucursal(Base):
    __tablename__ = 'sucursal'
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String, nullable=False)
    number = Column(String, nullable=False, unique=True)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    commune = Column(String, nullable=False)

    company_id = Column(Integer, ForeignKey('compania.id'))

    company = relationship('Company', back_populates='sucursales')

    #Relacion con la tabla office
    office = relationship('Office', back_populates='sucursal')

    @validates('company_id')
    def validate_company_id(self, key, company_id):
        try:
            # Intenta buscar una empresa con el ID proporcionado
            print("acaaaaa")
            company = get_company(company_id)
            print(company)
            return company_id
        except NoResultFound:
            # Si no se encuentra la empresa, levanta una excepción
            raise ValueError(f"No existe una empresa con el ID {company_id}")

