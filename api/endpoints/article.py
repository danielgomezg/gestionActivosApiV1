from models import article
from models.article import Article
from database import engine
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pathlib import Path
from sqlalchemy.orm import Session
from database import get_db
from crud.article import get_article_all, get_article_by_id, create_article, update_article, delete_article, get_article_by_id_company, get_image_url
from schemas.articleSchema import ArticleSchema, ArticleEditSchema
from schemas.schemaGenerico import Response, ResponseGet
from crud.company import get_company_by_id
from fastapi.responses import FileResponse
from crud.user import  get_user_disable_current
from typing import Tuple

router = APIRouter()
#article.Base.metadata.create_all(bind=engine)

@router.get("/article/{id}", response_model=ArticleSchema)
def get_article(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    # print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result = get_article_by_id(db, id)
    if result is None:
        raise HTTPException(status_code=404, detail="Articulo no encontrado")
    return result

@router.get('/articles')
def get_articles(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0):
    id_user, expiration_time = current_user_info
    # print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result = get_article_all(db, limit, offset)
    return result

@router.get('/articlesPorCompany/{id_company}')
def get_articles_por_company(id_company: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0):
    id_user, expiration_time = current_user_info
    # print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result = get_article_by_id_company(db, id_company, limit, offset)
    if not result:
        return ResponseGet(code= "404", result = [], limit= limit, offset = offset, count = 0).model_dump()
    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = len(result)).model_dump()
    #return result


@router.post("/image_article")
def upload_image(file: UploadFile = File(...), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    try:
        id_user, expiration_time = current_user_info
        # print("Tiempo de expiración: ", expiration_time)
        # Se valida la expiracion del token
        if expiration_time is None:
            return Response(code="401", message="token-exp", result=[])

        upload_folder = Path("files") / "images_article"
        upload_folder.mkdir(parents=True, exist_ok=True)  # Crea el directorio si no existe
        photo_url = get_image_url(file, upload_folder)
        return Response(code="201", message="Foto guardada con éxito", result=photo_url).model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la imagen: {e}")

@router.post('/article')
def create(request: ArticleSchema, db: Session = Depends(get_db), current_user_info: Tuple[int, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    #print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    if(len(request.name) == 0):
        return  Response(code = "400", message = "Nombre no valido", result = [])

    #if(len(request.photo) == 0):
        #return  Response(code = "400", message = "Foto no valida", result = [])

    id_company = get_company_by_id(db, request.company_id)
    if(not id_company):
        return Response(code="400", message="id compania no valido", result=[])

    _article = create_article(db, request, id_user)
    return Response(code = "201", message = f"Articulo {_article.name} creado", result = _article).model_dump()

@router.put('/article/{id}')
def update(request: ArticleEditSchema, id: int, db: Session = Depends(get_db), current_user_info: Tuple[int, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    #print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    if(len(request.name) == 0):
        return  Response(code = "400", message = "Nombre no valido", result = [])

    #if(len(request.photo) == 0):
        #return  Response(code = "400", message = "Foto no valida", result = [])

    _article = update_article(db, id,  request, id_user)
    return Response(code = "201", message = f"Articulo {_article.name} editado", result = _article).model_dump()

@router.delete('/article/{id}')
def delete(id: int, db: Session = Depends(get_db), current_user_info: Tuple[int, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    # print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    _article = delete_article(db, id, id_user)
    return Response(code = "201", message = f"Articulo con id {id} eliminado", result = _article).model_dump()


@router.get("/image_article/{image_path}")
async def get_image(image_path: str):
    image = Path("files") / "images_article" / image_path
    if not image.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image)