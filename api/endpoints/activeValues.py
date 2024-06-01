from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from database import get_db, conexion
from crud.activeValues import create_activeValues, get_activeValues_by_id, get_activeValues_all, update_activeValues, delete_activeValues
from schemas.activeValuesSchema import ActiveValuesSchema, ActiveValuesEditSchema
from schemas.schemaGenerico import Response, ResponseGet
from crud.user import  get_user_disable_current
from typing import Tuple

router = APIRouter()
# action.Base.metadata.create_all(bind=engine)

@router.get('/actives/values')
def get_activeValues(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0, companyId: int = Header(None)):
    
    try:
        name_user, expiration_time = current_user_info

        db = next(conexion(db, companyId))
        if db is None:
            return Response(code="404", result=[], message="BD no encontrada").model_dump()

        # Se valida la expiracion del token
        if expiration_time is None:
            return Response(code="401", message="token-exp", result=[])

        result, count = get_activeValues_all(db)
      
        if not result:
            return ResponseGet(code="404", result=[], limit=limit, offset=offset, count=0).model_dump()
    
        return ResponseGet(code="200", result=result, limit=limit, offset=offset, count=count).model_dump()
    
    except Exception as e:
        return Response(code="404", result=[], message="Error al obtener activeValues").model_dump()
        

@router.get("/active/values/{id}", response_model=ActiveValuesSchema)
def get_activeValue(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result = get_activeValues_by_id(db, id)
    if result is None:
        raise HTTPException(status_code=404, detail="activeValues no encontrada")
    return result
@router.post('/active/values')
def create(request: ActiveValuesSchema, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    # Validación de valores no negativos
    if request.adq_value < 0 or request.real_value < 0 or request.useful_life < 0:
        return Response(code="400", message="Los valores de adquisición, real y vida útil no pueden ser negativos.", result=[])

    _activeValues = create_activeValues(db, request)
    return Response(code = "201", message = "ActiveValues creada", result = _activeValues).model_dump()

@router.put('/active/values/{id}')
def update(request: ActiveValuesEditSchema, id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    # Validación de valores no negativos
    if request.adq_value < 0 or request.real_value < 0 or request.useful_life < 0:
        return Response(code="400", message="Los valores de adquisición, real y vida útil no pueden ser negativos.", result=[])

    _activeValues = update_activeValues(db, id, request)
    return Response(code = "201", message = "activeValues editada", result = _activeValues).model_dump()

@router.delete('/active/values/{id}')
def delete(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    _activeValues = delete_activeValues(db, id)
    return Response(code = "201", message = f"activeValues con id {id} eliminada", result = _activeValues).model_dump()