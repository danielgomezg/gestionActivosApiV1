from models import office
from models.office import Office
from database import engine
from fastapi import APIRouter, HTTPException, Path, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud.office import create_office, get_office_by_id, get_offices_all
from schemas.officeSchema import Response, OfficeSchema

from crud.user import get_user_disable_current

#obtener id surcursal
from api.endpoints.sucursal import get_sucursal_by_id

router = APIRouter()
office.Base.metadata.create_all(bind=engine)

@router.get('/offices')
async def get_offices(db: Session = Depends(get_db), current_user: str = Depends(get_user_disable_current)):
    result = get_offices_all(db)
    return result

@router.get("/office/{id}", response_model=OfficeSchema)
async def get_office(id: int, db: Session = Depends(get_db), current_user: str = Depends(get_user_disable_current)):
    result = get_office_by_id(db, id)
    if result is None:
        raise HTTPException(status_code=404, detail="Oficina no encontrada")
    return result

@router.post('/office')
async def create(request: OfficeSchema, db: Session = Depends(get_db)):

    if(len(request.description) == 0):
        return  Response(code = "400", message = "Descripcion no valida", result = [])

    if('floor' not in request and request.floor is None):
        return  Response(code = "400", message = "Piso no valido", result = [])

    id_sucursal = get_sucursal_by_id(db, request.sucursal_id)
    if (not id_sucursal):
        return Response(code="400", message="id sucursal no valido", result=[])

    _office = create_office(db, request)
    return Response(code = "201", message = "Oficina creada", result = _office).dict(exclude_none=True)