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

#Para la Generacion de catatlogo
# def get_company_by_sucursal(db: Session, sucursal_id: int, limit: int = 100, offset: int = 0):
#     try:
#         result = (db.query(Company).
#                   join(Sucursal, Company.id == Sucursal.company_id).
#                   filter(Sucursal.id == sucursal_id, Company.removed == 0).
#                   offset(offset).limit(limit).all())
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener activos {e}")


# def get_company_by_office(db: Session, office_id: int, limit: int = 100, offset: int = 0):
#     try:
#         result = (db.query(Company).
#                   join(Sucursal, Company.id == Sucursal.company_id).
#                   join(Office, Sucursal.id == Office.sucursal_id).
#                   filter(Office.id == office_id, Company.removed == 0).
#                   offset(offset).limit(limit).all())
#         count = db.query(Company).join(Sucursal, Company.id == Sucursal.company_id).join(Office, Sucursal.id == Office.sucursal_id).filter(Office.id == office_id, Company.removed == 0).count()
#         return result, count
#     except Exception as e:
#        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener activos {e}")

def get_company_by_rut_and_country(db: Session, rut: str, country: str, limit: int = 100, offset: int = 0):
    try:
        result = (db.query(Company).filter(Company.rut == rut, Company.country == country, Company.removed == 0).first())
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener empresa {e}")

def get_company_by_name(db: Session, name_company: str, limit: int = 100, offset: int = 0):
    try:
        result = (db.query(Company).filter(Company.name == name_company, Company.removed == 0).first())
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener empresa {e}")

def create_company(db: Session, company: CompanySchema, name_user: str, id_company_new_db: int = 0):
    try:
        print("creando....")
        if(id_company_new_db == 0):
            _company = Company(
                name=company.name,
                rut=company.rut,
                country=company.country,
                contact_name=company.contact_name,
                contact_phone=company.contact_phone,
                contact_email=company.contact_email,
                name_db=company.name.replace(" ", "_").lower()
            )
        else:
            _company = Company(
                id=id_company_new_db,
                name=company.name,
                rut=company.rut,
                country=company.country,
                contact_name=company.contact_name,
                contact_phone=company.contact_phone,
                contact_email=company.contact_email,
                name_db=company.name.replace(" ", "_").lower()
            )


        db.add(_company)
        db.commit()
        db.refresh(_company)
        print("termino...")

        # Actualiza name_db con la ID del nuevo registro
        _company.name_db = f"{company.name.replace(' ', '_').lower()}_{_company.id}"
        db.commit()
        db.refresh(_company)
        
        # creacion del historial
        history_params = {
            "description": "create-company",
            "company_id": _company.id,
            "name_user": name_user
            #"current_session_user_id": id_user
        }
        create_history(db, HistorySchema(**history_params))
        print("termino hisotrial")

        print(_company.id)
        return _company
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Error creando compania {e}")

def update_company(db: Session, company_id: int, company: CompanyEditSchema, name_user: str):

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
                "name_user": name_user
                #"current_session_user_id": id_user
            }
            create_history(db, HistorySchema(**history_params))

            return company_to_edit
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compañia no encontrada")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error editando compañia: {e}")

def delete_company(db: Session, company_id: int, name_user: str):
    try:
        company_to_delete = db.query(Company).filter(Company.id == company_id).first()
        if company_to_delete:
            company_to_delete.removed = 1
            db.commit()

            # creacion del historial
            history_params = {
                "description": "delete-company",
                "company_id": company_id,
                "name_user": name_user
                #"current_session_user_id": id_user
            }
            create_history(db, HistorySchema(**history_params))

            return company_id, company_to_delete.name
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Compañia con id {company_id} no encontrada")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error eliminando compañia: {e}")

def search_company(db: Session, search: str,  limit: int = 100, offset: int = 0):
    try:
        companies = (db.query(Company).filter(func.lower(Company.name).like(f"%{search}%"), Company.removed == 0).offset(offset).limit(limit).all())
        count = db.query(Company).filter(func.lower(Company.name).like(f"%{search}%")).count()
        return companies, count
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar compania por nombre {e}")
    

def get_name_db_company(db: Session, company_id: int):
    try:
        return db.query(Company.name_db).filter(Company.id == company_id).first()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar compania por nombre {e}")
