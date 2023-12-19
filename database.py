from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine

engine = create_engine("postgresql://postgres:admin@localhost:5432/gestion_activos")
#engine: AsyncEngine = create_async_engine("postgresql://postgres:admin@localhost:5432/gestion_activos", echo=True)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
# Configuración de la sesión asíncrona
#async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    #db = async_session()
    try:
        yield db
    finally:
        db.close()


#meta = MetaData()

#connection = engine.connect()