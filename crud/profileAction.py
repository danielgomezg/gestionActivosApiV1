from sqlalchemy.orm import Session
from schemas.profile_actionSchema import ProfileActionSchema
from models.profile_action import ProfileAction
from fastapi import HTTPException, status

def get_profile_action_all(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ProfileAction).offset(skip).limit(limit).all()

def get_profile_action_by_id(db: Session, profile_action_id: int):
    try:
        result = db.query(ProfileAction).filter(ProfileAction.id == profile_action_id).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar perfilAccion {e}")