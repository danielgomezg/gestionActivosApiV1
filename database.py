from sqlalchemy import create_engine, MetaData

engine = create_engine("postgresql://postgres:admin@localhost:5432/gestion_activos")

meta = MetaData()

connection = engine.connect()