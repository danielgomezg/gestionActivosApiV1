from sqlalchemy.orm import Session
from schemas.officeSchema import OfficeSchema
from models.office import Office
from fastapi import HTTPException, status

def get_offices_all(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Office).offset(skip).limit(limit).all()

def get_office_by_id(db: Session, office_id: int):
    try:
        result = db.query(Office).filter(Office.id == office_id).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar oficina {e}")

def create_office(db: Session, office: OfficeSchema):
    try:
        _office = Office(
            description=office.description,
            floor = office.floor,
            sucursal_id=office.sucursal_id
        )

        db.add(_office)
        db.commit()
        db.refresh(_office)
        return _office
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Error creando oficina {e}")