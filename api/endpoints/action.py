from models import action
from models.action import Action
# from database import engine
from fastapi import APIRouter, HTTPException, Path, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud.action import create_action, get_action_by_id, get_action_all, update_action, delete_action
from schemas.actionSchema import ActionSchema
from schemas.schemaGenerico import Response

from crud.user import  get_user_disable_current
from typing import Optional, Tuple

router = APIRouter()
# action.Base.metadata.create_all(bind=engine)

@router.get('/actions')
def get_actions(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    name_user, expiration_time = current_user_info
    # print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result = get_action_all(db)
    return result

@router.get("/action/{id}", response_model=ActionSchema)
def get_action(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    name_user, expiration_time = current_user_info
    # print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result = get_action_by_id(db, id)
    #print("getcompany")
    if result is None:
        raise HTTPException(status_code=404, detail="Accion no encontrada")
    return result
@router.post('/action')
def create(request: ActionSchema, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    name_user, expiration_time = current_user_info
    # print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    if(len(request.name) == 0):
        return  Response(code = "400", message = "Nombre de accion no valido", result = [])

    _action = create_action(db, request)
    return Response(code = "201", message = "Accion creada", result = _action).model_dump()

@router.put('/action/{id}')
def update(request: ActionSchema, id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    name_user, expiration_time = current_user_info
    # print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    if(len(request.name) == 0):
        return  Response(code = "400", message = "Nombre de accion no valido", result = [])

    _action = update_action(db, id, request.name)
    return Response(code = "201", message = "Accion editada", result = _action).model_dump()

@router.delete('/action/{id}')
def delete(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    name_user, expiration_time = current_user_info
    # print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    _action = delete_action(db, id)
    return Response(code = "201", message = f"Accion con id {id} eliminada", result = _action).model_dump()