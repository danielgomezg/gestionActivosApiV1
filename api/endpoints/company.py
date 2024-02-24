from models import company
from models.company import Company
# from database import engine
from fastapi import APIRouter, HTTPException, Path, Depends
from sqlalchemy.orm import Session
from database import get_db, create_database, conexion
from crud.company import (create_company, get_company_by_id, get_company_all, count_company, get_company_all_id_name, delete_company, update_company,
                          search_company, get_company_by_rut_and_country, get_company_by_name)
from schemas.companySchema import CompanySchema,CompanySchemaIdName, CompanyEditSchema
from schemas.schemaGenerico import ResponseGet, Response
import re

from crud.user import get_user_disable_current
from typing import Optional, Tuple

router = APIRouter()
#company.Base.metadata.create_all(bind=engine)


@router.get('/companies')
def get_companies(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0):
    name_user, expiration_time = current_user_info
    # Se valida la expiracion del token
    if expiration_time is None:
        return  Response(code = "401", message = "token-exp", result = [])

    count = count_company(db)
    if(count == 0):
        return ResponseGet(code="404", result=[], limit=limit, offset=offset, count=count).model_dump()
    result = get_company_all(db, limit, offset)
    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = count).model_dump()

@router.get('/companiesIdName')
def get_companies_id_name(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0):
    name_user, expiration_time = current_user_info
    #Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    count = count_company(db)
    if(count == 0):
        return ResponseGet(code="404", result=[], limit=limit, offset=offset, count=count).model_dump()
    result = get_company_all_id_name(db, limit, offset)
    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = count).model_dump()

@router.get('/company/search')
def search(search: str, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0):
    name_user, expiration_time = current_user_info
    # print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])
    
    result, count = search_company(db, search, limit, offset)
    #return Response(code= "200", message = "Empresas encontradas", result = result).model_dump()
    if not result:
        return ResponseGet(code= "200", result = [], limit= limit, offset = offset, count = 0).model_dump()
    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = count).model_dump()

@router.get("/company/{id}")
def get_company(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    name_user, expiration_time = current_user_info
    # print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result = get_company_by_id(db, id)
    if result is None:
        return Response(code= "404", result = [], message="Not found").model_dump()
    return Response(code= "200", result = result, message="Company found").model_dump()

# @router.get("/company/sucursal/office/{office_id}")
# def get_company_offices(office_id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0):
#     name_user, expiration_time = current_user_info
#     # Se valida la expiracion del token
#     if expiration_time is None:
#         return Response(code="401", message="token-exp", result=[])
#
#     result, count = get_company_by_office(db, office_id, limit, offset)
#     if not result:
#         return ResponseGet(code= "200", result = [], limit= limit, offset = offset, count = 0).model_dump()
#     return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = count).model_dump()

@router.post('/company')
def create(request: CompanySchema, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    name_user, expiration_time = current_user_info
    # print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    if(len(request.name) == 0):
        return  Response(code = "400", message = "Nombre de la empresa vacio", result = [])
    name_company = get_company_by_name(db, request.name)
    if(name_company):
        return Response(code="400", message="nombre de compania ya ingresado", result=[])

    if (len(request.country) == 0):
        return Response(code="400", message="Pais no valido", result=[])

    #Valida RUT
    if(request.country == "Chile"):
        patron_rut = r'^\d{1,8}-[\dkK]$'
        rut = str(request.rut.replace(".", ""))

        if not re.match(patron_rut, rut):
            return Response(code="400", message="Rut inválido", result=[])

    # Valida DNI
    if (request.country == "Perú"):
        patron_dni = r'^\d{8}[a-zA-Z]?$'
        dni = str(request.rut.replace(".", ""))
        if not re.match(patron_dni, dni):
            return Response(code="400", message="DNI inválido", result=[])

    # valida si existe una compania con el mismo rut y pais
    company_rut_country = get_company_by_rut_and_country(db, request.rut, request.country)
    if company_rut_country:
        return Response(code="400", message="rut de compania ya ingresado", result=[])

    if (len(request.contact_name) == 0):
        return Response(code="400", message="Nombre del contacto vacio", result=[])

    if (len(request.contact_phone) == 0):
        return Response(code="400", message="Telefono del contacto vacio", result=[])

    patron = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if (re.match(patron, request.contact_email) is None):
        return Response(code="400", message="Email del contacto invalido", result=[])

    _company = create_company(db, request, name_user)
    #Creando nueva bd para la empresa e inserta la empresa
    create_database(_company.name_db)
    
    db_company = next(conexion(_company.name_db))
    _company_db_own = create_company(db_company, request, name_user)

    return Response(code = "201", message = f"Empresa {_company.name} creada", result = _company).model_dump()

@router.put('/company/{id}')
def update(request: CompanyEditSchema, id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    name_user, expiration_time = current_user_info
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    if(len(request.name) == 0):
        return  Response(code = "400", message = "Nombre de la empresa vacio", result = [])
    name_company = get_company_by_name(db, request.name)
    if (name_company and name_company.id is not id):
        return Response(code="400", message="nombre de compania ya ingresado", result=[])

    if (len(request.contact_name) == 0):
        return Response(code="400", message="Nombre del contacto vacio", result=[])

    if (len(request.contact_phone) == 0):
        return Response(code="400", message="Telefono del contacto vacio", result=[])

    patron = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if (re.match(patron, request.contact_email) is None):
        return Response(code="400", message="Email del contacto invalido", result=[])

    _company = update_company(db, id, request, name_user)

    db_company = next(conexion(_company.name.lower().replace(" ", "_")))
    _company_db_own = update_company(db_company, 1, request, name_user)
    return Response(code = "201", message = f"La Empresa {_company.name} editada", result = _company).model_dump()

@router.delete('/company/{id}')
def delete(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    name_user, expiration_time = current_user_info
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    _company, name_company = delete_company(db, id, name_user)

    print(name_company)
    db_company = next(conexion(name_company.lower().replace(" ", "_")))
    _company_db_own = delete_company(db_company, 1, name_user)

    return Response(code = "201", message = f"Compañia con id {id} eliminada", result = _company).model_dump()