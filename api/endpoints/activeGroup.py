from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from database import get_db, conexion
from crud.activeGroup import create_activeGroup, get_activeGroup_by_id, get_activeGroup_all, update_activeGroup, delete_activeGroup, search_collection
from crud.activeGroup_active import create_collection_actives, get_actives_by_idCollection, update_collection_actives
from schemas.activeGroupSchema import ActiveGroupSchema, CollectionSchema
from schemas.schemaGenerico import Response, ResponseGet
from crud.user import  get_user_disable_current
from typing import Tuple

router = APIRouter()
# action.Base.metadata.create_all(bind=engine)

@router.get('/activesGroups')
def get_activesGroups(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0, companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result, count = get_activeGroup_all(db, offset, limit)
    # return result
    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = count).model_dump()

@router.get("/activesGroup/{id}", response_model=ActiveGroupSchema)
def get_activesGroup(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result = get_activeGroup_by_id(db, id)
    if result is None:
        raise HTTPException(status_code=404, detail="activesGroup no encontrada")
    return result

@router.post('/activesGroup')
def create(request: ActiveGroupSchema, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    if(len(request.name) == 0):
        return  Response(code = "400", message = "Nombre de activesGroup no valido", result = [])

    _activesGroup = create_activeGroup(db, request)
    return Response(code = "201", message = "ActivesGroup creada", result = _activesGroup).model_dump()

@router.put('/activesGroup/{id}')
def update(request: ActiveGroupSchema, id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    if(len(request.name) == 0):
        return  Response(code = "400", message = "Nombre de activesGroup no valido", result = [])

    _activesGroup = update_activeGroup(db, id, request.name)
    return Response(code = "201", message = "ActivesGroup editada", result = _activesGroup).model_dump()

@router.delete('/activesGroup/{id}')
def delete(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    _activesGroup = delete_activeGroup(db, id)
    return Response(code = "201", message = f"ActivesGroup con id {id} eliminada", result = _activesGroup).model_dump()

@router.post('/actives/collections')
def create_collection(request: CollectionSchema, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    if(len(request.name) == 0):
        return  Response(code = "400", message = "Nombre de activesGroup no valido", result = [])

    _collection = create_activeGroup(db, request)

    # Si se crea la colleccion, se crea la tabla intermedia
    _actives = create_collection_actives(db, request, _collection.id)
    _collection.actives_count = len(_actives)
    
    return Response(code = "201", message = f"Coleccion {_collection.name} creado", result = _collection).model_dump()

@router.get('/actives/collections/search')
def get_actives_collection_search(search: str, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None), limit: int = 25, offset: int = 0):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result, count = search_collection(db, search, limit, offset)
    if result is None:
        raise HTTPException(status_code=404, detail="activesGroup no encontrada")
    
    return ResponseGet(code= "200", result = result, limit=limit, offset=offset, count = count ).model_dump()

@router.get('/actives/collections/{id}')
def get_actives_collection(id: int, db: Session = Depends(get_db), current_user: str = Depends(get_user_disable_current), companyId: int = Header(None)):
    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    result = get_actives_by_idCollection(db, id)
    if result is None:
        raise HTTPException(status_code=404, detail="activesGroup no encontrada")
    
    return ResponseGet(code= "200", result = result, limit=0, offset=0, count = len(result) ).model_dump()

@router.put('/actives/collections/{id}')
def update_collection(request: CollectionSchema, id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    if(len(request.name) == 0):
        return  Response(code = "400", message = "Nombre de activesGroup no valido", result = [])

    _collection = update_activeGroup(db, id, request.name)

    # Editar la tabla intermedia
    _actives = update_collection_actives(db, _collection.id, request.activesId)
    

    return Response(code = "200", message = f"Coleccion {_collection.name} editada", result = _collection).model_dump()