from sqlalchemy.orm import Session, joinedload
from schemas.officeSchema import OfficeSchema, OfficeEditSchema
from models.office import Office
from fastapi import HTTPException, status
from sqlalchemy import desc, func, cast, String

#historial
from schemas.historySchema import HistorySchema
from crud.history import create_history

def get_offices_all(db: Session, limit: int = 100, offset: int = 0):
    #return db.query(Office).offset(skip).limit(limit).all()
    try:
        result = (db.query(Office).options(joinedload(Office.sucursal)).filter(Office.removed == 0).offset(offset).limit(limit).all())
        count = db.query(Office).filter(Office.removed == 0).count()
        return result, count
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener oficinas {e}")

def get_offices_all_android(db: Session):
    return db.query(Office).filter(Office.removed == 0).all()

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
        #result = []
        count = db.query(Office).filter(Office.sucursal_id == sucursal_id, Office.removed == 0).count()
        return offices, count
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al oficina por sucursal {e}")

def search_office_select_by_sucursal(db: Session, search: str, sucursal_id: int , limit: int = 100, offset: int = 0):
    try:
        count = db.query(Office). \
            filter(
            Office.removed == 0,
            Office.sucursal_id == sucursal_id,
            (
                    func.lower(cast(Office.floor, String)).like(search) |
                    func.lower(Office.description).like(f"%{search}%")
            )).count()

        if count == 0:
            return [], count

        query = db.query(Office). \
            filter(
            Office.removed == 0,
            Office.sucursal_id == sucursal_id,
            (
                    func.lower(cast(Office.floor, String)).like(search) |
                    func.lower(Office.description).like(f"%{search}%")
            )
        ).order_by(Office.id.desc()).offset(offset).limit(limit)

        offices = query.all()

        return offices, count

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Error al buscar oficina por sucursal {e}")

def get_office_by_id(db: Session, office_id: int):
    try:
        result = db.query(Office).filter(Office.id == office_id, Office.removed == 0).options(joinedload(Office.sucursal)).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar oficina {e}")

def create_office(db: Session, office: OfficeSchema, name_user: str):
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

        oficce_content = get_office_by_id(db, _office.id)
        id_company = oficce_content.sucursal.company_id

        # creacion del historial
        history_params = {
            "description": "create-office",
            "office_id": _office.id,
            "sucursal_id": _office.sucursal_id,
            "name_user": name_user,
            "company_id": id_company
            #"current_session_user_id": id_user
        }
        create_history(db, HistorySchema(**history_params))

        return _office
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Error creando oficina {e}")

def update_office(db: Session, office_id: int, office: OfficeEditSchema, name_user: str):

    try:
        office_to_edit = db.query(Office).filter(Office.id == office_id).first()
        if office_to_edit:
            office_to_edit.description = office.description
            office_to_edit.floor = office.floor
            office_to_edit.name_in_charge = office.name_in_charge

            db.commit()

            oficce_content = get_office_by_id(db, office_to_edit.id)
            id_company = oficce_content.sucursal.company_id

            # creacion del historial
            history_params = {
                "description": "update-office",
                "office_id": office_to_edit.id,
                "sucursal_id": office_to_edit.sucursal_id,
                "name_user": name_user,
                "company_id": id_company
                #"current_session_user_id": id_user
            }
            create_history(db, HistorySchema(**history_params))

            return office_to_edit
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Oficina no encontrada")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error editando oficina: {e}")

def delete_office(db: Session, office_id: int, name_user: str):
    try:
        office_to_delete = db.query(Office).filter(Office.id == office_id).first()
        if office_to_delete:
            oficce_content = get_office_by_id(db, office_to_delete.id)
            office_to_delete.removed = 1
            db.commit()

            
            print(oficce_content.sucursal.company_id)
            id_company = oficce_content.sucursal.company_id

            # creacion del historial
            history_params = {
                "description": "delete-office",
                "office_id": office_to_delete.id,
                "sucursal_id": office_to_delete.sucursal_id,
                "name_user": name_user,
                "company_id": id_company
                #"current_session_user_id": id_user
            }
            create_history(db, HistorySchema(**history_params))

            return office_id
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Oficina con id {office_id} no encontrada")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error eliminando Oficina: {e}")

