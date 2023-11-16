from sqlalchemy import Column, Integer, String
from database import Base
#from database import meta, engine

class Usuario(Base):
    __tablename__ = 'usuario'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)

#meta.create_all(engine)