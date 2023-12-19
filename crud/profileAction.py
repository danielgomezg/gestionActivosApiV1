from sqlalchemy.orm import Session
from schemas.profile_actionSchema import ProfileActionSchema
from models.profile_action import ProfileAction
from fastapi import HTTPException, status
from sqlalchemy import and_

def get_profile_action_all(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(ProfileAction).offset(skip).limit(limit).all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener prefilesAccion {e}")

def get_profile_action_by_id(db: Session, profile_action_id: int):
    try:
        result = db.query(ProfileAction).filter(ProfileAction.id == profile_action_id).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar perfilAccion {e}")

def get_profile_action_by_id_profile_action(db: Session, profile_id: int, action_id: int):
    try:
        result = db.query(ProfileAction).filter(and_(ProfileAction.profile_id == profile_id, ProfileAction.action_id == action_id)).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar perfilAccion {e}")

def create_profile_action(db: Session, profile_action: ProfileActionSchema):
    try:
        _profile_action = ProfileAction(
            profile_id=profile_action.profile_id,
            action_id=profile_action.action_id
        )

        db.add(_profile_action)
        db.commit()
        db.refresh(_profile_action)
        return _profile_action
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Error creando perfilAccion {e}")