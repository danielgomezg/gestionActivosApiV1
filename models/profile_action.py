from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base
from sqlalchemy.orm import relationship, validates
from sqlalchemy.orm.exc import NoResultFound

from crud.profile import get_profile_by_id
from crud.action import get_action_by_id

class ProfileAction(Base):
    __tablename__ = 'perfil_accion'
    id = Column(Integer, primary_key=True, autoincrement=True)

    #Relacion con perfil
    profile_id = Column(Integer, ForeignKey('perfil.id'))
    profile = relationship('Profile', back_populates='profileActions')

    # Relacion con accion
    action_id = Column(Integer, ForeignKey('accion.id'))
    action = relationship('Action', back_populates='profileActions')

    # Relacion con perfil
    #perfiles = relationship('Profile', back_populates='profile_action')
    @validates('profile_id')
    def validate_profile_id(self, key, profile_id):
        try:
            # Intenta buscar una empresa con el ID proporcionado
            #print("acaaaaa")
            profile = get_profile_by_id(profile_id)
            #print(company)
            return profile_id
        except NoResultFound:
            # Si no se encuentra la empresa, levanta una excepción
            raise ValueError(f"No existe un perfil con el ID {profile_id}")

    @validates('action_id')
    def validate_action_id(self, key, action_id):
        try:
            # Intenta buscar una empresa con el ID proporcionado
            #print("acaaaaa")
            company = get_action_by_id(action_id)
            #print(company)
            return action_id
        except NoResultFound:
            # Si no se encuentra la empresa, levanta una excepción
            raise ValueError(f"No existe una accion con el ID {action_id}")