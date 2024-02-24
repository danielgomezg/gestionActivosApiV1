from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
import psycopg2
from psycopg2 import sql
from models import user as user_model


# engine = create_engine("postgresql://postgres:gactivos@gbd-c:5432/gestion_activos")
engine = create_engine("postgresql://postgres:admin@localhost:5432/gestion_activos") #Dany
#engine = create_engine("postgresql://postgres:postgres@localhost:5432/gestion_activos")

#engine: AsyncEngine = create_async_engine("postgresql://postgres:admin@localhost:5432/gestion_activos", echo=True)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
# Configuración de la sesión asíncrona
#async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autocommit=False)
Base = declarative_base()


def get_db():
    # engine = create_engine("postgresql://postgres:postgres@localhost:5432/")
    # db = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  
    

def create_database(db_name):
    print("Creando base de datos")
    print(db_name)
    #conn = psycopg2.connect(user='postgres', password='postgres', host='localhost', port='5432')
    conn = psycopg2.connect(user='postgres', password='admin', host='localhost', port='5432') #dany
    conn.autocommit = True

    cursor = conn.cursor()

    cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))

    # conexion(db_name)
    #engine = create_engine("postgresql://postgres:postgres@localhost:5432/" + db_name)
    engine = create_engine("postgresql://postgres:admin@localhost:5432/" + db_name)  # Dany
    # db = sessionmaker(bind=engine, autocommit=False, autoflush=False)   

    Base.metadata.create_all(bind=engine)

    cursor.close()
    conn.close()

def conexion(db_name):
    #engine = create_engine("postgresql://postgres:postgres@localhost:5432/" + db_name)
    engine = create_engine("postgresql://postgres:admin@localhost:5432/" + db_name)  # Dany
    #db = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        print(db_name)
        yield db
    finall
        db.close()

#meta = MetaData()

#connection = engine.connect()