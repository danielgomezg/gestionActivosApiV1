import shutil
from sqlalchemy.orm import Session
from schemas.articleSchema import ArticleSchema, ArticleEditSchema
from models.article import Article
from fastapi import HTTPException, status, UploadFile
from sqlalchemy import func, and_, desc
from models.active import Active
import uuid
from urllib.parse import urlparse
from pathlib import Path

#historial
from schemas.historySchema import HistorySchema
from crud.history import create_history

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

def get_image_url(file: UploadFile, upload_folder: Path) -> str:
    try:
        unique_id = uuid.uuid4().hex
        # Concatena el UUID al nombre del archivo original
        filename_with_uuid = f"{unique_id}_{file.filename}"
        file_path = upload_folder / filename_with_uuid
        with open(file_path, "wb") as image_file:
            shutil.copyfileobj(file.file, image_file)

        # photo_url = f"http://127.0.0.1:9000/files/images_article/{filename_with_uuid}"
        return filename_with_uuid
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al guardar la imagen: {e}")


def create_article(db: Session, article: ArticleSchema, id_user: int):
    try:
        _article = Article(
            name=article.name,
            description=article.description,
            photo=article.photo,
            company_id=article.company_id
        )

        db.add(_article)
        db.commit()
        db.refresh(_article)

        # creacion del historial
        history_params = {
            "description": "create-article",
            "article_id": _article.id,
            "company_id": _article.company_id,
            "current_session_user_id": id_user
        }
        create_history(db, HistorySchema(**history_params))

        return _article
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Error creando articulo {e}")



def update_article(db: Session, article_id: int, article: ArticleEditSchema, id_user: int):
    try:
        article_to_edit = db.query(Article).filter(Article.id == article_id).first()
        if article_to_edit:
            article_to_edit.name = article.name
            article_to_edit.description = article.description

            # Se elimina la foto reemplazada del servidor
            # Si la foto es nula, no se hace nada
            if len(article_to_edit.photo) > 0:
                # Extraer el nombre del archivo de la URL
                # parsed_url = urlparse(article_to_edit.photo)
                # filename = Path(parsed_url.path).name
                # Construir la ruta al archivo existente
                existing_file_path = Path("files") / "images_article" / article_to_edit.photo

                # Verificar si el archivo existe y eliminarlo
                if existing_file_path.exists():
                   existing_file_path.unlink()

            article_to_edit.photo = article.photo

            db.commit()

            # creacion del historial
            history_params = {
                "description": "update-article",
                "article_id": article_to_edit.id,
                "company_id": article_to_edit.company_id,
                "current_session_user_id": id_user
            }
            create_history(db, HistorySchema(**history_params))

            return article_to_edit
            #return {"message": "Acción actualizada correctamente", "action": action_to_edit}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Articulo no encontrado")
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error editando articulo: {e}")

def delete_article(db: Session, article_id: int, id_user: int):
    try:
        article_to_delete = db.query(Article).filter(Article.id == article_id).first()
        if article_to_delete:
            article_to_delete.removed = 1
            #db.delete(article_to_delete)
            db.commit()

            # creacion del historial
            history_params = {
                "description": "delete-article",
                "article_id": article_to_delete.id,
                "company_id": article_to_delete.company_id,
                "current_session_user_id": id_user
            }
            create_history(db, HistorySchema(**history_params))

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
