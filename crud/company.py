from sqlalchemy.orm import Session, joinedload
from schemas.companySchema import CompanySchema, CompanyEditSchema
from sqlalchemy import desc, func
from models.company import Company
from models.sucursal import Sucursal
from fastapi import HTTPException, status


def get_company_all(db: Session, limit: int = 100, offset: int = 0):
    try:
        companies = (
            db.query(Company, func.count(Sucursal.id).label("count_sucursales"))
            .outerjoin(Sucursal)  # Asegúrate de ajustar el nombre de la relación si es diferente
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
        companies = (db.query(Company.id, Company.name).offset(offset).limit(limit).all())
        result = [{'id': company[0], 'name': company[1]} for company in companies]
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar compania por nombre {e}")

def count_company(db: Session):
    try:
        return db.query(Company).count()
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


def create_company(db: Session, company: CompanySchema):
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
        return _company
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Error creando compania {e}")

def update_company(db: Session, company_id: int, company: CompanyEditSchema):

    try:
        company_to_edit = db.query(Company).filter(Company.id == company_id).first()
        if company_to_edit:
            company_to_edit.name = company.name
            company_to_edit.contact_name = company.contact_name
            company_to_edit.contact_phone = company.contact_phone
            company_to_edit.contact_email = company.contact_email

            db.commit()
            company_edited = get_company_by_id(db, company_id)
            return company_edited
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compañia no encontrada")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error editando compañia: {e}")


def delete_company(db: Session, company_id: int):
    company_to_delete = db.query(Company).filter(Company.id == company_id).first()
    try:
        if company_to_delete:
            db.delete(company_to_delete)
            db.commit()
            return company_id
            #return {"message": "Acción actualizada correctamente", "action": action_to_edit}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Compañia con id {company_id} no encontrada")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error eliminando compañia: {e}")

