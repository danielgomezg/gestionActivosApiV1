from models import office
from models.office import Office
from database import engine
from fastapi import APIRouter, HTTPException, Path, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud.office import create_office, get_office_by_id, get_offices_all, get_office_by_id_sucursal
from schemas.officeSchema import Response, OfficeSchema
from schemas.schemaGenerico import ResponseGet

from crud.user import get_user_disable_current
from typing import Tuple

#obtener id surcursal
from api.endpoints.sucursal import get_sucursal_by_id

router = APIRouter()
office.Base.metadata.create_all(bind=engine)

@router.get('/offices')
def get_offices(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0):
    id_user, expiration_time = current_user_info
    #print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result = get_offices_all(db, limit, offset)
    return result

@router.get("/officePorSucursal/{id_sucursal}")
def get_office_por_sucursal(id_sucursal: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0):
    id_user, expiration_time = current_user_info
    #print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result = get_office_by_id_sucursal(db, id_sucursal,limit, offset)
    if not result:
        return ResponseGet(code= "404", result = [], limit= limit, offset = offset, count = 0).model_dump()
    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = len(result)).model_dump()

@router.get("/office/{id}", response_model=OfficeSchema)
def get_office(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    #print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result = get_office_by_id(db, id)
    if result is None:
        raise HTTPException(status_code=404, detail="Oficina no encontrada")
    return result

@router.post('/office')
def create(request: OfficeSchema, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    #print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    #if(len(request.description) == 0):
       # return  Response(code = "400", message = "Descripcion no valida", result = [])

    if('floor' not in request and request.floor is None):
        return  Response(code = "400", message = "Piso no valido", result = [])

    id_sucursal = get_sucursal_by_id(db, request.sucursal_id)
    if (not id_sucursal):
        return Response(code="400", message="id sucursal no valido", result=[])

    _office = create_office(db, request)
    return Response(code = "201", message = "Oficina creada", result = _office).model_dump()