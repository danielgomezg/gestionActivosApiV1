from sqlalchemy.orm import Session, joinedload
from schemas.officeSchema import OfficeSchema
from models.office import Office
from fastapi import HTTPException, status
from sqlalchemy import desc, func

def get_offices_all(db: Session, skip: int = 0, limit: int = 100):
    #return db.query(Office).offset(skip).limit(limit).all()
    return (db.query(Office).options(joinedload(Office.sucursal)).offset(skip).limit(limit).all()) # Agrega la carga anidada de la relación 'sucursal'


def get_office_by_id_sucursal(db: Session, sucursal_id: int, limit: int = 100, offset: int = 0):
    offices = (
        db.query(Office)
        .filter(Office.sucursal_id == sucursal_id)  # Reemplaza "tu_valor_de_aid" con el valor real
        .group_by(Office.id)
        .order_by(desc(Office.id))
        .offset(offset)
        .limit(limit)
        .all()
    )
    result = []
    return offices


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

