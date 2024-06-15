from sqlalchemy.orm import Session
from sqlalchemy import func
from schemas.activeGroupSchema import ActiveGroupSchema
from models.activeGroup import ActiveGroup
from models.activeGroup_active import Active_GroupActive
from fastapi import HTTPException, status

def get_activeGroup_all(db: Session, skip: int = 0, limit: int = 100):
    try:
        count = db.query(ActiveGroup).count()
        if count == 0:
            return [], 0
        
        # 
        # result = db.query(ActiveGroup).offset(skip).limit(limit).all()
        result = (
            db.query(ActiveGroup, func.count(Active_GroupActive.active_id).label('count'))
            .join(Active_GroupActive, ActiveGroup.id == Active_GroupActive.activeGroup_id)
            .group_by(ActiveGroup.id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        # result = [row._asdict() for row in result]
        result = [
            {
                "id": row.ActiveGroup.id,
                "name": row.ActiveGroup.name,
                "actives_count": row.count,
                "creation_date": row.ActiveGroup.creation_date,
            }
            for row in result
        ]

        return result, count
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener activeGroup {e}")

def get_activeGroup_by_id(db: Session, activeGroup_id: int):
    try:
        result = db.query(ActiveGroup).filter(ActiveGroup.id == activeGroup_id).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar activeGroup {e}")

def get_activeGroup_by_name(db: Session, activeGroup_name: str):
    try:
        result = db.query(ActiveGroup).filter(ActiveGroup.name == activeGroup_name).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar activeGroup por name {e}")


def create_activeGroup(db: Session, activeGroup: ActiveGroupSchema):
    try:
        _activeGroup = ActiveGroup(
            name=activeGroup.name
        )

        db.add(_activeGroup)
        db.commit()
        db.refresh(_activeGroup)
        return _activeGroup
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Error creando activeGroup {e}")


def update_activeGroup(db: Session, activeGroup_id: int, name_edited: str):
    activeGroup_to_edit = db.query(ActiveGroup).filter(ActiveGroup.id == activeGroup_id).first()
    try:
        if activeGroup_to_edit:
            activeGroup_to_edit.name = name_edited

            db.commit()
            act_group = get_activeGroup_by_id(db, activeGroup_id)
            return act_group
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="activeGroup no encontrada")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error editando activeGroup: {e}")

def delete_activeGroup(db: Session, activeGroup_id: int):
    
    try:
        db.query(Active_GroupActive).filter(Active_GroupActive.activeGroup_id == activeGroup_id).delete()

        activeGroup_to_delete = db.query(ActiveGroup).filter(ActiveGroup.id == activeGroup_id).first()
        if activeGroup_to_delete:
            db.delete(activeGroup_to_delete)
            db.commit()
            return activeGroup_id
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"activeGroup con id {activeGroup_id} no encontrada")
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error eliminando acción: {e}")

def search_collection(db: Session, search: str, limit: int = 25, offset: int = 0):
    try:
        count = db.query(ActiveGroup).filter(ActiveGroup.name.ilike(f"%{search}%")).count()
        if count == 0:
            return [], 0
        
        result = db.query(ActiveGroup).filter(ActiveGroup.name.ilike(f"%{search}%")).offset(offset).limit(limit).all()
        return result, count
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar activeGroup {e}")