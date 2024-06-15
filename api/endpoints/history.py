from models import history
from models.history import History
# from database import engine
from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from database import get_db, conexion
from crud.history import get_history_all, get_history_by_company, create_history, get_history_by_sucursal, get_history_by_office, get_history_by_article, get_history_by_active
from schemas.historySchema import HistorySchema
from schemas.schemaGenerico import Response, ResponseGet
from crud.user import  get_user_disable_current
from typing import Tuple, Optional
from fastapi.responses import JSONResponse

router = APIRouter()
# history.Base.metadata.create_all(bind=engine)

@router.get('/histories')
def get_histories(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0, companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return ResponseGet(code="404", result=[], limit=limit, offset=offset, count=0).model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result, count = get_history_all(db, limit, offset)
    if not result:
        return ResponseGet(code= "200", result = [], limit= limit, offset = offset, count = 0).model_dump()
    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = count).model_dump()

@router.get("/history/company/{id_company}")
def get_history_por_company(id_company: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, id_company))
    if db is None:
        return ResponseGet(code="404", result=[], limit=limit, offset=offset, count=0).model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result, count = get_history_by_company(db, id_company,limit, offset)
    if not result:
        return ResponseGet(code= "200", result = [], limit= limit, offset = offset, count = 0).model_dump()
    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = count).model_dump()

@router.get("/history/sucursal/{id_sucursal}")
def get_history_por_sucursal(id_sucursal: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0, companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return ResponseGet(code="404", result=[], limit=limit, offset=offset, count=0).model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result, count = get_history_by_sucursal(db, id_sucursal,limit, offset)
    if not result:
        return ResponseGet(code= "200", result = [], limit= limit, offset = offset, count = 0).model_dump()
    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = count).model_dump()

@router.get("/history/office/{id_office}")
def get_history_por_office(id_office: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0, companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return ResponseGet(code="404", result=[], limit=limit, offset=offset, count=0).model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result, count = get_history_by_office(db, id_office,limit, offset)
    if not result:
        return ResponseGet(code= "200", result = [], limit= limit, offset = offset, count = 0).model_dump()
    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = count).model_dump()

@router.get("/history/article/{id_article}")
def get_history_por_article(id_article: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0, companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return ResponseGet(code="404", result=[], limit=limit, offset=offset, count=0).model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result, count = get_history_by_article(db, id_article,limit, offset)
    if not result:
        return ResponseGet(code= "200", result = [], limit= limit, offset = offset, count = 0).model_dump()
    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = count).model_dump()

@router.get("/history/active/{id_active}")
def get_history_por_active(id_active: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0, companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return ResponseGet(code="404", result=[], limit=limit, offset=offset, count=0).model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result, count = get_history_by_active(db, id_active,limit, offset)
    if not result:
        return ResponseGet(code= "200", result = [], limit= limit, offset = offset, count = 0).model_dump()
    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = count).model_dump()

# @router.get("/history/user/{user_id}")
# def get_history_por_user(user_id: int, db: Session = Depends(get_db), current_user_info: Tuple[int, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0):
#     id_usera, expiration_time = current_user_info
#     #print(id_usera)
#     # Se valida la expiracion del token
#     if expiration_time is None:
#         return Response(code="401", message="token-exp", result=[])
#
#     result, count = get_history_by_user(db, user_id,limit, offset)
#     if not result:
#         return ResponseGet(code= "200", result = [], limit= limit, offset = offset, count = 0).model_dump()
#     return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = count).model_dump()


@router.post('/history')
def create(request: HistorySchema, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    name_user, expiration_time = current_user_info
    # print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    _history = create_history(db, request)
    return Response(code = "201", message = "Historial creado", result = _history).model_dump()
