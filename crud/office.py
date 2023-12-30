from sqlalchemy.orm import Session, joinedload
from schemas.officeSchema import OfficeSchema, OfficeEditSchema
from models.office import Office
from fastapi import HTTPException, status
from sqlalchemy import desc, func

def get_offices_all(db: Session, limit: int = 100, offset: int = 0):
    #return db.query(Office).offset(skip).limit(limit).all()
    try:
        return (db.query(Office).options(joinedload(Office.sucursal)).filter(Office.removed == 0).offset(offset).limit(limit).all())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener oficinas {e}")


def get_office_by_id_sucursal(db: Session, sucursal_id: int, limit: int = 100, offset: int = 0):
    try:
        offices = (
            db.query(Office)
            .filter(Office.sucursal_id == sucursal_id, Office.removed == 0)
            .group_by(Office.id)
            .order_by(desc(Office.id))
            .offset(offset)
            .limit(limit)
            .all()
        )
        result = []
        return offices
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al oficina por sucursal {e}")


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
            name_in_charge = office.name_in_charge,
            sucursal_id=office.sucursal_id
        )

        db.add(_office)
        db.commit()
        db.refresh(_office)
        return _office
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Error creando oficina {e}")

def update_office(db: Session, office_id: int, office: OfficeEditSchema):

    try:
        office_to_edit = db.query(Office).filter(Office.id == office_id).first()
        if office_to_edit:
            office_to_edit.description = office.description
            office_to_edit.floor = office.floor
            office_to_edit.name_in_charge = office.name_in_charge

            db.commit()
            office_edited = get_office_by_id(db, office_id)
            return office_edited
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Oficina no encontrada")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error editando oficina: {e}")

def delete_office(db: Session, office_id: int):
    try:
        office_to_delete = db.query(Office).filter(Office.id == office_id).first()
        if office_to_delete:
            office_to_delete.removed = 1
            db.commit()
            return office_id
            #return {"message": "Acción actualizada correctamente", "action": action_to_edit}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Oficina con id {office_id} no encontrada")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error eliminando Oficina: {e}")

