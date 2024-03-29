from typing import Tuple
from sqlalchemy.orm import Session
from database import get_db, conexion
from fastapi.responses import FileResponse
from crud.user import  get_user_disable_current
from fastapi import APIRouter, Depends, Header, HTTPException
from schemas.schemaGenerico import Response
from crud.report_conciliacion import get_actives_equals, get_actives_missing, get_actives_surplus
from crud.company import get_company_by_id
import xlsxwriter
import os

router = APIRouter()

@router.get("/active/report/conciliacion/iguales")
def report_conciliacion_equals_excel(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    try:
        name_user, expiration_time = current_user_info
        db = next(conexion(db, companyId))
        if db is None:
            return Response(code="404", result=[], message="BD no encontrada").model_dump()

        if expiration_time is None:
            return Response(code="401", message="token-exp", result=[])

        company = get_company_by_id(db, companyId)
        actives = get_actives_equals(db)

        # Lógica para generar el catálogo Excel
        excel_filename = f'Reporte_conciliacion_iguales_{company.name}.xlsx'
        excel_path = os.path.join('Generations_files', excel_filename)

        # Crear un libro de trabajo y una hoja de trabajo
        workbook = xlsxwriter.Workbook(excel_path)
        worksheet = workbook.add_worksheet()

        # ancho por defecto de las filas
        worksheet.set_default_row(18)

        # Configurar un formato para el título con la fuente Helvetica
        formato_titulo = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_name': 'Helvetica',
            'font_size': 16,
        })

        worksheet.set_row(0, 25)
        # Escribir el título en una celda específica
        worksheet.merge_range('C1:H1', f' Reporte de conciliación iguales ', formato_titulo)

        # Datos a escribir en el archivo Excel
        datos = ["Código", "Modelo", "Serie", "Fecha adquisición", "Num. de registro", "Estado", "Encargado",
                 "Rut encargado", "Cod. articulo", "Oficina"]

        start_table = 1

        # Configurar un formato para los encabezados
        formato_encabezado = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D3D3D3',
            'font_name': 'Helvetica',
            'font_size': 11,
            'border': 1
        })

        # Escribir los encabezados en la primera fila
        for col, encabezado in enumerate(datos):
            worksheet.write(start_table, col, encabezado, formato_encabezado)

        # Ancho de cada celda del encabezado
        width_column = [0] * len(datos)
        for index, value in enumerate(datos):
            width_column[index] = len(value)

        # Configurar un formato para los datos
        formato_datos = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'font_name': 'Helvetica',
            'font_size': 9
        })

        # Escribir los datos desde la base de datos en el resto de las filas
        for row, active in enumerate(actives, start=1):
            for col, value in enumerate([active.bar_code, active.model, active.serie, str(active.acquisition_date),
                                         active.accounting_record_number, active.state, active.name_in_charge_active,
                                         active.rut_in_charge_active, str(active.article.code),
                                         str(active.office.floor) + " - " + active.office.description]):
                width_column[col] = max(width_column[col], len(value))
                worksheet.write(row + start_table, col, value, formato_datos)

        # Ajustar automáticamente el ancho de las columnas después de escribir los datos
        for index, col in enumerate(width_column):
            worksheet.set_column(index, index, width_column[index] + 3)

        # Cerrar el libro de trabajo (guardará el archivo)
        workbook.close()

        # Devolver el archivo Excel usando FileResponse
        return FileResponse(excel_path, filename=excel_filename,
                            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        print("no funco")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active/report/conciliacion/faltantes")
def report_conciliacion_missing_excel(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    try:
        name_user, expiration_time = current_user_info
        db = next(conexion(db, companyId))
        if db is None:
            return Response(code="404", result=[], message="BD no encontrada").model_dump()

        if expiration_time is None:
            return Response(code="401", message="token-exp", result=[])

        company = get_company_by_id(db, companyId)
        actives_teoricos = get_actives_missing(db)

        # Lógica para generar el catálogo Excel
        excel_filename = f'Reporte_conciliacion_faltantes_{company.name}.xlsx'
        excel_path = os.path.join('Generations_files', excel_filename)

        # Crear un libro de trabajo y una hoja de trabajo
        workbook = xlsxwriter.Workbook(excel_path)
        worksheet = workbook.add_worksheet()

        # ancho por defecto de las filas
        worksheet.set_default_row(18)

        # Configurar un formato para el título con la fuente Helvetica
        formato_titulo = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_name': 'Helvetica',
            'font_size': 16,
        })

        worksheet.set_row(0, 25)
        # Escribir el título en una celda específica
        worksheet.merge_range('B1:D1', ' Reporte de conciliación faltantes ', formato_titulo)

        # Datos a escribir en el archivo Excel
        datos = ["Código de activo", "Fecha de compra", "Denominación del activo fijo", "Valor de adquisición", "Valor contable"]

        start_table = 1

        # Configurar un formato para los encabezados
        formato_encabezado = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D3D3D3',
            'font_name': 'Helvetica',
            'font_size': 11,
            'border': 1
        })

        # Escribir los encabezados en la primera fila
        for col, encabezado in enumerate(datos):
            worksheet.write(start_table, col, encabezado, formato_encabezado)

        # Ancho de cada celda del encabezado
        width_column = [0] * len(datos)
        for index, value in enumerate(datos):
            width_column[index] = len(value)

        # Configurar un formato para los datos
        formato_datos = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'font_name': 'Helvetica',
            'font_size': 9
        })

        # Escribir los datos desde la base de datos en el resto de las filas
        for row, active in enumerate(actives_teoricos, start=1):
            for col, value in enumerate([active.bar_code, active.acquisition_date,
                                         active.description, active.valor_adq, active.valor_cont]):
                width_column[col] = max(width_column[col], len(value))
                worksheet.write(row + start_table, col, value, formato_datos)

        # Ajustar automáticamente el ancho de las columnas después de escribir los datos
        for index, col in enumerate(width_column):
            worksheet.set_column(index, index, width_column[index] + 3)

        # Cerrar el libro de trabajo (guardará el archivo)
        workbook.close()

        # Devolver el archivo Excel usando FileResponse
        return FileResponse(excel_path, filename=excel_filename,
                            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        print("no funco")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active/report/conciliacion/sobrantes")
def report_conciliacion_surplus_excel(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    try:
        name_user, expiration_time = current_user_info
        db = next(conexion(db, companyId))
        if db is None:
            return Response(code="404", result=[], message="BD no encontrada").model_dump()

        if expiration_time is None:
            return Response(code="401", message="token-exp", result=[])

        company = get_company_by_id(db, companyId)
        actives = get_actives_surplus(db)

        # Lógica para generar el catálogo Excel
        excel_filename = f'Reporte_conciliacion_sobrantes_{company.name}.xlsx'
        excel_path = os.path.join('Generations_files', excel_filename)

        # Crear un libro de trabajo y una hoja de trabajo
        workbook = xlsxwriter.Workbook(excel_path)
        worksheet = workbook.add_worksheet()

        # ancho por defecto de las filas
        worksheet.set_default_row(18)

        # Configurar un formato para el título con la fuente Helvetica
        formato_titulo = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_name': 'Helvetica',
            'font_size': 16,
        })

        worksheet.set_row(0, 25)
        # Escribir el título en una celda específica
        worksheet.merge_range('C1:H1', ' Reporte de conciliación sobrantes ', formato_titulo)

        # Datos a escribir en el archivo Excel
        datos = ["Código", "Modelo", "Serie", "Fecha adquisición", "Num. de registro", "Estado", "Encargado",
                 "Rut encargado", "Cod. articulo", "Oficina"]

        start_table = 1

        # Configurar un formato para los encabezados
        formato_encabezado = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D3D3D3',
            'font_name': 'Helvetica',
            'font_size': 11,
            'border': 1
        })

        # Escribir los encabezados en la primera fila
        for col, encabezado in enumerate(datos):
            worksheet.write(start_table, col, encabezado, formato_encabezado)

        # Ancho de cada celda del encabezado
        width_column = [0] * len(datos)
        for index, value in enumerate(datos):
            width_column[index] = len(value)

        # Configurar un formato para los datos
        formato_datos = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'font_name': 'Helvetica',
            'font_size': 9
        })

        # Escribir los datos desde la base de datos en el resto de las filas
        for row, active in enumerate(actives, start=1):
            for col, value in enumerate([active.bar_code, active.model, active.serie, str(active.acquisition_date),
                                         active.accounting_record_number, active.state, active.name_in_charge_active,
                                         active.rut_in_charge_active, str(active.article.code),
                                         str(active.office.floor) + " - " + active.office.description]):
                width_column[col] = max(width_column[col], len(value))
                worksheet.write(row + start_table, col, value, formato_datos)

        # Ajustar automáticamente el ancho de las columnas después de escribir los datos
        for index, col in enumerate(width_column):
            worksheet.set_column(index, index, width_column[index] + 3)

        # Cerrar el libro de trabajo (guardará el archivo)
        workbook.close()

        # Devolver el archivo Excel usando FileResponse
        return FileResponse(excel_path, filename=excel_filename,
                            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        print("no funco")
        raise HTTPException(status_code=500, detail=str(e))