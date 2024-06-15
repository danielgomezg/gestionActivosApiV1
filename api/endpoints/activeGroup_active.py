from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from database import get_db, conexion
from crud.activeGroup_active import get_activeGroup_active_by_id, get_activeGroup_active_all, create_activeGroup_active
from schemas.activeGroup_active import ActiveGroup_ActiveSchema
from schemas.schemaGenerico import Response, ResponseGet
from crud.user import get_user_disable_current
from typing import Tuple
from crud.active import get_active_by_id
from crud.activeGroup import get_activeGroup_by_id

router = APIRouter()
# profile_action.Base.metadata.create_all(bind=engine)

@router.get('/active/activesGroups')
def get_active_activesGroups(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0, companyId: int = Header(None), ):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    result, count = get_activeGroup_active_all(db)
    if not result:
        return ResponseGet(code= "200", result = [], limit= limit, offset = offset, count = 0).model_dump()

    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = count).model_dump()

@router.get("/active/activesGroup/{id}", response_model=ActiveGroup_ActiveSchema)
def get_active_activesGroup(id: int, db: Session = Depends(get_db), current_user: str = Depends(get_user_disable_current), companyId: int = Header(None)):
    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    result = get_activeGroup_active_by_id(db, id)
    if result is None:
        raise HTTPException(status_code=404, detail="active_activesGroup no encontrada")
    return result


@router.post('/active/activesGroup')
def create(request: ActiveGroup_ActiveSchema, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    id_active = get_active_by_id(db, request.active_id)
    if (not id_active):
        return Response(code="400", message=f"id del activo no valido", result=[])

    id_activesGroup = get_activeGroup_by_id(db, request.activeGroup_id)
    if (not id_activesGroup):
        return Response(code="400", message="id de la activesGroup no valido", result=[])

    _active_activesGroup = create_activeGroup_active(db, request)
    return Response(code = "201", message = "active_activesGroup creada", result = _active_activesGroup).model_dump()