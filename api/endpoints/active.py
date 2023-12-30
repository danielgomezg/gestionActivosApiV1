from models import active
from database import engine
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud.active import get_active_all, get_active_by_id, create_active, update_active, delete_active, get_active_by_id_article
from schemas.activeSchema import ActiveSchema, ActiveEditSchema
from schemas.schemaGenerico import Response, ResponseGet
from crud.office import get_office_by_id
from crud.article import get_article_by_id

import re
from dateutil import parser as date_parser

from crud.user import  get_user_disable_current, get_user_by_id
from typing import Tuple

router = APIRouter()
active.Base.metadata.create_all(bind=engine)

@router.get("/active/{id}", response_model=ActiveSchema)
def get_active(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    # print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result = get_active_by_id(db, id)
    if result is None:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    return result

@router.get('/actives')
def get_actives(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current),limit: int = 25, offset: int = 0):
    id_user, expiration_time = current_user_info
    # print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result = get_active_all(db, limit, offset)
    return result

@router.get("/activePorArticle/{id_article}")
def get_active_por_article(id_article: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0):
    id_user, expiration_time = current_user_info
    #print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result = get_active_by_id_article(db, id_article,limit, offset)
    if not result:
        return ResponseGet(code= "404", result = [], limit= limit, offset = offset, count = 0).model_dump()
    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = len(result)).model_dump()

@router.post('/active')
def create(request: ActiveSchema, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    #print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    if(len(request.bar_code) == 0):
        return  Response(code = "400", message = "codigo de barra no valido", result = [])

    try:
        # Intenta convertir la fecha a un objeto date
        acquisition_date = date_parser.parse(str(request.acquisition_date)).date()

        # Verificar el formato específico
        if acquisition_date.strftime('%Y-%m-%d') != str(request.acquisition_date):
            return Response(code="400", message="Formato de fecha de adquisición no válido (debe ser YYYY-MM-DD)", result=[])

    except ValueError as e:
        return Response(code="400", message=str(e), result=[])

    if(len(request.accounting_document) == 0):
        return  Response(code = "400", message = "Documento de adquisición no valido", result = [])

    if (len(request.accounting_record_number) == 0):
        return Response(code="400", message="Numero registro contable no valido", result=[])

    if (len(request.name_in_charge_active) == 0):
        return Response(code="400", message="Nombre del responsable no valido", result=[])

    patron_rut = r'^\d{1,8}-[\dkK]$'
    rut = str(request.rut_in_charge_active.replace(".", ""))
    if not re.match(patron_rut, rut):
        return Response(code="400", message="Rut del responsable inválido", result=[])

    if (len(request.serie) == 0):
        return Response(code="400", message="Número de serie no valido", result=[])

    if (len(request.model) == 0):
        return Response(code="400", message="Modelo no valido", result=[])

    if (len(request.state) == 0):
        return Response(code="400", message="Esatdo no valido", result=[])

    id_office = get_office_by_id(db, request.office_id)
    if(not id_office):
        return Response(code="400", message="id oficina no valido", result=[])

    id_article = get_article_by_id(db, request.article_id)
    if (not id_article):
        return Response(code="400", message="id articulo no valido", result=[])

    _active = create_active(db, request)
    return Response(code = "201", message = "Activo creado", result = _active).model_dump()

@router.put('/active/{id}')
def update(request: ActiveEditSchema, id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    #print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    if (len(request.bar_code) == 0):
        return Response(code="400", message="codigo de barra no valido", result=[])

    try:
        # Intenta convertir la fecha a un objeto date
        acquisition_date = date_parser.parse(str(request.acquisition_date)).date()

        # Verificar el formato específico
        if acquisition_date.strftime('%Y-%m-%d') != str(request.acquisition_date):
            return Response(code="400", message="Formato de fecha de adquisición no válido (debe ser YYYY-MM-DD)", result=[])

    except ValueError as e:
        return Response(code="400", message=str(e), result=[])

    if (len(request.accounting_document) == 0):
        return Response(code="400", message="Documento de adquisición no valido", result=[])

    if (len(request.accounting_record_number) == 0):
        return Response(code="400", message="Numero registro contable no valido", result=[])

    if (len(request.name_in_charge_active) == 0):
        return Response(code="400", message="Nombre del responsable no valido", result=[])

    patron_rut = r'^\d{1,8}-[\dkK]$'
    rut = str(request.rut_in_charge_active.replace(".", ""))
    if not re.match(patron_rut, rut):
        return Response(code="400", message="Rut del responsable inválido", result=[])

    if (len(request.serie) == 0):
        return Response(code="400", message="Número de serie no valido", result=[])

    if (len(request.model) == 0):
        return Response(code="400", message="Modelo no valido", result=[])

    if (len(request.state) == 0):
        return Response(code="400", message="Esatdo no valido", result=[])

    id_office = get_office_by_id(db, request.office_id)
    if (not id_office):
        return Response(code="400", message="id oficina no valido", result=[])

    _active = update_active(db, id,  request)
    return Response(code = "201", message = "Activo editado", result = _active).model_dump()

@router.delete('/active/{id}')
def delete(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    # print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    _active = delete_active(db, id)
    return Response(code = "201", message = f"Activo con id {id} eliminado", result = _active).model_dump()