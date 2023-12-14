from models import profile_action
from models.profile_action import ProfileAction
from database import engine
from fastapi import APIRouter, HTTPException, Path, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud.profileAction import get_profile_action_by_id, get_profile_action_all, create_profile_action
from schemas.profile_actionSchema import Response, ProfileActionSchema

from crud.user import get_user_disable_current
from typing import Tuple

#importtaciones de perfil y accion para validacion
from crud.profile import get_profile_by_id
from crud.action import get_action_by_id


router = APIRouter()
profile_action.Base.metadata.create_all(bind=engine)

@router.get('/profileActions')
async def get_profile_sctions(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    #print("ID del usuario: ", id_user)
    #print("Tiempo de expiración: ", expiration_time)
    result = get_profile_action_all(db)
    return result

@router.get("/profileAction/{id}", response_model=ProfileActionSchema)
async def get_profile_action(id: int, db: Session = Depends(get_db), current_user: str = Depends(get_user_disable_current)):
    result = get_profile_action_by_id(db, id)
    #print("getcompany")
    if result is None:
        raise HTTPException(status_code=404, detail="Perfil Accion no encontrada")
    return result

@router.post('/profileAction')
async def create(request: ProfileActionSchema, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    # print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="Su sesión ha expirado", result=[])

    id_profile = get_profile_by_id(db, request.profile_id)
    if (not id_profile):
        return Response(code="400", message=f"id del perfil no valido", result=[])

    id_action = get_action_by_id(db, request.action_id)
    if (not id_action):
        return Response(code="400", message="id de la acción no valido", result=[])

    _profile_action = create_profile_action(db, request)
    return Response(code = "201", message = "PerfilAccion creada", result = _profile_action).dict(exclude_none=True)