from models import action
from models.action import Action
from database import engine
from fastapi import APIRouter, HTTPException, Path, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud.action import create_action, get_action_by_id, get_action_all, update_action, delete_action
from schemas.actionSchema import Response, ActionSchema

from crud.user import  get_user_disable_current
from typing import Optional, Tuple

router = APIRouter()
action.Base.metadata.create_all(bind=engine)

@router.get('/actions')
async def get_sctions(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    print("ID del usuario: ", id_user)
    print("Tiempo de expiración: ", expiration_time)
    result = get_action_all(db)
    return result

@router.get("/action/{id}", response_model=ActionSchema)
async def get_action(id: int, db: Session = Depends(get_db), current_user: str = Depends(get_user_disable_current)):
    result = get_action_by_id(db, id)
    #print("getcompany")
    if result is None:
        raise HTTPException(status_code=404, detail="Accion no encontrada")
    return result
@router.post('/action')
async def create(request: ActionSchema, db: Session = Depends(get_db)):

    if(len(request.name) == 0):
        return  Response(code = "400", message = "Nombre de accion no valido", result = [])

    _action = create_action(db, request)
    return Response(code = "201", message = "Accion creada", result = _action).dict(exclude_none=True)

@router.put('/action/{id}')
async def update(request: ActionSchema, id: int, db: Session = Depends(get_db), current_user: str = Depends(get_user_disable_current)):

    if(len(request.name) == 0):
        return  Response(code = "400", message = "Nombre de accion no valido", result = [])

    _action = update_action(db, id, request.name)
    return Response(code = "201", message = "Accion editada", result = _action).dict(exclude_none=True)

@router.delete('/action/{id}')
async def delete(id: int, db: Session = Depends(get_db), current_user: str = Depends(get_user_disable_current)):

    _action = delete_action(db, id)
    return Response(code = "201", message = f"Accion con id {id} eliminada", result = _action).dict(exclude_none=True)