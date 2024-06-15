from sqlalchemy.orm import Session
from schemas.activeGroup_active import ActiveGroup_ActiveSchema
from models.activeGroup_active import Active_GroupActive
from models.active import Active
from schemas.activeGroupSchema import ActiveGroupSchema
from fastapi import HTTPException, status
from sqlalchemy import and_

def get_activeGroup_active_all(db: Session, skip: int = 0, limit: int = 100):
    try:
        count = db.query(Active_GroupActive).count()
        result = db.query(Active_GroupActive).offset(skip).limit(limit).all()
        return result, count
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener activos_gruposActivos {e}")

def get_activeGroup_active_by_id(db: Session, activeGroup_active_id: int):
    try:
        result = db.query(Active_GroupActive).filter(Active_GroupActive.id == activeGroup_active_id).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar activeGroup_active {e}")

def get_activeGroup_active_by_id_activeGroup_activen(db: Session, activeGroup_id: int, active_id: int):
    try:
        result = db.query(Active_GroupActive).filter(and_(Active_GroupActive.activeGroup_id == activeGroup_id, Active_GroupActive.active == active_id)).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar activeGroup_active {e}")

def create_activeGroup_active(db: Session, activeGroup_active: ActiveGroup_ActiveSchema):
    try:
        _activeGroup_active = ActiveGroup_ActiveSchema(
            activeGroup_id=activeGroup_active.activeGroup_id,
            active_id=activeGroup_active.active_id
        )

        db.add(_activeGroup_active)
        db.commit()
        db.refresh(_activeGroup_active)
        return _activeGroup_active
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Error creando perfilAccion {e}")
    
def create_collection_actives(db: Session, body: ActiveGroupSchema, collId: int):
    try:
        mapping = [
            {
                "activeGroup_id": collId,
                "active_id": active_id
            }
            for active_id in body.activesId
        ]
        db.bulk_insert_mappings(Active_GroupActive, mapping)
        db.commit()

        return mapping

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Error creando perfilAccion {e}")

def get_actives_by_idCollection(db: Session, collId: int):
    try:
        result = db.query(Active_GroupActive, Active.id, Active.bar_code, Active.virtual_code).outerjoin(Active, Active.id == Active_GroupActive.active_id).filter(Active_GroupActive.activeGroup_id == collId).all()

        result_dict = [
            {   
                "id": id,
                "bar_code": bar_code, 
                "virtual_code": virtual_code 
            }
            for _, id, bar_code, virtual_code in result
        ]

        return result_dict
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar actives por id de coleccion {e}")
    
def update_collection_actives(db: Session, collId: int, activesId: list):
    try:
        # Eliminar todos los actives de la coleccion
        db.query(Active_GroupActive).filter(Active_GroupActive.activeGroup_id == collId).delete()

        # Insertar los nuevos actives
        mapping = [
            {
                "activeGroup_id": collId,
                "active_id": active_id
            }
            for active_id in activesId
        ]
        db.bulk_insert_mappings(Active_GroupActive, mapping)
        db.commit()

        return mapping
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al actualizar actives de coleccion {e}")