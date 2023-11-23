from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base
from sqlalchemy.orm import relationship, validates
from sqlalchemy.orm.exc import NoResultFound
from api.endpoints.sucursal import get_sucursal

class Office(Base):
    __tablename__ = 'oficina'
    id = Column(Integer, primary_key=True, autoincrement=True)
    description= Column(String, nullable=False)
    floor = Column(Integer, nullable=False)

    sucursal_id = Column(Integer, ForeignKey('sucursal.id'))

    sucursal = relationship('Sucursal', back_populates='office')

    @validates('sucursal_id')
    def validate_sucursal_id(self, key, sucursal_id):
        try:
            print("validate")
            # Intenta buscar una sucursal con el ID proporcionado
            sucursal = get_sucursal(sucursal_id)
            print(sucursal)
            return sucursal_id
        except NoResultFound:
            # Si no se encuentra la empresa, levanta una excepción
            raise ValueError(f"No existe una sucursal con el ID {sucursal_id}")

