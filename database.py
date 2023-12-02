from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


engine = create_engine("postgresql://postgres:admin@localhost:5432/gestion_activos")

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

print("database")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#meta = MetaData()

#connection = engine.connect()