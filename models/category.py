from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class Category(Base):
    __tablename__ = 'categoria'
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String, nullable=False)
    description = Column(String, nullable=False)
    father_id = Column(Integer, nullable=False)
    client_code = Column(String, nullable=True)
    removed = Column(Integer, default=0, nullable=False)

    #Relacion con sucursales
    #sucursales = relationship('Sucursal', back_populates='company')
    #sucursales_count_var = None

    #Relacion con usuario
    #users = relationship('Usuario', back_populates='company')

    #Relacion con article
    articles = relationship('Article', back_populates='category')

    # Relacion con historial
    #historial = relationship('History', back_populates='category')