from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from models.active import Active
from models.article import Article
from models.office import Office
from models.active_teorico import ActiveTeorico
from sqlalchemy import func

def get_actives_equals(db: Session):
    try:
        #result = db.query(Active.bar_code).join(ActiveTeorico, Active.bar_code == ActiveTeorico.bar_code).all()
        result = (db.query(Active).join(Article).join(Office).join(ActiveTeorico, Active.bar_code == ActiveTeorico.bar_code).
                  options(joinedload(Active.article), joinedload(Active.office).joinedload(Office.sucursal)).all())

        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener códigos de activos coincidentes: {e}")

#Obtiene activos solo de la tabla activos teoricos
def get_actives_missing(db: Session):
    try:
        result = db.query(ActiveTeorico).outerjoin(Active, ActiveTeorico.bar_code == Active.bar_code).filter(Active.bar_code == None).all()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener códigos de activos coincidentes: {e}")

#Obtiene activos solo de la tabla activos
def get_actives_surplus(db: Session):
    try:
        #result = db.query(Active.bar_code).outerjoin(ActiveTeorico, Active.bar_code == ActiveTeorico.bar_code).filter(ActiveTeorico.bar_code == None).all()
        result = (db.query(Active).join(Article).join(Office).outerjoin(ActiveTeorico, Active.bar_code == ActiveTeorico.bar_code).filter(ActiveTeorico.bar_code == None, Active.removed == 0).
                  options(joinedload(Active.article), joinedload(Active.office).joinedload(Office.sucursal)).all())
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Error al obtener códigos de activos coincidentes: {e}")