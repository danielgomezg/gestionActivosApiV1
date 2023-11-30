from models import sucursal
from models.sucursal import Sucursal
from database import engine
from fastapi import APIRouter, HTTPException, Path, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud.sucursal import create_sucursal, get_sucursal_by_id, get_sucursal_all
from schemas.sucursalSchema import Response, SucursalSchema

from crud.user import get_user_disable_current

#importacion de compania para comprobar si existe
from api.endpoints.company import get_company_by_id

router = APIRouter()
sucursal.Base.metadata.create_all(bind=engine)


@router.get('/sucursales')
async def get_sucursales(db: Session = Depends(get_db), current_user: str = Depends(get_user_disable_current)):
    result = get_sucursal_all(db)
    return result

@router.get("/sucursal/{id}", response_model=SucursalSchema)
async def get_sucursal(id: int, db: Session = Depends(get_db), current_user: str = Depends(get_user_disable_current)):
    result = get_sucursal_by_id(db, id)
    if result is None:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    return result
@router.post('/sucursal')
async def create(request: SucursalSchema, db: Session = Depends(get_db)):

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

    id_company = get_company_by_id(db, request.company_id)
    if(not id_company):
        return Response(code="400", message="id compania no valido", result=[])

    _sucursal = create_sucursal(db, request)
    return Response(code = "201", message = "Sucursal creada", result = _sucursal).dict(exclude_none=True)