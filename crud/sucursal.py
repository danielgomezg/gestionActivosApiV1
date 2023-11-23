from sqlalchemy.orm import Session
from schemas.sucursalSchema import SucursalSchema
from models.sucursal import Sucursal
from fastapi import HTTPException, status

def get_sucursal_all(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Sucursal).offset(skip).limit(limit).all()

def get_sucursal_by_id(db: Session, sucursal_id: int):
    return db.query(Sucursal).filter(Sucursal.id == sucursal_id).first()

def create_sucursal(db: Session, sucursal: SucursalSchema):
    try:
        _sucursal = Sucursal(
            description=sucursal.description,
            number = sucursal.number,
            address = sucursal.address,
            city = sucursal.city,
            commune=sucursal.commune,
            company_id=sucursal.company_id
        )

        db.add(_sucursal)
        db.commit()
        db.refresh(_sucursal)
        return _sucursal
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Error creando sucursal {e}")