from models import category
from models.category import Category
# from database import engine
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from database import get_db, conexion
from crud.category import (get_category_all, count_category, get_category_by_parent_id, create_category, update_category, delete_category, count_category_children,
                           get_category_by_description, get_category_without_son, get_category_by_code)
from schemas.categorySchema import CategorySchema, CategoryEditSchema
from schemas.schemaGenerico import ResponseGet, Response

from crud.user import get_user_disable_current
from typing import Tuple

router = APIRouter()
#category.Base.metadata.create_all(bind=engine)


@router.get('/categories')
def get_categories(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0, companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return  Response(code = "401", message = "token-exp", result = [])

    count = count_category(db)
    if(count == 0):
        return ResponseGet(code="404", result=[], limit=limit, offset=offset, count=count).model_dump()
    result = get_category_all(db, limit, offset)
    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = count).model_dump()

@router.get("/category/{parent_id}")
def get_category(parent_id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0, companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    count, result = get_category_by_parent_id(db, parent_id, limit, offset)
    if result is None:
        return Response(code= "404", result = [], message="Not found").model_dump()
    
    return ResponseGet(code= "200", result = result, limit=limit, offset = offset, count = count).model_dump()


@router.get("/categories/finals")
def get_category_finals(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25,
                 offset: int = 0, companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    count, result = get_category_without_son(db, limit, offset)
    if result is None:
        return Response(code="404", result=[], message="Not found").model_dump()

    return ResponseGet(code="200", result=result, limit=limit, offset=offset, count=count).model_dump()

@router.post('/category')
def create(request: CategorySchema, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    if (len(request.description) == 0):
        return Response(code="400", message="Descripcion de la categoria esta vacío", result=[])

    cat_dup = get_category_by_code(db, request.code)
    if cat_dup:
        return Response(code="400", message="Codigo ya existe", result=[])

    if (request.parent_id is None):
        return Response(code="400", message="La categoria no tiene padre", result=[])

    if (len(request.code) == 0):
        return Response(code="400", message="Codigo de la categoria esta vacío", result=[])

    # category_parent = get_category_by_id(db, int(request.parent_id))
    # if(category_parent is None):
    #     return Response(code="400", message="Id del padre de la categoria no existe", result=[])

    _category = create_category(db, request)
    return Response(code = "201", message = f"Categoria {_category.description} creada", result = _category).model_dump()

@router.put('/category/{id}')
def update(request: CategoryEditSchema, id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    if (len(request.description) == 0):
        return Response(code="400", message="Descripcion de la categoria esta vacío", result=[])
    
    if (len(request.code) == 0):
        return Response(code="400", message="Codigo de la categoria esta vacío", result=[])
    
    cat_dup = get_category_by_code(db, request.code)
    if cat_dup and cat_dup.id != id:
        return Response(code="400", message="Codigo ya existe", result=[])
    
    # cat_description = get_category_by_description(db, request.description)
    # if cat_description:
    #     return Response(code="400", message="Descripcion de categoria ya ingresado", result=[])

    _category = update_category(db, id, request)
    return Response(code = "201", message = f"La Categoria {_category.description} editada", result = _category).model_dump()

@router.delete('/category/{id}')
def delete(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    count_childs = count_category_children(db, id)

    if(count_childs > 0):
        return Response(code = "400", message = f"La Categoria con id {id} tiene hijos", result = []).model_dump()

    _category = delete_category(db, id)


    return Response(code = "201", message = f"Cateogria con id {id} eliminada", result = _category).model_dump()