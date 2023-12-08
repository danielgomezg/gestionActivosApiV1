from sqlalchemy.orm import Session, joinedload
from schemas.companySchema import CompanySchema
from sqlalchemy import desc, func
from models.company import Company
from models.sucursal import Sucursal
from fastapi import HTTPException, status


def get_company_all(db: Session, limit: int = 100, offset: int = 0):
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
    #return (db.query(Company).options(joinedload(Company.sucursales)).order_by(desc(Company.id)).offset(offset).limit(limit).all())

def get_company_all_id_name(db: Session, limit: int = 100, offset: int = 0):
    companies = (db.query(Company.id, Company.name).offset(offset).limit(limit).all())
    result = [{'id': company[0], 'name': company[1]} for company in companies]
    return result

def count_company(db: Session):
    return db.query(Company).count()

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
            country=company.country
        )

        db.add(_company)
        db.commit()
        db.refresh(_company)
        return _company
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Error creando compania {e}")



# from sqlalchemy.orm import Session
# from models.company import Company as DBCompany
# from fastapi import HTTPException, status
#
# def create_company_DB(company, db:Session):
#     company = company.dict()
#     print(company)
#     try:
#         new_company = DBCompany(
#             id = company["id"],
#             name = company["name"]
#         )
#         db.add(new_company)
#         db.commit()
#         db.refresh(new_company)
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error creando compania {e}")