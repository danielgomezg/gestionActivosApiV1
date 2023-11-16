from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String
#from database import meta, engine
from database import Base

class Company(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)

#meta.create_all(engine)