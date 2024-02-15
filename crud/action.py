from sqlalchemy.orm import Session
from schemas.actionSchema import ActionSchema
from models.action import Action
from fastapi import HTTPException, status

def get_action_all(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(Action).offset(skip).limit(limit).all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener acciones {e}")

def get_action_by_id(db: Session, action_id: int):
    try:
        result = db.query(Action).filter(Action.id == action_id).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar accion {e}")

def get_action_by_name(db: Session, action_name: str):
    try:
        result = db.query(Action).filter(Action.name == action_name).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar accion por name {e}")


def create_action(db: Session, action: ActionSchema):
    try:
        _action = Action(
            name=action.name
        )

        db.add(_action)
        db.commit()
        db.refresh(_action)
        return _action
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Error creando accion {e}")


def update_action(db: Session, action_id: int, name_edited: str):
    action_to_edit = db.query(Action).filter(Action.id == action_id).first()
    try:
        if action_to_edit:
            action_to_edit.name = name_edited

            db.commit()
            action = get_action_by_id(db, action_id)
            return action
            #return {"message": "Acción actualizada correctamente", "action": action_to_edit}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Acción no encontrada")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error editando acción: {e}")

def delete_action(db: Session, action_id: int):
    action_to_delete = db.query(Action).filter(Action.id == action_id).first()
    try:
        if action_to_delete:
            db.delete(action_to_delete)
            db.commit()
            return action_id
            #return {"message": "Acción actualizada correctamente", "action": action_to_edit}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Acción con id {action_id} no encontrada")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error eliminando acción: {e}")
