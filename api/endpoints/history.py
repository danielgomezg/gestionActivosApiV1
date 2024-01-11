from models import history
from models.history import History
from database import engine
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud.history import get_history_all, get_history_by_company, create_history
from schemas.historySchema import HistorySchema
from schemas.schemaGenerico import Response, ResponseGet
from crud.user import  get_user_disable_current
from typing import Tuple, Optional
from fastapi.responses import JSONResponse

router = APIRouter()
history.Base.metadata.create_all(bind=engine)

@router.get('/histories')
def get_histories(db: Session = Depends(get_db), current_user_info: Tuple[str, str, Optional[dict]] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0):
    id_user, expiration_time, additional_info = current_user_info
    #print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result = get_history_all(db, limit, offset)
    return result

@router.get("/history/company/{id_company}")
def get_history_por_company(id_company: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str, Optional[dict]] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0):
    id_user, expiration_time, additional_info = current_user_info
    #print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result = get_history_by_company(db, id_company,limit, offset)
    if not result:
        return ResponseGet(code= "200", result = [], limit= limit, offset = offset, count = 0).model_dump()
    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = len(result)).model_dump()


@router.post('/action')
def create(request: HistorySchema, db: Session = Depends(get_db), current_user_info: Tuple[str, str, Optional[dict]] = Depends(get_user_disable_current)):
    id_user, expiration_time, additional_info = current_user_info
    # print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    #if(len(request.name) == 0):
        #return  Response(code = "400", message = "Nombre de accion no valido", result = [])

    _history = create_history(db, request)
    return Response(code = "201", message = "Historial creado", result = _history).model_dump()
