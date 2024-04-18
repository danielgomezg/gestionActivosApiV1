from sqlalchemy import create_engine, MetaData, text, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
import psycopg2
from psycopg2 import sql

# credentials = "postgresql://postgres:postgres@localhost:5432/"
credentials = "postgresql://postgres:gactivos@gbd-c:5432/"

# engine = create_engine("postgresql://postgres:gactivos@gbd-c:5432/gestion_activos")
# engine = create_engine("postgresql://postgres:admin@localhost:5432/gestion_activos") #Dany
engine = create_engine(credentials + "gestion_activos")


SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_database(db_name):
    print("Creando base de datos")
    print(db_name)
    conn = psycopg2.connect(user='postgres', password='gactivos', host='gbd-c', port='5432')
    # conn = psycopg2.connect(user='postgres', password='postgres', host='localhost', port='5432')
    # conn = psycopg2.connect(user='postgres', password='admin', host='localhost', port='5432') #dany
    conn.autocommit = True

    cursor = conn.cursor()

    cursor.execute(sql.SQL("CREATE DATABASE {} TEMPLATE template0").format(sql.Identifier(db_name)))

    # conexion(db_name)
    engine = create_engine(credentials + db_name)
    # engine = create_engine("postgresql://postgres:admin@localhost:5432/" + db_name)

    Base.metadata.create_all(bind=engine)

    cursor.close()
    conn.close()

    # Conexión a la nueva base de datos
    conn_new = psycopg2.connect(user='postgres', password='gactivos', host='gbd-c', port='5432')
    # conn_new = psycopg2.connect(user='postgres', password='postgres', host='localhost', port='5432', dbname=db_name)
    # conn_new = psycopg2.connect(user='postgres', password='postgres', host='localhost', port='5432', dbname=db_name)
    conn_new.autocommit = True
    cursor_new = conn_new.cursor()

    cursor_new.execute("""
            CREATE OR REPLACE FUNCTION increment_count_activo()
            RETURNS TRIGGER AS $$
            BEGIN
                UPDATE articulo
                SET count_active = count_active + 1
                WHERE id = NEW.article_id;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)

    # Crear el trigger en la nueva base de datos
    cursor_new.execute("""
            CREATE TRIGGER after_insert_activo
            AFTER INSERT ON activo
            FOR EACH ROW
            EXECUTE FUNCTION increment_count_activo();
        """)

    # Crear la función del segundo trigger
    cursor_new.execute("""
        CREATE OR REPLACE FUNCTION update_count_active()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Verificar si el activo ha sido marcado como removido
            IF OLD.removed = 0 AND NEW.removed = 1 THEN
                UPDATE articulo
                SET count_active = count_active - 1
                WHERE id = NEW.article_id;
            ELSIF OLD.removed = 1 AND NEW.removed = 0 THEN
                -- Si un activo previamente removido se restaura, incrementa el contador
                UPDATE articulo
                SET count_active = count_active + 1
                WHERE id = NEW.article_id;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Crear el trigger del segundo trigger
    cursor_new.execute("""
        CREATE TRIGGER after_active_update
        AFTER UPDATE ON activo
        FOR EACH ROW
        EXECUTE FUNCTION update_count_active();
    """)

    cursor_new.close()
    conn_new.close()

def conexion(db: Session, companyId: int):
    print("entro a conexion")	

    query = text("SELECT name_db FROM compania WHERE id = :company_id")
    result = db.execute(query, {"company_id": companyId})
    db_name = result.scalar() # Obtiene el primer valor del primer resultado
    
    db.close()
    
    print("db_name: ", db_name)
    if (db_name is None):
        yield None
        return

    engine = create_engine(credentials + db_name)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

#meta = MetaData()

#connection = engine.connect()