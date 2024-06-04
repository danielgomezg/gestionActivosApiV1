from sqlalchemy.orm import Session
from schemas.activeValuesSchema import ActiveValuesSchema
from models.activeValues import ActiveValues
from models.active import Active
from fastapi import HTTPException, status

def get_activeValues_all(db: Session, skip: int = 0, limit: int = 100):
    try:
        count = db.query(Active).filter(Active.removed == 0).count()

        # Obtener activos y ralizar left join con activeValues
        
        result = db.query(Active.id, Active.bar_code, Active.virtual_code, ActiveValues).outerjoin(ActiveValues, Active.id == ActiveValues.active_id).all()
        print(result)
        # Convertir los objetos Active y ActiveValues en diccionarios
        result_dict = [
            {
                "active": {
                    "id": id,
                    "bar_code": bar_code, 
                    "virtual_code": virtual_code
                },
                "active_values": active_values.__dict__ if active_values else None
            }
            for id, bar_code, virtual_code, active_values in result
        ]

        return result_dict, count
        
    except Exception as e:
        return [], 0
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener activeValues {e}")

def get_activeValues_by_id(db: Session, activeValues_id: int):
    try:
        result = db.query(ActiveValues).filter(ActiveValues.id == activeValues_id).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar activeValues {e}")

def create_activeValues(db: Session, activeValues: ActiveValuesSchema):
    try:
        _activeValues = ActiveValues(
            adq_value=activeValues.adq_value,
            real_value=activeValues.real_value,
            useful_life=activeValues.useful_life,
            active_id=activeValues.active_id
        )

        db.add(_activeValues)
        db.commit()
        db.refresh(_activeValues)
        return _activeValues
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Error creando activeValues {e}")

def update_activeValues(db: Session, activeValues_id: int, activeValues: ActiveValuesSchema):
    activeValues_to_edit = db.query(ActiveValues).filter(ActiveValues.id == activeValues_id).first()
    try:
        if activeValues_to_edit:
            activeValues_to_edit.adq_value = activeValues.adq_value,
            activeValues_to_edit.real_value = activeValues.real_value,
            activeValues_to_edit.useful_life = activeValues.useful_life

            db.commit()
            act_value = get_activeValues_by_id(db, activeValues_id)
            return act_value
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="activeValues no encontrada")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error editando activeValues: {e}")

def delete_activeValues(db: Session, activeValues_id: int):
    activeValues_to_delete = db.query(ActiveValues).filter(ActiveValues.id == activeValues_id).first()
    try:
        if activeValues_to_delete:
            db.delete(activeValues_to_delete)
            db.commit()
            return activeValues_id
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"activeValues con id {activeValues_id} no encontrada")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error eliminando activeValues: {e}")