from sqlalchemy.orm import Session, joinedload
from schemas.companySchema import CompanySchema
from models.company import Company
from fastapi import HTTPException, status

def get_company_all(db: Session, skip: int = 0, limit: int = 100):
    #return db.query(Company).offset(skip).limit(limit).all()
    #sucursales es la variable que se defie en el modelo company
    return (db.query(Company).options(joinedload(Company.sucursales)).offset(skip).limit(limit).all())

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