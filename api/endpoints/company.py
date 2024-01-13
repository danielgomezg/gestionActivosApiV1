from models import company
from models.company import Company
from database import engine
from fastapi import APIRouter, HTTPException, Path, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud.company import create_company, get_company_by_id, get_company_all, count_company, get_company_all_id_name, delete_company, update_company, search_company
from schemas.companySchema import CompanySchema,CompanySchemaIdName, CompanyEditSchema
from schemas.schemaGenerico import ResponseGet, Response
import re

from crud.user import get_user_disable_current
from typing import Optional, Tuple

router = APIRouter()
#company.Base.metadata.create_all(bind=engine)


@router.get('/companies')
def get_companies(db: Session = Depends(get_db), current_user_info: Tuple[int, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0):
    id_user, expiration_time = current_user_info
    #print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return  Response(code = "401", message = "token-exp", result = [])

    count = count_company(db)
    if(count == 0):
        return ResponseGet(code="404", result=[], limit=limit, offset=offset, count=count).model_dump()
    result = get_company_all(db, limit, offset)
    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = count).model_dump()

@router.get('/companiesIdName')
def get_companies_id_name(db: Session = Depends(get_db), current_user_info: Tuple[int, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0):
    id_user, expiration_time = current_user_info
    #print("funcion companiesIdName")
    #Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    count = count_company(db)
    if(count == 0):
        return ResponseGet(code="404", result=[], limit=limit, offset=offset, count=count).model_dump()
    result = get_company_all_id_name(db, limit, offset)
    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = count).model_dump()

@router.get('/company/search')
def search(search: str, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    # print("Tiempo de expiración: ", expiration_time)
    print("funcion search")
    print(search)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    # count = count_company(db)
    # if(count == 0):
    #     return ResponseGet(code="404", result=[], limit=limit, offset=offset, count=count).model_dump()
    
    result = search_company(db, search)
    return Response(code= "200", message = "Empresas encontradas", result = result).model_dump()

@router.get("/company/{id}", response_model=CompanySchema)
def get_company(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    # print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result = get_company_by_id(db, id)
    if result is None:
        raise HTTPException(status_code=404, detail="Compania no encontrada")
    return result

@router.post('/company')
def create(request: CompanySchema, db: Session = Depends(get_db), current_user_info: Tuple[int, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    # print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    if(len(request.name) == 0):
        return  Response(code = "400", message = "Nombre de la empresa vacio", result = [])

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

    if (len(request.country) == 0):
        return Response(code="400", message="Pais no valido", result=[])

    if (len(request.contact_name) == 0):
        return Response(code="400", message="Nombre del contacto vacio", result=[])

    if (len(request.contact_phone) == 0):
        return Response(code="400", message="Telefono del contacto vacio", result=[])

    patron = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if (re.match(patron, request.contact_email) is None):
        return Response(code="400", message="Email del contacto invalido", result=[])

    _company = create_company(db, request, id_user)
    return Response(code = "201", message = f"Empresa {_company.name} creada", result = _company).model_dump()

@router.put('/company/{id}')
def update(request: CompanyEditSchema, id: int, db: Session = Depends(get_db), current_user_info: Tuple[int, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    # print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    if(len(request.name) == 0):
        return  Response(code = "400", message = "Nombre de la empresa vacio", result = [])

    if (len(request.contact_name) == 0):
        return Response(code="400", message="Nombre del contacto vacio", result=[])

    if (len(request.contact_phone) == 0):
        return Response(code="400", message="Telefono del contacto vacio", result=[])

    patron = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if (re.match(patron, request.contact_email) is None):
        return Response(code="400", message="Email del contacto invalido", result=[])

    _company = update_company(db, id, request, id_user)
    return Response(code = "201", message = f"La Empresa {_company.name} editada", result = _company).model_dump()

@router.delete('/company/{id}')
def delete(id: int, db: Session = Depends(get_db), current_user_info: Tuple[int, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    #print(additional_info)
    # print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    _company = delete_company(db, id, id_user)
    return Response(code = "201", message = f"Compañia con id {id} eliminada", result = _company).model_dump()