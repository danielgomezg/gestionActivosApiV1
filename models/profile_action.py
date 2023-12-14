from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base
from sqlalchemy.orm import relationship, validates
from sqlalchemy.orm.exc import NoResultFound

# from crud.profile import get_profile_by_id
# from crud.action import get_action_by_id

class ProfileAction(Base):
    __tablename__ = 'perfil_accion'
    id = Column(Integer, primary_key=True, autoincrement=True)

    #Relacion con perfil
    profile_id = Column(Integer, ForeignKey('perfil.id'))
    profile = relationship('Profile', back_populates='profileActions')

    # Relacion con accion
    action_id = Column(Integer, ForeignKey('accion.id'))
    action = relationship('Action', back_populates='profileActions')
