from sqlalchemy.orm import Session
from schemas.articleSchema import ArticleSchema, ArticleEditSchema
from models.article import Article
from fastapi import HTTPException, status
from sqlalchemy import func, and_, desc
from models.active import Active

def get_article_all(db: Session, limit: int = 100, offset: int = 0):
    try:
        articles = (
            db.query(Article, func.count(Active.id).label("count_active"))
            .outerjoin(Active, and_(Active.article_id == Article.id, Active.removed == 0))
            .filter(Article.removed == 0)
            .group_by(Article.id)
            .order_by(desc(Article.id))
            .offset(offset)
            .limit(limit)
            .all()
        )
        result = []
        for article in articles:
            article[0].count_actives = article[1]
            result.append(article[0])

        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener articulo {e}")

def get_article_by_id(db: Session, article_id: int):
    try:
        result = db.query(Article).filter(Article.id == article_id).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar articulo {e}")

def get_article_by_id_company(db: Session, company_id: int, limit: int = 100, offset: int = 0):
    try:
        articles = (
            db.query(Article, func.count(Active.id).label("count_actives"))
            .outerjoin(Active, and_(Active.article_id == Article.id, Active.removed == 0))
            .filter(Article.company_id == company_id, Article.removed == 0)
            .group_by(Article.id)
            .order_by(desc(Article.id))
            .offset(offset)
            .limit(limit)
            .all()
        )
        result = []
        for article in articles:
            article[0].count_actives = article[1]
            result.append(article[0])
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener Articulo {e}")

def create_article(db: Session, article: ArticleSchema):
    try:
        _article = Article(
            name=article.name,
            description=article.description,
            photo=article.photo,
            #creation_date=article.creation_date,
            company_id=article.company_id
        )

        db.add(_article)
        db.commit()
        db.refresh(_article)
        return _article
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Error creando articulo {e}")


def update_article(db: Session, article_id: int, article: ArticleEditSchema):
    try:
        article_to_edit = db.query(Article).filter(Article.id == article_id).first()
        if article_to_edit:
            article_to_edit.name = article.name
            article_to_edit.description = article.description
            article_to_edit.photo = article.photo
            #article_to_edit.creation_date = article.creation_date

            db.commit()
            article = get_article_by_id(db, article_id)
            return article
            #return {"message": "Acción actualizada correctamente", "action": action_to_edit}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Articulo no encontrado")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error editando articulo: {e}")

def delete_article(db: Session, article_id: int):
    try:
        article_to_delete = db.query(Article).filter(Article.id == article_id).first()
        if article_to_delete:
            article_to_delete.removed = 1
            #db.delete(article_to_delete)
            db.commit()
            return article_id
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Articulo con id {article_id} no encontrado")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error eliminando article: {e}")



# def delete_article(db: Session, article_id: int):
#     article_to_delete = db.query(Article).filter(Article.id == article_id).first()
#     try:
#         if article_to_delete:
#             db.delete(article_to_delete)
#             db.commit()
#             return article_id
#         else:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Articulo con id {article_id} no encontrado")
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error eliminando article: {e}")
