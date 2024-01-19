from sqlalchemy.orm import Session, joinedload, join
from schemas.companySchema import CompanySchema, CompanyEditSchema
from sqlalchemy import desc, func, and_
from models.company import Company
from models.sucursal import Sucursal
from models.office import Office
from fastapi import HTTPException, status
#historial
from schemas.historySchema import HistorySchema
from crud.history import create_history


def get_company_all(db: Session, limit: int = 100, offset: int = 0):
    try:
        companies = (
            db.query(Company, func.count(Sucursal.id).label("count_sucursales"))
            .outerjoin(Sucursal, and_(Sucursal.company_id == Company.id, Sucursal.removed == 0))
            .filter(Company.removed == 0)
            .group_by(Company.id)
            .order_by(desc(Company.id))
            .offset(offset)
            .limit(limit)
            .all()
        )
        result = []
        for company in companies:
            company[0].count_sucursal = company[1]
            result.append(company[0])

        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar compania {e}")
    #return (db.query(Company).options(joinedload(Company.sucursales)).order_by(desc(Company.id)).offset(offset).limit(limit).all())

def get_company_all_id_name(db: Session, limit: int = 100, offset: int = 0):
    try:
        companies = (db.query(Company.id, Company.name).filter(Company.removed == 0).offset(offset).limit(limit).all())
        result = [{'id': company[0], 'name': company[1]} for company in companies]
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar compania por nombre {e}")

def count_company(db: Session):
    try:
        return db.query(Company).filter(Company.removed == 0).count()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al contar las companias {e}")

def get_company_by_id(db: Session, company_id: int):
    #print(company_id)
    #print(db)
    try:
        result = db.query(Company).filter(Company.id == company_id).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar compania {e}")


def get_company_by_sucursal(db: Session, sucursal_id: int, limit: int = 100, offset: int = 0):
    try:
        result = (db.query(Company).
                  join(Sucursal, Company.id == Sucursal.company_id).
                  filter(Sucursal.id == sucursal_id, Company.removed == 0).
                  offset(offset).limit(limit).all())
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener activos {e}")

def get_company_by_office(db: Session, office_id: int, limit: int = 100, offset: int = 0):
    try:
        result = (db.query(Company).
                  join(Sucursal, Company.id == Sucursal.company_id).
                  join(Office, Sucursal.id == Office.sucursal_id).
                  filter(Office.id == office_id, Company.removed == 0).
                  offset(offset).limit(limit).all())
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener activos {e}")

def create_company(db: Session, company: CompanySchema, id_user: int):
    try:
        _company = Company(
            name=company.name,
            rut=company.rut,
            country=company.country,
            contact_name=company.contact_name,
            contact_phone=company.contact_phone,
            contact_email=company.contact_email
        )

        db.add(_company)
        db.commit()
        db.refresh(_company)
        _company.count_sucursal = 0

        # creacion del historial
        history_params = {
            "description": "create-company",
            "company_id": _company.id,
            "current_session_user_id": id_user
        }
        create_history(db, HistorySchema(**history_params))

        return _company
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Error creando compania {e}")

def update_company(db: Session, company_id: int, company: CompanyEditSchema, id_user: int):

    try:
        company_to_edit = db.query(Company).filter(Company.id == company_id).first()
        if company_to_edit:
            company_to_edit.name = company.name
            company_to_edit.contact_name = company.contact_name
            company_to_edit.contact_phone = company.contact_phone
            company_to_edit.contact_email = company.contact_email

            db.commit()
            db.refresh(company_to_edit)
            #company_edited = get_company_by_id(db, company_id)
            # creacion del historial
            history_params = {
                "description": "update-company",
                "company_id": company_to_edit.id,
                "current_session_user_id": id_user
            }
            create_history(db, HistorySchema(**history_params))

            return company_to_edit
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compañia no encontrada")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error editando compañia: {e}")


def delete_company(db: Session, company_id: int, id_user: int):
    try:
        company_to_delete = db.query(Company).filter(Company.id == company_id).first()
        if company_to_delete:
            company_to_delete.removed = 1
            db.commit()

            # creacion del historial
            history_params = {
                "description": "delete-company",
                "company_id": company_id,
                "current_session_user_id": id_user
            }
            create_history(db, HistorySchema(**history_params))

            return company_id
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Compañia con id {company_id} no encontrada")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error eliminando compañia: {e}")

def search_company(db: Session, search: str):
    try:
        companies = (db.query(Company).filter(func.lower(Company.name).like(f"%{search}%")).all())
        return companies
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar compania por nombre {e}")