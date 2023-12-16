from models import company
from models.company import Company
from database import engine
from fastapi import APIRouter, HTTPException, Path, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud.company import create_company, get_company_by_id, get_company_all, count_company, get_company_all_id_name
from schemas.companySchema import Response, CompanySchema,CompanySchemaIdName
from schemas.schemaGenerico import ResponseGet
import re

from crud.user import get_user_disable_current
from typing import Optional, Tuple

router = APIRouter()
#company.Base.metadata.create_all(bind=engine)


@router.get('/companies')
async def get_companies(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0):
    id_user, expiration_time = current_user_info
    print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return  Response(code = "401", message = "Su sesión ha expirado", result = [])

    count = count_company(db)
    if(count == 0):
        return ResponseGet(code="404", result=[], limit=limit, offset=offset, count=count).dict(exclude_none=True)
    result = get_company_all(db, limit, offset)
    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = count).dict(exclude_none=True)

@router.get('/companiesIdName')
async def get_companies_id_name(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0):
    id_user, expiration_time = current_user_info
    print("funcion companiesIdName")
    #Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="Su sesión ha expirado", result=[])

    count = count_company(db)
    if(count == 0):
        return ResponseGet(code="404", result=[], limit=limit, offset=offset, count=count).dict(exclude_none=True)
    result = get_company_all_id_name(db, limit, offset)
    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = count).dict(exclude_none=True)

@router.get("/company/{id}", response_model=CompanySchema)
async def get_company(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    # print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="Su sesión ha expirado", result=[])

    result = get_company_by_id(db, id)
    if result is None:
        raise HTTPException(status_code=404, detail="Compania no encontrada")
    return result

@router.post('/company')
async def create(request: CompanySchema, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    # print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="Su sesión ha expirado", result=[])

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