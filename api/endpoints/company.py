from fastapi import APIRouter, status, Depends
#from models.company import company
#from database import connection
from database import get_db
from sqlalchemy.orm import Session
from crud.company import create_company_DB
from companySchema import Company as CompanySchema

router = APIRouter()

#@router.get("/company")
#def get_companies():
 #   return connection.execute(company.select()).fetchall()


@router.post('/company', status_code=status.HTTP_201_CREATED)
def create_company(compania: CompanySchema, db:Session = Depends(get_db)):
    create_company_DB(compania, db)
    return {"respuesta": "Compania creado satisfactoriamente!!"}