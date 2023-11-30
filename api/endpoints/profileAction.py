from models import profile_action
from models.profile_action import ProfileAction
from database import engine
from fastapi import APIRouter, HTTPException, Path, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud.profileAction import get_profile_action_by_id, get_profile_action_all
from schemas.profile_actionSchema import Response, ProfileActionSchema

from crud.user import get_user_disable_current
from typing import Optional, Tuple

router = APIRouter()
profile_action.Base.metadata.create_all(bind=engine)

@router.get('/profileactions')
async def get_profile_sctions(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    #print("ID del usuario: ", id_user)
    #print("Tiempo de expiración: ", expiration_time)
    result = get_profile_action_all(db)
    return result

@router.get("/profileaction/{id}", response_model=ProfileActionSchema)
async def get_profile_action(id: int, db: Session = Depends(get_db), current_user: str = Depends(get_user_disable_current)):
    result = get_profile_action_by_id(db, id)
    #print("getcompany")
    if result is None:
        raise HTTPException(status_code=404, detail="Perfil Accion no encontrada")
    return result