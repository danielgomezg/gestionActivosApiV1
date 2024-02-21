from models import category
from models.category import Category
from database import engine
from fastapi import APIRouter, HTTPException, Path, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud.category import get_category_all, count_category, get_category_by_id, create_category, update_category, delete_category
from schemas.categorySchema import CategorySchema, CategoryEditSchema
from schemas.schemaGenerico import ResponseGet, Response
import re

from crud.user import get_user_disable_current
from typing import Optional, Tuple

router = APIRouter()
#category.Base.metadata.create_all(bind=engine)


@router.get('/categories')
def get_categories(db: Session = Depends(get_db), current_user_info: Tuple[int, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0):
    id_user, expiration_time = current_user_info
    # Se valida la expiracion del token
    if expiration_time is None:
        return  Response(code = "401", message = "token-exp", result = [])

    count = count_category(db)
    if(count == 0):
        return ResponseGet(code="404", result=[], limit=limit, offset=offset, count=count).model_dump()
    result = get_category_all(db, limit, offset)
    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = count).model_dump()

@router.get("/category/{id}")
def get_category(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result = get_category_by_id(db, id)
    if result is None:
        return Response(code= "404", result = [], message="Not found").model_dump()
    return Response(code= "200", result = result, message="Categoryy found").model_dump()

@router.post('/category')
def create(request: CategorySchema, db: Session = Depends(get_db), current_user_info: Tuple[int, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    if(request.level is None):
        return  Response(code = "400", message = "El nivel de la categoria esta vacío", result = [])

    if (len(request.description) == 0):
        return Response(code="400", message="Descripcion de la categoria esta vacío", result=[])

    if (request.father_id is None):
        return Response(code="400", message="La categoria no tiene padre", result=[])

    category_father = get_category_by_id(db, int(request.father_id))
    if(category_father is None):
        return Response(code="400", message="Id del padre de la categoria no existe", result=[])

    #if (len(request.client_code) == 0):
     #   return Response(code="400", message="Descripcion de la categoria esta vacío", result=[])

    _category = create_category(db, request)
    return Response(code = "201", message = f"Categoria {_category.description} creada", result = _category).model_dump()

@router.put('/category/{id}')
def update(request: CategoryEditSchema, id: int, db: Session = Depends(get_db), current_user_info: Tuple[int, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    if (len(request.description) == 0):
        return Response(code="400", message="Descripcion de la categoria esta vacío", result=[])

    _category = update_category(db, id, request)
    return Response(code = "201", message = f"La Categoria {_category.description} editada", result = _category).model_dump()

@router.delete('/category/{id}')
def delete(id: int, db: Session = Depends(get_db), current_user_info: Tuple[int, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    _category = delete_category(db, id)
    return Response(code = "201", message = f"Cateogria con id {id} eliminada", result = _category).model_dump()