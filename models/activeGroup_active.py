from sqlalchemy import Column, Integer, ForeignKey
from database import Base
from sqlalchemy.orm import relationship

class Active_GroupActive(Base):
    __tablename__ = 'grupoActivo_activo'
    id = Column(Integer, primary_key=True, autoincrement=True)
    removed = Column(Integer, default=0, nullable=False)

    #Relacion con grupo de activo
    activeGroup_id = Column(Integer, ForeignKey('grupoActivo.id'))
    activeGroup = relationship('ActiveGroup', back_populates='activeGroup_active')

    # Relacion con activo
    active_id = Column(Integer, ForeignKey('activo.id'))
    active = relationship('Active', back_populates='activeGroup_active')