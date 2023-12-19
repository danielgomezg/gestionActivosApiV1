from models import sucursal
from models.sucursal import Sucursal
from database import engine
from fastapi import APIRouter, HTTPException, Path, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud.sucursal import create_sucursal, get_sucursal_by_id, get_sucursal_all, count_sucursal, get_sucursal_by_id_company
from schemas.sucursalSchema import Response, SucursalSchema
from schemas.schemaGenerico import ResponseGet
from typing import Tuple
from crud.user import get_user_disable_current

#importacion de compania para comprobar si existe
from api.endpoints.company import get_company_by_id

router = APIRouter()
sucursal.Base.metadata.create_all(bind=engine)


@router.get('/sucursales')
async def get_sucursales(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0):
    id_user, expiration_time = current_user_info
    #print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="Su sesión ha expirado", result=[])

    count = await count_sucursal(db)
    if(count == 0):
        return ResponseGet(code="404", result=[], limit=limit, offset=offset, count=count).model_dump()
    result = await get_sucursal_all(db, limit, offset)
    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = count).model_dump()

@router.get("/sucursal/{id}", response_model=SucursalSchema)
def get_sucursal(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    #print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="Su sesión ha expirado", result=[])

    result = get_sucursal_by_id(db, id)
    if result is None:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    return result

@router.get("/sucursalPorCompany/{id_company}")
def get_sucursal_por_company(id_company: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0):
    id_user, expiration_time = current_user_info
    #print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="Su sesión ha expirado", result=[])

    result = get_sucursal_by_id_company(db, id_company,limit, offset)
    if not result:
        return ResponseGet(code= "404", result = [], limit= limit, offset = offset, count = 0).model_dump()
    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = len(result)).model_dump()

@router.post('/sucursal')
def create(request: SucursalSchema, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    #print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="Su sesión ha expirado", result=[])

    if(len(request.description) == 0):
        return  Response(code = "400", message = "Descripcion no valida", result = [])

    if(len(request.address) == 0):
        return  Response(code = "400", message = "direccion no valida", result = [])

    if (len(request.region) == 0):
        return Response(code="400", message="Region no valida", result=[])

    if (len(request.commune) == 0):
        return Response(code="400", message="Comuna no valida", result=[])

    if ('number' not in request and request.number is None):
        return Response(code="400", message="Numero no valido", result=[])

    #valida si existe una sucursal con el mismo numero dentro de la empresa
    sucursales_por_id_company = get_sucursal_by_id_company(db, request.company_id)
    for sucursal_id_company in sucursales_por_id_company:
        if(sucursal_id_company.number == request.number):
            return Response(code="400", message="Número de sucursal ya ingresado", result=[])

    id_company = get_company_by_id(db, request.company_id)
    if(not id_company):
        return Response(code="400", message="id compania no valido", result=[])

    _sucursal = create_sucursal(db, request)
    return Response(code = "201", message = "Sucursal creada", result = _sucursal).model_dump()