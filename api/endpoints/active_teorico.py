import pandas as pd
from typing import Tuple
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
        # df = pd.read_excel(file.file)
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
