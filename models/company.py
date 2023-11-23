from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class Company(Base):
    __tablename__ = 'compania'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    rut = Column(String, unique=True, nullable=False)
    country = Column(String, nullable=False)

    sucursales = relationship('Sucursal', back_populates='company')


# from sqlalchemy import Table, Column
# from sqlalchemy.sql.sqltypes import Integer, String
# #from database import meta, engine
# from database import Base
#
# class Company(Base):
#     __tablename__ = 'companies'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(String, unique=True)
