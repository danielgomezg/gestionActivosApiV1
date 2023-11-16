from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String
from database import meta, engine

company = Table("companies", meta,
                  Column("id", Integer, primary_key=True),
                  Column("name", String(255)))

meta.create_all(engine)