import pandas as pd
import os
from typing import Tuple
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db, conexion
from schemas.schemaGenerico import Response
from crud.user import  get_user_disable_current
from crud.activo_teorico import create, delete_all_data
from models.active_teorico import validateActiveTeoricoFile
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Header

router = APIRouter()

@router.post("/active/teorico/upload")
def active_teorico_file(db: Session = Depends(get_db), file: UploadFile = File(...), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    try:
        name_user, expiration_time = current_user_info
        db = next(conexion(db, companyId))
        if db is None:
            return Response(code="404", result=[], message="BD no encontrada").model_dump()
        
        if expiration_time is None:
            return Response(code="401", message="token-exp", result=[])
            
        # Leer el archivo Excel en un DataFrame de pandas
        df = pd.read_csv(file.file)

        #Elimanar datos de bd de activo teorico
        delete_all_data(db)

        # Iterar a través del DataFrame fila por fila
        for index, row in df.iterrows():
            # Aquí puedes acceder a los datos de cada fila
            # Por ejemplo, si tu DataFrame tiene una columna llamada 'Columna1', puedes obtener su valor así:
            code = row.iloc[0]
            print(code)
            if not code.isnumeric():
                print("Código no numérico")
                continue
            
            activeTeoricSchema, msg = validateActiveTeoricoFile(row)
            if activeTeoricSchema is None:
                print("Datos del activo no válidos")
                # print(msg)
                # df.at[index, 'Guardado'] = "no"
                # failed += 1
                continue

            activeTeorico = create(db, activeTeoricSchema)
            if activeTeorico is None:
                print("Error al guardar activo")
                # df.at[index, 'Guardado'] = "no"
                # failed += 1
                continue
        
            print("Activo guardado")

        return Response(code="201", message="Activos teoricos guardados con éxito", result=[]).model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {e}")

@router.post("/active/template")
def active_teorico_template():
    # Lista de encabezados
    headers = ["Código de activo", "Fecha de compra", "Denominación del activo fijo", "Valor de adquisición", "Valor contable"]

    # Definir el título "TEORICO" en la primera fila (posición C1)
    title = ["", "", "TEORICO", "", ""]

    # Crear un DataFrame vacío con los encabezados
    df = pd.DataFrame(columns=title)

    # Insertar la fila de título al principio del DataFrame
    df.loc[-1] = headers
    df.index += 1
    df.sort_index(inplace=True)

    # Define la carpeta en la que quieres guardar el archivo
    folder_path = "files"

    # Verifica si la carpeta existe, si no, créala
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Define la ruta completa del archivo CSV
    csv_filename = os.path.join(folder_path, "Activo_teorico_template.csv")

    # Guarda el DataFrame como un archivo CSV en la carpeta especificada
    df.to_csv(csv_filename, index=False, encoding='utf-8-sig')

    # Devuelve el archivo CSV como respuesta
    return FileResponse(csv_filename, media_type='text/csv', filename="Activo_teorico_template.csv")


@router.get("/active/teorico/template")
def download_template_csv(current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    try:
        name_user, expiration_time = current_user_info

        if expiration_time is None:
            return Response(code="401", message="token-exp", result=[])

        # Define la ruta del archivo CSV
        csv_filepath = "files/Activo_teorico_template.csv"

        # Verifica que el archivo existe antes de servirlo
        if not os.path.exists(csv_filepath):
            return {"error": "Archivo no encontrado"}

        # Devuelve el archivo CSV como respuesta
        # Define el FileResponse para devolver el archivo CSV
        return FileResponse(
            csv_filepath,
            media_type="text/csv",
            filename="Activo_teorico_template.csv",
            headers={
                'Content-Disposition': f'attachment; filename="Activo_teorico_template.csv"'
            })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al descargar el template: {e}")