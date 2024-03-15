from models import active
# from database import engine
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query, Header
from sqlalchemy.orm import Session
from database import get_db, conexion
from crud.active import (get_active_all, get_active_by_id, create_active, update_active, delete_active, get_active_by_id_article, get_file_url, get_active_by_sucursal,
                         get_active_by_office, get_active_by_offices, count_active, get_active_by_article_and_barcode, search_active_sucursal, search_active_offices)
from schemas.activeSchema import ActiveSchema, ActiveEditSchema, ActiveUploadSchema
from schemas.schemaGenerico import Response, ResponseGet
from crud.office import get_office_by_id
from crud.article import get_article_by_id, get_article_by_code, create_article
from pathlib import Path
import re
from fastapi.responses import FileResponse
from dateutil import parser as date_parser

from crud.user import  get_user_disable_current, get_user_by_id
from typing import Tuple, List
from datetime import datetime
import pandas as pd

router = APIRouter()
# active.Base.metadata.create_all(bind=engine)

@router.get("/active/{id}")
def get_active(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result = get_active_by_id(db, id)
    if result is None:
        return Response(code= "404", result = [], message="Not found").model_dump()
    return Response(code= "200", result = result, message="Activo no encontrado").model_dump()

@router.get('/actives')
def get_actives(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current),limit: int = 25, offset: int = 0, companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result = get_active_all(db, limit, offset)
    count = count_active(db)
    if not result:
        return ResponseGet(code= "200", result = [], limit= limit, offset = offset, count = 0).model_dump()

    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = count).model_dump()

@router.get("/activePorArticle/{id_article}")
def get_active_por_article(id_article: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0, companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result, count = get_active_by_id_article(db, id_article,limit, offset)
    if not result:
        return ResponseGet(code= "200", result = [], limit= limit, offset = offset, count = 0).model_dump()

    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = count).model_dump()

@router.get("/active/office/{id_office}")
def get_active_por_office(id_office: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0, companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result, count = get_active_by_office(db, id_office,limit, offset)
    if not result:
        return ResponseGet(code= "200", result = [], limit= limit, offset = offset, count = 0).model_dump()
    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = count).model_dump()


