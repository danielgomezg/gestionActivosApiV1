from sqlalchemy.orm import Session
from schemas.secuenciaVTSchema import SecuenciaVTSchema
from models.secuenciaVT import SecuenciaVT
from fastapi import HTTPException, status

def get_secuenciaVT_all(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(SecuenciaVT).offset(skip).limit(limit).all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener secuancias {e}")

def get_secuenciaVT_by_id(db: Session, secuenciaVT_id: int):
    try:
        result = db.query(SecuenciaVT).filter(SecuenciaVT.id == secuenciaVT_id).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar secuancia {e}")

def create_secuencia_vt(db: Session, initial_value: int = 0):
    try:
        _secuencia = SecuenciaVT(current_value=initial_value)
        db.add(_secuencia)
        db.commit()
        db.refresh(_secuencia)
        return _secuencia
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error creating sequence: {e}")

def get_next_sequence(db: Session):
    try:
        sequence = db.query(SecuenciaVT).with_for_update().first()
        if sequence:
            sequence.current_value += 1
            db.commit()
        else:
            sequence = create_secuencia_vt(db, 1)  # Inicia desde 1 si no hay secuencia
        return sequence.current_value
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error getting next sequence: {e}")