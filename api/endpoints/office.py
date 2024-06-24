from models import office
from models.office import Office
# from database import engine
from fastapi import APIRouter, HTTPException, Path, Depends, Header
from sqlalchemy.orm import Session
from database import get_db, conexion
from crud.office import create_office, get_office_by_id, get_offices_all, get_office_by_id_sucursal, delete_office, update_office
from schemas.officeSchema import OfficeSchema, OfficeEditSchema
from schemas.schemaGenerico import ResponseGet, Response

from crud.user import get_user_disable_current
from typing import Tuple

#obtener id surcursal
from api.endpoints.sucursal import get_sucursal_by_id

router = APIRouter()
# office.Base.metadata.create_all(bind=engine)

@router.get('/offices')
def get_offices(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 300, offset: int = 0, companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result, count = get_offices_all(db, limit, offset)
    if not result:
        return ResponseGet(code= "404", result = [], limit= limit, offset = offset, count = 0).model_dump()
    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = count).model_dump()

@router.get("/officePorSucursal/{id_sucursal}")
def get_office_por_sucursal(id_sucursal: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 300, offset: int = 0, companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result, count = get_office_by_id_sucursal(db, id_sucursal,limit, offset)
    if not result:
        return ResponseGet(code= "404", result = [], limit= limit, offset = offset, count = 0).model_dump()
    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = count).model_dump()

@router.get("/office/{id}")
def get_office(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result = get_office_by_id(db, id)
    if result is None:
        return Response(code="404", result=[], message="Oficina no encontrada").model_dump()
    return Response(code= "200", message="Oficina encontrada" , result = result).model_dump()

@router.post('/office')
def create(request: OfficeSchema, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    if('floor' not in request and request.floor is None):
        return  Response(code = "400", message = "Piso no valido", result = [])

    if (len(request.name_in_charge) == 0):
     return  Response(code = "400", message = "Falta el nombre de la persona a cargo", result = [])

    id_sucursal = get_sucursal_by_id(db, request.sucursal_id)
    if (not id_sucursal):
        return Response(code="400", message="id sucursal no valido", result=[])

    _office = create_office(db, request, name_user)
    return Response(code = "201", message = f"Oficina piso {_office.floor} creada", result = _office).model_dump()

@router.put('/office/{id}')
def update(request: OfficeEditSchema, id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    if('floor' not in request and request.floor is None):
        return  Response(code = "400", message = "Piso no valido", result = [])

    if (len(request.name_in_charge) == 0):
     return  Response(code = "400", message = "Falta el nombre de la persona a cargo", result = [])

    _office = update_office(db, id, request, name_user)
    return Response(code = "201", message = f"Oficina piso {_office.floor} editada", result = _office).model_dump()

@router.delete('/office/{id}')
def delete(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    _office = delete_office(db, id, name_user)
    return Response(code = "201", message = f"Oficina con id {id} eliminada", result = _office).model_dump()