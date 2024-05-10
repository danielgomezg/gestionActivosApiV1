import shutil
from sqlalchemy.orm import Session, joinedload
from schemas.articleSchema import ArticleSchema, ArticleEditSchema
from models.article import Article
from fastapi import HTTPException, status, UploadFile
from sqlalchemy import func, and_, desc
from models.active import Active
import uuid
from urllib.parse import urlparse
from pathlib import Path
import hashlib
import random

#historial
from schemas.historySchema import HistorySchema
from crud.history import create_history

def get_article_all(db: Session, limit: int = 100, offset: int = 0):
    try:
        articles = (
            db.query(Article, func.count(Active.id).label("count_actives"))
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

        count = db.query(Article).filter(Article.removed == 0).count()

        return result, count
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener articulo {e}")

def get_articles_all_android(db: Session):
    return db.query(Article).filter(Article.removed == 0).all()

def get_article_by_id(db: Session, article_id: int):
    try:
        result = db.query(Article).filter(Article.id == article_id).options(joinedload(Article.category)).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar articulo {e}")

# reemplazada por get_article_by_code
def get_article_by_company_and_code(db: Session, company_id: int, code: str, limit: int = 100, offset: int = 0):
    try:
        result = db.query(Article).filter(Article.company_id == company_id, Article.code == code, Article.removed == 0).offset(offset).limit(limit).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener activos {e}")

def get_article_by_code(db: Session, code: str, limit: int = 100, offset: int = 0):
    try:
        result = db.query(Article).filter(Article.code == code, Article.removed == 0).offset(offset).limit(limit).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener activos {e}")

def count_article_by_company(db: Session, company_id: int):
    try:
        count = db.query(Article).filter(Article.company_id == company_id, Article.removed == 0).count()
        return count
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener Articulo {e}")

def get_article_by_id_company(db: Session, company_id: int, limit: int = 100, offset: int = 0, adjust_limit: bool = False):
    try:
        if adjust_limit:
            count_articles = count_article_by_company(db, company_id)
            if count_articles > limit:
                limit = count_articles

        articles = (
            db.query(Article)
            .outerjoin(Active, and_(Active.article_id == Article.id, Active.removed == 0))
            .filter(Article.company_id == company_id, Article.removed == 0)
            .options(joinedload(Article.category))
            .order_by(desc(Article.id))
            .offset(offset)
            .limit(limit)
            .all()
        )

        count = db.query(Article).filter(Article.company_id == company_id, Article.removed == 0).count()
        return articles, count
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener Articulo {e}")

def search_article_by_company(db: Session, search: str, company_id: int , limit: int = 100, offset: int = 0):
    try:
        query = db.query(Article, func.count(Active.id).label("count_actives")). \
            outerjoin(Active, and_(Active.article_id == Article.id, Active.removed == 0)). \
            filter(
            Article.company_id == company_id,
            Article.removed == 0,
            (
                    func.lower(Article.name).like(f"%{search}%") |
                    func.lower(Article.code).like(f"%{search}%")
            )
            ).group_by(Article.id).order_by(desc(Article.id)).offset(offset).limit(limit)

        Artilces = query.all()
        result = []
        for article in Artilces:
            article[0].count_actives = article[1]
            result.append(article[0])

        count = db.query(Article).filter(Article.company_id == company_id, Article.removed == 0, (
                func.lower(Article.name).like(f"%{search}%") |
                func.lower(Article.code).like(f"%{search}%")
            )).count()

        return result, count
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar sucursales {e}")

def generate_short_unique_id(data: str, length: int = 20) -> str:
    # Generar un número aleatorio
    random_number = random.randint(0, 1000000000)  # Un entero grande

    # Combinar el string de entrada con el número aleatorio
    data_with_random = data + str(random_number)

    hash_object = hashlib.sha256(data_with_random.encode())
    hex_dig = hash_object.hexdigest()
    return hex_dig[:length]


def get_image_url(file: UploadFile, upload_folder: Path) -> str:
    try:
        #unique_id = uuid.uuid4().hex
        unique_id = generate_short_unique_id(file.filename)
        # Concatena el UUID al nombre del archivo original
        filename_with_uuid = f"{unique_id}_{file.filename}"
        file_path = upload_folder / filename_with_uuid
        with open(file_path, "wb") as image_file:
            shutil.copyfileobj(file.file, image_file)

        # photo_url = f"http://127.0.0.1:9000/files/images_article/{filename_with_uuid}"
        return filename_with_uuid
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al guardar la imagen: {e}")


def create_article(db: Session, article: ArticleSchema, name_user: str):
    try:
        _article = Article(
            name=article.name,
            description=article.description,
            code=article.code,
            photo=article.photo,
            category_id=article.category_id,
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
            "name_user": name_user
            #"current_session_user_id": id_user
        }
        create_history(db, HistorySchema(**history_params))

        return _article
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Error creando articulo {e}")



def update_article(db: Session, article_id: int, article: ArticleEditSchema, name_user: str):
    try:
        article_to_edit = db.query(Article).filter(Article.id == article_id).first()
        if article_to_edit:
            article_to_edit.name = article.name
            article_to_edit.description = article.description
            article_to_edit.code = article.code
            article_to_edit.category_id = article.category_id

            # Se elimina la foto reemplazada del servidor
            # Si la foto es nula, no se hace nada
            if len(article_to_edit.photo) > 0 and article_to_edit.photo != article.photo:

                photos_old = article_to_edit.photo.split(",")
                photos_new = article.photo.split(",")
                print(photos_old)
                print(photos_new)

                # Convierte las listas en conjuntos
                photos_old_set = set(photos_old)
                photos_new_set = set(photos_new)

                photos_deletes = list(photos_old_set - photos_new_set)
                print(photos_deletes)

                for photo_to_delete in photos_deletes:
                    # Construir la ruta al archivo existente
                    existing_file_path = Path("files") / "images_article" / photo_to_delete

                    # Verificar si el archivo existe y eliminarlo
                    if existing_file_path.exists():
                        existing_file_path.unlink()

                    print(photo_to_delete)

                # # Construir la ruta al archivo existente
                # existing_file_path = Path("files") / "images_article" / article_to_edit.photo
                #
                # # Verificar si el archivo existe y eliminarlo
                # if existing_file_path.exists():
                #    existing_file_path.unlink()

            article_to_edit.photo = article.photo

            db.commit()

            # creacion del historial
            history_params = {
                "description": "update-article",
                "article_id": article_to_edit.id,
                "company_id": article_to_edit.company_id,
                "name_user": name_user
                #"current_session_user_id": id_user
            }
            create_history(db, HistorySchema(**history_params))

            return get_article_by_id(db, article_id)
            #return article_to_edit
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Articulo no encontrado")
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error editando articulo: {e}")

def delete_article(db: Session, article_id: int, name_user: str):
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
                "name_user": name_user
                #"current_session_user_id": id_user
            }
            create_history(db, HistorySchema(**history_params))

            return article_id
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Articulo con id {article_id} no encontrado")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error eliminando article: {e}")

