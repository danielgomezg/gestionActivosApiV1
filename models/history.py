from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base
from sqlalchemy.orm import relationship

class History(Base):
    __tablename__ = 'historial'
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String, nullable=True)
    #removed = Column(Integer, default=0, nullable=False)

    #Relacion con empresa
    company_id = Column(Integer, ForeignKey('compania.id'), nullable=True)
    company = relationship('Company', back_populates='historial')

    # Relacion con sucursal
    sucursal_id = Column(Integer, ForeignKey('sucursal.id'), nullable=True)
    sucursal = relationship('Sucursal', back_populates='historial')

    # Relacion con oficina
    office_id = Column(Integer, ForeignKey('oficina.id'), nullable=True)
    office = relationship('Office', back_populates='historial')

    # Relacion con article
    article_id = Column(Integer, ForeignKey('articulo.id'), nullable=True)
    article = relationship('Article', back_populates='historial')

    # Relacion con active
    active_id = Column(Integer, ForeignKey('activo.id'), nullable=True)
    active = relationship('Active', back_populates='historial')

    # Relacion con user
    user_id = Column(Integer, ForeignKey('usuario.id'), nullable=True)
    user = relationship('Usuario', back_populates='historial')




    #def __repr__(self):
       # return f"Usuario(nombre={self.email}, correo={self.firstName})"