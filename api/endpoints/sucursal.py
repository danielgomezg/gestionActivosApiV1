from models import sucursal
from models.sucursal import Sucursal
from database import engine
from fastapi import APIRouter, HTTPException, Path, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud.sucursal import create_sucursal, get_sucursal_by_id, get_sucursal_all
from schemas.sucursalSchema import Response, SucursalSchema, SucursalRequest

router = APIRouter()
sucursal.Base.metadata.create_all(bind=engine)


@router.get('/sucursales')
async def get_sucursales(db: Session = Depends(get_db)):
    result = get_sucursal_all(db)
    return result

@router.get("/sucursal/{id}", response_model=SucursalSchema)
async def get_sucursal(id: int, db: Session = Depends(get_db)):
    result = get_sucursal_by_id(db, id)
    if result is None:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    return result
@router.post('/sucursal')
async def create(request: SucursalRequest, db: Session = Depends(get_db)):

    if(len(request.parameter.description) == 0):
        return  Response(code = "400", message = "Descripcion no valida", result = [])

    if(len(request.parameter.address) == 0):
        return  Response(code = "400", message = "direccion no valida", result = [])

    if (len(request.parameter.city) == 0):
        return Response(code="400", message="Ciudad no valida", result=[])

    if (len(request.parameter.commune) == 0):
        return Response(code="400", message="Comuna no valida", result=[])

    if ('number' not in request.parameter and request.parameter.number is None):
        return Response(code="400", message="Numero no valido", result=[])

    _sucursal = create_sucursal(db, request.parameter)
    return Response(code = "201", message = "Sucursal creada", result = _sucursal).dict(exclude_none=True)