from sqlalchemy import Column, Integer, String, ForeignKey, Date
from database import Base
from sqlalchemy.orm import relationship
from datetime import date
import pandas as pd
from schemas.articleSchema import ArticleSchema

class Article(Base):
    __tablename__ = 'articulo'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description= Column(String, nullable=True)
    code = Column(String, nullable=False)
    photo = Column(String, nullable=True)
    count_active = Column(Integer, default=0, nullable=False)
    creation_date = Column(Date, default=date.today, nullable=False)
    removed = Column(Integer, default=0, nullable=False)

    company_id = Column(Integer, ForeignKey('compania.id'))
    company = relationship('Company', back_populates='articles')

    category_id = Column(Integer, ForeignKey('categoria.id'))
    category = relationship('Category', back_populates='articles')

    actives = relationship('Active', back_populates='article')

    # Relacion con historial
    historial = relationship('History', back_populates='article')


def validateArticleFromFile(article, companyID):
    try:
        # Aquí puedes acceder a los datos de cada fila
        name = '' if pd.isna(article.iloc[9]) else article.iloc[9]  # OBLIGATORIO
        code = '' if pd.isna(article.iloc[10]) else article.iloc[10]  # OBLIGATORIO
        description = '' if pd.isna(article.iloc[11]) else article.iloc[11]  # OBLIGATORIO
        code = convert_string(code)
        print("model article")
        print(name)
        print(code)
        print(description)

        new_article = {
            "name": str(name),
            "description": str(description),
            "code": code,
            "photo": "",
            "company_id": companyID
        }

        if new_article["name"] == '' or new_article["description"] == '' or new_article["code"] == '':
            return None, "Faltan campos obligatorios"

        print(f"Article : {new_article}")
        new_article = ArticleSchema(**new_article)
        return new_article, "ok"

    except Exception as e:
        print(f"Error : {e}")
        print(f"Tipo de error : {type(e)}")
        print("Argumentos del error : ", e.args)
        return None, e


def convert_string(code):
    if isinstance(code, float):
        # Si el dato es un flotante, lo convierte primero a entero y luego a string
        code = int(code)
    return str(code)