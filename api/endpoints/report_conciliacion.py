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
from reportlab.pdfgen import canvas
from crud.generation_catalogo import draw_table
#para prueba de datos
import copy

router = APIRouter()

@router.get("/active/report/excel/conciliacion/iguales")
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

        # Verificar si la carpeta existe, de lo contrario, crearla
        folder_path = 'Generations_files/report_conciliacion/iguales_excel'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Lógica para generar el catálogo Excel
        excel_filename = f'Reporte_conciliacion_iguales_{company.name}.xlsx'
        excel_path = os.path.join(folder_path, excel_filename)

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

@router.get("/active/report/pdf/conciliacion/iguales")
def report_conciliacion_equals_pdf(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    try:
        name_user, expiration_time = current_user_info
        db = next(conexion(db, companyId))
        if db is None:
            return Response(code="404", result=[], message="BD no encontrada").model_dump()

        if expiration_time is None:
            return Response(code="401", message="token-exp", result=[])

        company = get_company_by_id(db, companyId)
        actives = get_actives_equals(db)

        # Creando mas datos para test
        #while len(actives) < 80:
            #actives.extend(copy.deepcopy(actives))

        # Lógica para generar el catálogo PDF con ReportLab
        ruta_temporal = os.path.abspath(f"Generations_files/report_conciliacion/iguales_pdf/Reporte_conciliacion_iguales_{company.name}.pdf")
        os.makedirs(os.path.dirname(ruta_temporal), exist_ok=True)

        custom_page_size = (816, 1056)

        with (open(ruta_temporal, 'wb') as f):

            pdf = canvas.Canvas(f, pagesize=custom_page_size)

            width, height = pdf._pagesize

            pdf.setTitle(f"Reporte de conciliación iguales")

            # Agregamos el título al PDF
            pdf.setFont("Helvetica-Bold", 20)
            pdf.drawString((width/2) - 150, height - 40, f"Reporte de conciliación iguales")

            # Crear y configurar la tabla
            table_data = [
                ["Código", "Modelo", "Serie", "F. Adquisición", "Num. de registro", "Estado", "Encargado",
                 "Rut encargado", "Cod. articulo", "Oficina"]]

            cant_items = 0
            page_number = 1
            #comienzo primera pag
            eje_y_table = height - 90
            # comienzo demas pag
            eje_y = height - 70
            for i, active in enumerate(actives, start=1):

                if ((eje_y_table - (20 * len(table_data))) < 60 and i < len(actives)):
                    if (page_number == 1):
                        draw_table(pdf, table_data, eje_y_table)
                    else:
                        draw_table(pdf, table_data, eje_y)
                    cant_items = i
                    pdf.setFont("Helvetica", 8)
                    pdf.drawRightString(755, 30, f"Página {page_number}")
                    pdf.showPage()
                    table_data = [table_data[0]]
                    page_number += 1
                    #eje_y_table = height - 100

                table_data.append([
                    active.bar_code,
                    active.model,
                    active.serie,
                    str(active.acquisition_date),
                    active.accounting_record_number,
                    active.state,
                    active.name_in_charge_active,
                    active.rut_in_charge_active,
                    active.article.code,
                    str(active.office.floor) + " - " + active.office.description
                ])

            draw_table(pdf, table_data, eje_y_table)
            pdf.setFont("Helvetica", 8)
            pdf.drawRightString(755, 30, f"Página {page_number}")

            pdf.save()

        return FileResponse(ruta_temporal, filename=f"Reporte_conciliacion_iguales_{company.name}.pdf", media_type="application/pdf")

    except Exception as e:
        print("no funco")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active/report/excel/conciliacion/faltantes")
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

        # Verificar si la carpeta existe, de lo contrario, crearla
        folder_path = 'Generations_files/report_conciliacion/faltantes_excel'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Lógica para generar el catálogo Excel
        excel_filename = f'Reporte_conciliacion_faltantes_{company.name}.xlsx'
        excel_path = os.path.join(folder_path, excel_filename)

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

@router.get("/active/report/pdf/conciliacion/faltantes")
def report_conciliacion_missing_pdf(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    try:
        name_user, expiration_time = current_user_info
        db = next(conexion(db, companyId))
        if db is None:
            return Response(code="404", result=[], message="BD no encontrada").model_dump()

        if expiration_time is None:
            return Response(code="401", message="token-exp", result=[])

        company = get_company_by_id(db, companyId)
        actives = get_actives_missing(db)

        # Creando mas datos para test
        #while len(actives) < 80:
            #actives.extend(copy.deepcopy(actives))

        # Lógica para generar el catálogo PDF con ReportLab
        ruta_temporal = os.path.abspath(f"Generations_files/report_conciliacion/faltantes_pdf/Reporte_conciliacion_faltantes_{company.name}.pdf")
        os.makedirs(os.path.dirname(ruta_temporal), exist_ok=True)

        custom_page_size = (816, 1056)

        with (open(ruta_temporal, 'wb') as f):

            pdf = canvas.Canvas(f, pagesize=custom_page_size)

            width, height = pdf._pagesize

            pdf.setTitle(f"Reporte de conciliación faltantes")

            # Agregamos el título al PDF
            pdf.setFont("Helvetica-Bold", 20)
            pdf.drawString((width/2) - 150, height - 40, f"Reporte de conciliación faltantes")

            # Crear y configurar la tabla
            table_data = [["Código de activo", "Fecha de compra", "Denominación del activo fijo", "Valor de adquisición", "Valor contable"]]

            #cant_items = 0
            page_number = 1
            #comienzo primera pag
            eje_y_table = height - 90
            # comienzo demas pag
            eje_y = height - 70
            for i, active in enumerate(actives, start=1):

                if ((eje_y_table - (20 * len(table_data))) < 60 and i < len(actives)):
                    if (page_number == 1):
                        draw_table(pdf, table_data, eje_y_table, 100)
                    else:
                        draw_table(pdf, table_data, eje_y, 100)
                    #cant_items = i
                    pdf.setFont("Helvetica", 8)
                    pdf.drawRightString(755, 30, f"Página {page_number}")
                    pdf.showPage()
                    table_data = [table_data[0]]
                    page_number += 1
                    #eje_y_table = height - 100

                table_data.append([
                    active.bar_code,
                    active.acquisition_date,
                    active.description,
                    active.valor_adq,
                    active.valor_cont
                ])

            draw_table(pdf, table_data, eje_y_table, 100)
            pdf.setFont("Helvetica", 8)
            pdf.drawRightString(755, 30, f"Página {page_number}")

            pdf.save()

        return FileResponse(ruta_temporal, filename=f"Reporte_conciliacion_faltantes_{company.name}.pdf", media_type="application/pdf")

    except Exception as e:
        print("no funco")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active/report/excel/conciliacion/sobrantes")
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

        # Verificar si la carpeta existe, de lo contrario, crearla
        folder_path = 'Generations_files/report_conciliacion/sobrantes_excel'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Lógica para generar el catálogo Excel
        excel_filename = f'Reporte_conciliacion_sobrantes_{company.name}.xlsx'
        excel_path = os.path.join(folder_path, excel_filename)

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

@router.get("/active/report/pdf/conciliacion/sobrantes")
def report_conciliacion_surplus_pdf(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    try:
        name_user, expiration_time = current_user_info
        db = next(conexion(db, companyId))
        if db is None:
            return Response(code="404", result=[], message="BD no encontrada").model_dump()

        if expiration_time is None:
            return Response(code="401", message="token-exp", result=[])

        company = get_company_by_id(db, companyId)
        actives = get_actives_surplus(db)

        # Creando mas datos para test
        #while len(actives) < 80:
            #actives.extend(copy.deepcopy(actives))

        # Lógica para generar el catálogo PDF con ReportLab
        ruta_temporal = os.path.abspath(f"Generations_files/report_conciliacion/sobrantes_pdf/Reporte_conciliacion_sobrantes_{company.name}.pdf")
        os.makedirs(os.path.dirname(ruta_temporal), exist_ok=True)

        custom_page_size = (816, 1056)

        with (open(ruta_temporal, 'wb') as f):

            pdf = canvas.Canvas(f, pagesize=custom_page_size)

            width, height = pdf._pagesize

            pdf.setTitle(f"Reporte de conciliación sobrantes")

            # Agregamos el título al PDF
            pdf.setFont("Helvetica-Bold", 20)
            pdf.drawString((width/2) - 150, height - 40, f"Reporte de conciliación sobrantes")

            # Crear y configurar la tabla
            table_data = [
                ["Código", "Modelo", "Serie", "F. Adquisición", "Num. de registro", "Estado", "Encargado",
                 "Rut encargado", "Cod. articulo", "Oficina"]]

            page_number = 1
            #comienzo primera pag
            eje_y_table = height - 90
            # comienzo demas pag
            eje_y = height - 70
            for i, active in enumerate(actives, start=1):

                if ((eje_y_table - (20 * len(table_data))) < 60 and i < len(actives)):
                    if (page_number == 1):
                        draw_table(pdf, table_data, eje_y_table)
                    else:
                        draw_table(pdf, table_data, eje_y)
                    pdf.setFont("Helvetica", 8)
                    pdf.drawRightString(755, 30, f"Página {page_number}")
                    pdf.showPage()
                    table_data = [table_data[0]]
                    page_number += 1
                    #eje_y_table = height - 100

                table_data.append([
                    active.bar_code,
                    active.model,
                    active.serie,
                    str(active.acquisition_date),
                    active.accounting_record_number,
                    active.state,
                    active.name_in_charge_active,
                    active.rut_in_charge_active,
                    active.article.code,
                    str(active.office.floor) + " - " + active.office.description
                ])

            draw_table(pdf, table_data, eje_y_table)
            pdf.setFont("Helvetica", 8)
            pdf.drawRightString(755, 30, f"Página {page_number}")

            pdf.save()

        return FileResponse(ruta_temporal, filename=f"Reporte_conciliacion_sobrantes_{company.name}.pdf", media_type="application/pdf")

    except Exception as e:
        print("no funco")
        raise HTTPException(status_code=500, detail=str(e))