@router.get("/active/offices/{id_offices}")
def get_active_por_offices(id_offices: str , db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0, companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    id_offices_list = id_offices.split(",")
    id_offices_int = [int(id_office) for id_office in id_offices_list]
    result, count = get_active_by_offices(db, id_offices_int, limit, offset)
    if not result:
        return ResponseGet(code="200", result=[], limit=limit, offset=offset, count=0).model_dump()
    return ResponseGet(code="200", result=result, limit=limit, offset=offset, count=count).model_dump()

@router.get("/active/sucursal/{sucursal_id}")
def get_actives_por_sucursal(sucursal_id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0, companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result, count = get_active_by_sucursal(db, sucursal_id, limit, offset)
    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = count).model_dump()


@router.get('/active/search/sucursal/{sucursal_id}')
def search_by_sucursal(sucursal_id: int, search: str, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0, companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result, count = search_active_sucursal(db, search, sucursal_id, limit, offset)
    if not result:
        return ResponseGet(code="200", result=[], limit=limit, offset=offset, count=0).model_dump()
    return ResponseGet(code="200", result=result, limit=limit, offset=offset, count=count).model_dump()

@router.get('/active/search/offices/{id_offices}')
def search_by_offices(id_offices: str, search: str, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0, companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    id_offices_list = id_offices.split(",")
    id_offices_int = [int(id_office) for id_office in id_offices_list]
    result, count = search_active_offices(db, search, id_offices_int, limit, offset)
    if not result:
        return ResponseGet(code="200", result=[], limit=limit, offset=offset, count=0).model_dump()
    return ResponseGet(code="200", result=result, limit=limit, offset=offset, count=count).model_dump()

@router.post("/file_active")
def upload_file(file: UploadFile = File(...), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    try:
        id_user, expiration_time = current_user_info
        # print("Tiempo de expiración: ", expiration_time)
        # Se valida la expiracion del token
        if expiration_time is None:
            return Response(code="401", message="token-exp", result=[])

        upload_folder = Path("files") / "files_active"
        upload_folder.mkdir(parents=True, exist_ok=True)  # Crea el directorio si no existe
        file_url = get_file_url(file, upload_folder)
        return Response(code="201", message="Archivo guardado con éxito", result=file_url).model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {e}")

@router.post('/active')
def create(request: ActiveSchema, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    if(len(request.bar_code) == 0):
        return  Response(code = "400", message = "código de barra no valido", result = [])

    # valida si existe un codigo de barra con el mismo numero dentro de los articulos
    #active_barcode = get_active_by_article_and_barcode(db, request.article_id, request.bar_code)
    print(request.bar_code)
    active_barcode = get_active_by_article_and_barcode(db, request.article_id, request.bar_code)
    if active_barcode:
        return Response(code="400", message="Código de barra ya ingresado", result=[])

    try:
        # Intenta convertir la fecha a un objeto date
        acquisition_date = date_parser.parse(str(request.acquisition_date)).date()

        # Verificar el formato específico
        if acquisition_date.strftime('%Y-%m-%d') != str(request.acquisition_date):
            return Response(code="400", message="Formato de fecha de adquisición no válido (debe ser YYYY-MM-DD)", result=[])

    except ValueError as e:
        return Response(code="400", message=str(e), result=[])

    #if(len(request.accounting_document) == 0):
        #return  Response(code = "400", message = "Documento de adquisición no valido", result = [])

    if (len(request.accounting_record_number) == 0):
        return Response(code="400", message="Numero registro contable no valido", result=[])

    if (len(request.name_in_charge_active) == 0):
        return Response(code="400", message="Nombre del responsable no valido", result=[])

    patron_rut = r'^\d{1,8}-[\dkK]$'
    rut = str(request.rut_in_charge_active.replace(".", ""))
    if not re.match(patron_rut, rut):
        return Response(code="400", message="Rut del encargado inválido", result=[])

    if (len(request.serie) == 0):
        return Response(code="400", message="Número de serie no valido", result=[])

    if (len(request.model) == 0):
        return Response(code="400", message="Modelo no valido", result=[])

    if (len(request.state) == 0):
        return Response(code="400", message="Estado no valido", result=[])

    #id_office = get_office_by_id(db, request.office_id)
    id_office = get_office_by_id(db, request.office_id)
    if(not id_office):
        return Response(code="400", message="id oficina no valido", result=[])

    #id_article = get_article_by_id(db, request.article_id)
    id_article = get_article_by_id(db, request.article_id)
    if (not id_article):
        return Response(code="400", message="id articulo no valido", result=[])

    #_active = create_active(db, request, name_user)
    _active = create_active(db, request, name_user)
    return Response(code = "201", message = f"Activo {_active.bar_code} creado", result = _active).model_dump()

@router.put('/active/{id}')
def update(request: ActiveEditSchema, id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    if (len(request.bar_code) == 0):
        return Response(code="400", message="codigo de barra no valido", result=[])

    # valida si existe un codigo de barra con el mismo numero dentro de los articulos
    #active_barcode = get_active_by_article_and_barcode(db, request.article_id, request.bar_code)
    active_barcode = get_active_by_article_and_barcode(db, request.article_id, request.bar_code)
    if active_barcode and id is not active_barcode.id:
        return Response(code="400", message="Codigo de barra ya ingresado", result=[])

    #activos_por_id_articles, count = get_active_by_id_article(db, request.article_id)
    #for active_por_article in activos_por_id_articles:
        #if (active_por_article.bar_code == request.bar_code and id is not active_por_article.id):
            #return Response(code="400", message="Codigo de barra ya ingresado", result=[])

    try:
        # Intenta convertir la fecha a un objeto date
        acquisition_date = date_parser.parse(str(request.acquisition_date)).date()

        # Verificar el formato específico
        if acquisition_date.strftime('%Y-%m-%d') != str(request.acquisition_date):
            return Response(code="400", message="Formato de fecha de adquisición no válido (debe ser YYYY-MM-DD)", result=[])

    except ValueError as e:
        return Response(code="400", message=str(e), result=[])

    #if (len(request.accounting_document) == 0):
        #return Response(code="400", message="Documento de adquisición no valido", result=[])

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

    #id_office = get_office_by_id(db, request.office_id)
    id_office = get_office_by_id(db, request.office_id)
    if (not id_office):
        return Response(code="400", message="id oficina no valido", result=[])

    id_article = get_article_by_id(db, request.article_id)
    if (not id_article):
        return Response(code="400", message="id articulo no valido", result=[])

    #_active = update_active(db, id,  request, name_user)
    _active = update_active(db, id, request, name_user)
    return Response(code = "201", message = f"Activo {_active.bar_code} editado", result = _active).model_dump()

@router.delete('/active/{id}')
def delete(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    #_active = delete_active(db, id, name_user)
    _active = delete_active(db, id, name_user)
    return Response(code = "201", message = f"Activo con id {id} eliminado", result = _active).model_dump()

@router.get("/file_active/{file_path}")
async def get_image(file_path: str):
    image = Path("files") / "files_active" / file_path
    if not image.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image)


@router.post("/active/upload")
def active_file(office_id: int, db: Session = Depends(get_db), file: UploadFile = File(...), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    try:
        name_user, expiration_time = current_user_info
        db = next(conexion(db, companyId))
        if db is None:
            return Response(code="404", result=[], message="BD no encontrada").model_dump()
        
        if expiration_time is None:
            return Response(code="401", message="token-exp", result=[])

        # Leer el archivo Excel en un DataFrame de pandas
        df = pd.read_csv(file.file)

        # Iterar sobre las filas del DataFrame
        for index, row in df.iterrows():
            # Aquí puedes acceder a los datos de cada fila
            codigo = str(row.iloc[0])
            serie = str(row.iloc[1])
            model = str(row.iloc[2])
            date = row.iloc[3]
            date = datetime.strptime(date, '%d-%m-%Y')
            # Convertir el objeto datetime de nuevo a una cadena, pero en el formato 'yyyy-mm-dd'
            date = date.strftime('%Y-%m-%d')

            state = str(row.iloc[4])
            comment = '' if pd.isna(row.iloc[5]) else row.iloc[5]
            name_charge = str(row.iloc[6])
            rut_charge = str(row.iloc[7])
            num_register = str(row.iloc[8])
            article_name = str(row.iloc[9])
            article_code = row.iloc[10]
            article_description = str(row.iloc[11])

            print(f"codigo: {codigo}, serie: {serie}, model: {model}, date: {date}, state: {state}, comment: {comment}, name_charge: {name_charge}, rut_charge: {rut_charge}, num_register: {num_register}, article_name: {article_name}, article_code: {article_code}, article_description: {article_description}")
            # 0. SI ARTICLE CODE NO EXISTE, NO HACER NADA. INDICAR EN CSV QUE NRO DE ARTICULO NO EXISTE.
            if pd.isna(article_code):
                print("No existe código de artículo")
                continue

            # 1. BUSCAR SI EXISTE ARTICULO.
            article = get_article_by_code(db, str(int(article_code)))
            print(f"article found: {article}")

            # 1.1 SI NO EXISTE ARTICULO, CREARLO
            if not article:
                print("Creando artículo")
                new_article = {
                    "name": article_name,
                    "code": str(int(article_code)),
                    "description": article_description
                }   
                print(f"")
                article = create_article(db, new_article, name_user)
                print(f"Article created: {article}")

            # 2. BUSCAR SI EXISTE ACTIVO.
            active = get_active_by_article_and_barcode(db, article.id, str(int(codigo)))

            # 2.1 CREAR EL ACTIVO. INDICAR SI YA ESTABA CREADO.
            print("Creando activo")
            new_active = {
                "bar_code": str(int(codigo)),
                "serie": serie,
                "model": model,
                "acquisition_date": date,
                "state": state,
                "comment": comment,
                "name_in_charge_active": name_charge,
                "rut_in_charge_active": rut_charge,
                "accounting_record_number": num_register,
                "article_id": article.id,
                "office_id": office_id,
            }
            print(f"new active: {new_active}")
            active = create_active(db, ActiveSchema(**new_active), name_user)
            print(f"Activo creado: {active}")




            # print(f"{index}: {row}")


        return Response(code="201", message="Archivo guardado con éxito", result=[]).model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {e}")