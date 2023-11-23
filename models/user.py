from sqlalchemy import Column, Integer, String
from database import Base
from sqlalchemy.ext.hybrid import hybrid_property
from passlib.hash import bcrypt

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