from sqlalchemy import Column, Integer, String, ForeignKey, Date
from database import Base
from sqlalchemy.orm import relationship
from datetime import date

class Active(Base):
    __tablename__ = 'activo'
    id = Column(Integer, primary_key=True, autoincrement=True)
    bar_code = Column(String, nullable=False)
    comment= Column(String, nullable=True)
    acquisition_date = Column(Date, default=date.today, nullable=False)
    accounting_document = Column(String, nullable=False)
    accounting_record_number = Column(String, nullable=False)
    name_in_charge_active = Column(String, nullable=False)
    rut_in_charge_active = Column(String, nullable=False)
    serie = Column(String, nullable=False)
    model = Column(String, nullable=False)
    state = Column(String, nullable=False)
    creation_date = Column(Date, default=date.today, nullable=False)
    removed = Column(Integer, default=0, nullable=False)

    #user_id = Column(Integer, ForeignKey('usuario.id'))
    #user = relationship('Usuario', back_populates='actives')

    office_id = Column(Integer, ForeignKey('oficina.id'))
    office = relationship('Office', back_populates='actives')

    article_id = Column(Integer, ForeignKey('articulo.id'))
    article = relationship('Article', back_populates='actives')
