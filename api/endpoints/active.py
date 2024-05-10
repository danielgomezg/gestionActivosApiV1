from models.active import validateActiveFromFile
from models.article import validateArticleFromFile2
# from database import engine
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query, Header
from sqlalchemy.orm import Session
from database import get_db, conexion
from crud.active import (get_active_all, get_active_by_id, create_active, update_active, delete_active, get_active_by_id_article, get_file_url, get_active_by_sucursal,
                         get_active_by_office, get_active_by_offices, count_active, get_active_by_article_and_barcode, search_active_sucursal, search_active_offices,
                         get_image_url, generate_short_unique_id, get_active_by_virtual_code)
from schemas.activeSchema import ActiveSchema, ActiveEditSchema
from schemas.articleSchema import ArticleSchema
from schemas.schemaGenerico import Response, ResponseGet
from crud.office import get_office_by_id
from crud.article import get_article_by_id, get_article_by_code, create_article
from pathlib import Path
import re
import os
from fastapi.responses import FileResponse
from dateutil import parser as date_parser

from crud.user import  get_user_disable_current, get_user_by_id
from typing import Tuple
import pandas as pd
from datetime import datetime
import traceback

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

@router.post("/image_active")
def upload_image(file: UploadFile = File(...), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    try:
        id_user, expiration_time = current_user_info
        # Se valida la expiracion del token
        if expiration_time is None:
            return Response(code="401", message="token-exp", result=[])

        upload_folder = Path("files") / "images_active"
        upload_folder.mkdir(parents=True, exist_ok=True)
        photo_url = get_image_url(file, upload_folder)
        return Response(code="201", message="Foto guardada con éxito", result=photo_url).model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la imagen: {e}")


@router.post('/active')
def create(request: ActiveSchema, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    try:

        db = next(conexion(db, companyId))
        if db is None:
            return Response(code="404", result=[], message="BD no encontrada").model_dump()

        # Se valida la expiracion del token
        if expiration_time is None:
            return Response(code="401", message="token-exp", result=[])
        
        if (len(request.serie) == 0):
            return Response(code="400", message="Número de serie no valido", result=[])

        if(len(request.bar_code) == 0 and request.virtual_code == 'false'):
            return  Response(code = "400", message = "Código de activo fijo no válido", result = [])

        if(request.virtual_code == 'false'):

            # valida si existe un codigo de barra con el mismo numero dentro de los articulos
            active_barcode = get_active_by_article_and_barcode(db, request.article_id, request.bar_code)
            request.virtual_code = ""
            if active_barcode:
                return Response(code="400", message="Código de activo fijo ya ingresado", result=[])
        
        else:
            # generar codigo virtual con 20 digitos.
            request.virtual_code = generate_short_unique_id(request.serie)
            active_vc = get_active_by_virtual_code(db, request.virtual_code)
            intento = 0
            int_max = 100
            while(active_vc and intento < int_max):
                request.virtual_code = generate_short_unique_id(request.serie)
                active_vc = get_active_by_virtual_code(db, request.virtual_code)
                intento += 1
            if(intento > int_max):
                return Response(code="400", message=" Error al generar código virtual", result=[])
         
        # Intenta convertir la fecha a un objeto date
        acquisition_date = date_parser.parse(str(request.acquisition_date)).date()

        # Verificar el formato específico
        if acquisition_date.strftime('%Y-%m-%d') != str(request.acquisition_date):
            return Response(code="400", message="Formato de fecha de adquisición no válido (debe ser YYYY-MM-DD)", result=[])

        

        if (len(request.model) == 0):
            return Response(code="400", message="Modelo no valido", result=[])

        if (len(request.state) == 0):
            return Response(code="400", message="Estado no valido", result=[])

        if (len(request.brand) == 0):
            return Response(code="400", message="Marca no valida", result=[])

        id_office = get_office_by_id(db, request.office_id)
        if(not id_office):
            return Response(code="400", message="id oficina no valido", result=[])

        id_article = get_article_by_id(db, request.article_id)
        if (not id_article):
            return Response(code="400", message="id articulo no valido", result=[])

        _active = create_active(db, request, name_user)
        return Response(code = "201", message = f"Activo {_active.bar_code} creado", result = _active).model_dump()

    except ValueError as e:
            return Response(code="400", message=str(e), result=[])

@router.put('/active/{id}')
def update(request: ActiveEditSchema, id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    try:
        db = next(conexion(db, companyId))
        if db is None:
            return Response(code="404", result=[], message="BD no encontrada").model_dump()

        # Se valida la expiracion del token
        if expiration_time is None:
            return Response(code="401", message="token-exp", result=[])

        if (len(request.bar_code) == 0):
            return Response(code="400", message="codigo de barra no valido", result=[])

        # valida si existe un codigo de barra con el mismo numero dentro de los articulos
        active_barcode = get_active_by_article_and_barcode(db, request.article_id, request.bar_code)
        if active_barcode and id is not active_barcode.id:
            return Response(code="400", message="Codigo de barra ya ingresado", result=[])

   
        # Intenta convertir la fecha a un objeto date
        acquisition_date = date_parser.parse(str(request.acquisition_date)).date()

        # Verificar el formato específico
        if acquisition_date.strftime('%Y-%m-%d') != str(request.acquisition_date):
            return Response(code="400", message="Formato de fecha de adquisición no válido (debe ser YYYY-MM-DD)", result=[])

        #if (len(request.accounting_document) == 0):
            #return Response(code="400", message="Documento de adquisición no valido", result=[])

        #if (len(request.accounting_record_number) == 0):
            #return Response(code="400", message="Numero registro contable no valido", result=[])

        #if (len(request.name_in_charge_active) == 0):
            #return Response(code="400", message="Nombre del responsable no valido", result=[])

        #patron_rut = r'^\d{1,8}-[\dkK]$'
        #rut = str(request.rut_in_charge_active.replace(".", ""))
        #if not re.match(patron_rut, rut):
            #return Response(code="400", message="Rut del responsable inválido", result=[])

        if (len(request.serie) == 0):
            return Response(code="400", message="Número de serie no valido", result=[])

        if (len(request.model) == 0):
            return Response(code="400", message="Modelo no valido", result=[])

        if (len(request.state) == 0):
            return Response(code="400", message="Esatdo no valido", result=[])

        if (len(request.brand) == 0):
            return Response(code="400", message="Marca no valida", result=[])

        id_office = get_office_by_id(db, request.office_id)
        if (not id_office):
            return Response(code="400", message="id oficina no valido", result=[])

        id_article = get_article_by_id(db, request.article_id)
        if (not id_article):
            return Response(code="400", message="id articulo no valido", result=[])

        _active = update_active(db, id, request, name_user)
        return Response(code = "201", message = f"Activo {_active.bar_code} editado", result = _active).model_dump()

    except ValueError as e:
        print(e)
        traceback.print_exc()
        return Response(code="400", message=str(e), result=[])

@router.delete('/active/{id}')
def delete(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    _active = delete_active(db, id, name_user)
    return Response(code = "201", message = f"Activo con id {id} eliminado", result = _active).model_dump()

@router.get("/file_active/{file_path}")
async def get_file(file_path: str):
    image = Path("files") / "files_active" / file_path
    if not image.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(image)

@router.get("/image_active/{image_path}")
async def get_image(image_path: str):
    image = Path("files") / "images_active" / image_path
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
        num_columns = len(df.columns)
        print(f"Numero de columnas header: {num_columns}")

        failed = 0
        success = 0

        # Iterar sobre las filas del DataFrame
        for index, row in df.iterrows():

            article_Schema, msg = validateArticleFromFile2(row, companyId)
            if article_Schema is None:
                print("Datos del articulo no válidos")
                df.at[index, 'Guardado'] = "no"
                failed += 1
                continue

            # 1. BUSCAR SI EXISTE ARTICULO.
            article = get_article_by_code(db, article_Schema.code)

            # 1.1 SI NO EXISTE ARTICULO, CREARLO
            if not article:
                article = create_article(db, article_Schema, name_user)
                print(f"Article created: {article}")

            # 2.0 VALIDAR QUE LOS DATOS DEL ACTIVO SEAN CORRECTOS.
            activeSchema, msg = validateActiveFromFile(row, article.id, office_id)
            if activeSchema is None:
                print("Datos del activo no válidos")
                # print(msg)
                df.at[index, 'Guardado'] = "no"
                failed += 1
                continue

            print('activeSchema', activeSchema)

            # 2. BUSCAR SI EXISTE ACTIVO.
            active = get_active_by_article_and_barcode(db, article.id, str(int(activeSchema.bar_code)))

            if(active):
                print("existe el activo")
                df.at[index, 'Guardado'] = "ya registrado"
                failed += 1
                continue
            
            active = create_active(db, activeSchema, name_user)
            print(f"Activo creado: {active}")
            success += 1

            # Agregar la columna 'Completado' al DataFrame
            df.at[index, 'Guardado'] = 'Sí'

            # Sobrescribir el archivo original con los datos actualizados
            #df.to_excel(file.file, index=False)

        # Guardar el DataFrame actualizado en un nuevo archivo Excel
        new_file_path = os.path.join("files", f"{file.filename}_guardados.xlsx")
        df.to_excel(new_file_path, index=False)

        print()
        print(f"Guardados: {success}, No guardados: {failed}")

        #return Response(code="201", message="Archivo guardado con éxito", result=[]).model_dump()
        return FileResponse(new_file_path, filename=f"{file.filename}_guardados.xlsx")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {e}")