from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from database import get_db, conexion
from crud.activeGroup import create_activeGroup, get_activeGroup_by_id, get_activeGroup_all, update_activeGroup, delete_activeGroup
from schemas.activeGroupSchema import ActiveGroupSchema
from schemas.schemaGenerico import Response
from crud.user import  get_user_disable_current
from typing import Tuple

router = APIRouter()
# action.Base.metadata.create_all(bind=engine)

@router.get('/activesGroups')
def get_activesGroups(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result = get_activeGroup_all(db)
    return result

@router.get("/activesGroup/{id}", response_model=ActiveGroupSchema)
def get_activesGroup(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result = get_activeGroup_by_id(db, id)
    if result is None:
        raise HTTPException(status_code=404, detail="activesGroup no encontrada")
    return result
@router.post('/activesGroup')
def create(request: ActiveGroupSchema, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    if(len(request.name) == 0):
        return  Response(code = "400", message = "Nombre de activesGroup no valido", result = [])

    _activesGroup = create_activeGroup(db, request)
    return Response(code = "201", message = "ActivesGroup creada", result = _activesGroup).model_dump()

@router.put('/activesGroup/{id}')
def update(request: ActiveGroupSchema, id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    if(len(request.name) == 0):
        return  Response(code = "400", message = "Nombre de activesGroup no valido", result = [])

    _activesGroup = update_activeGroup(db, id, request.name)
    return Response(code = "201", message = "ActivesGroup editada", result = _activesGroup).model_dump()

@router.delete('/activesGroup/{id}')
def delete(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    _activesGroup = delete_activeGroup(db, id)
    return Response(code = "201", message = f"ActivesGroup con id {id} eliminada", result = _activesGroup).model_dump()