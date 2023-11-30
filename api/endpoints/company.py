from models import company
from models.company import Company
from database import engine
from fastapi import APIRouter, HTTPException, Path, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud.company import create_company, get_company_by_id, get_company_all
from schemas.companySchema import Response, CompanySchema
import re

from crud.user import get_user_disable_current
from typing import Optional, Tuple

router = APIRouter()
company.Base.metadata.create_all(bind=engine)

@router.get('/companies')
async def get_companies(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    print("ID del usuario: ", id_user)
    print("Tiempo de expiración: ", expiration_time)
    result = get_company_all(db)
    return result

@router.get("/company/{id}", response_model=CompanySchema)
async def get_company(id: int, db: Session = Depends(get_db), current_user: str = Depends(get_user_disable_current)):
    result = get_company_by_id(db, id)
    print("getcompany")
    if result is None:
        raise HTTPException(status_code=404, detail="Compania no encontrada")
    return result
@router.post('/company')
async def create(request: CompanySchema, db: Session = Depends(get_db)):

    if(len(request.name) == 0):
        return  Response(code = "400", message = "Nombre no valido", result = [])

    patron_rut = r'^\d{1,8}-[\dkK]$'
    rut = str(request.rut.replace(".", ""))

    if not re.match(patron_rut, rut):
        return Response(code="400", message="Rut inválido", result=[])


    if (len(request.country) == 0):
        return Response(code="400", message="Pais no valido", result=[])

    _company = create_company(db, request)
    return Response(code = "201", message = "Empresa creada", result = _company).dict(exclude_none=True)





# from fastapi import APIRouter, status, Depends
# #from models.company import company
# #from database import connection
# from database import get_db
# from sqlalchemy.orm import Session
# from crud.company import create_company_DB
# #from companySchema import Company as CompanySchema
#
# router = APIRouter()
#
# #@router.get("/company")
# #def get_companies():
#  #   return connection.execute(company.select()).fetchall()
#
#
# @router.post('/company', status_code=status.HTTP_201_CREATED)
# def create_company(compania: CompanySchema, db:Session = Depends(get_db)):
#     create_company_DB(compania, db)
#     return {"respuesta": "Compania creado satisfactoriamente!!"}