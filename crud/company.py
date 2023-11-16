from sqlalchemy.orm import Session
from models.company import Company as DBCompany
from fastapi import HTTPException, status

def create_company_DB(company, db:Session):
    company = company.dict()
    print(company)
    try:
        new_company = DBCompany(
            id = company["id"],
            name = company["name"]
        )
        db.add(new_company)
        db.commit()
        db.refresh(new_company)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error creando compania {e}")