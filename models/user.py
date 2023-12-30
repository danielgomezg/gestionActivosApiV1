from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base
from sqlalchemy.ext.hybrid import hybrid_property
from passlib.hash import bcrypt
from sqlalchemy.orm import relationship

from models import company
from models import profile
from database import engine


company.Base.metadata.create_all(bind=engine)
profile.Base.metadata.create_all(bind=engine)

class Usuario(Base):
    __tablename__ = 'usuario'
    id = Column(Integer, primary_key=True, autoincrement=True)
    firstName = Column(String, nullable=False)
    secondName = Column(String, nullable=True)
    lastName = Column(String, nullable=False)
    secondLastName = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=False)
    _password = Column(String, nullable=False)
    rut = Column(String, unique=True, nullable=False)
    removed = Column(Integer, default=0, nullable=False)

    #Relacion con empresa
    company_id = Column(Integer, ForeignKey('compania.id'), nullable=True)
    # Relacion con perfil
    profile_id = Column(Integer, ForeignKey('perfil.id'))


    company = relationship('Company', back_populates='users')

    profile = relationship('Profile', back_populates='users')

    #actives = relationship('Active', back_populates='user')


    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, plainTextPassword):
        self._password = bcrypt.hash(plainTextPassword)

    @classmethod
    def verify_password(self, password, passwordHash):
        print(password)
        return bcrypt.verify(password, passwordHash)

    def __repr__(self):
        return f"Usuario(nombre={self.email}, correo={self.firstName})"