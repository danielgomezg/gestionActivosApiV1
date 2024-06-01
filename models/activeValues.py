from sqlalchemy import Column, Integer, String, ForeignKey, Date
from database import Base
from sqlalchemy.orm import relationship

class ActiveValues(Base):
    __tablename__ = 'valores_activo'
    id = Column(Integer, primary_key=True, autoincrement=True)
    adq_value = Column(Integer, default=0, nullable=False)
    real_value = Column(Integer, default=0, nullable=False)
    useful_life = Column(Integer, default=0, nullable=False)
    removed = Column(Integer, default=0, nullable=False)

    # Relacion con activo
    active_id = Column(Integer, ForeignKey('activo.id'))
    active = relationship('Active', back_populates='activeValues')