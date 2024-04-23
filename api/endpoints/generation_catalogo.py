from fastapi import Depends, HTTPException, Header
from fastapi.responses import FileResponse
from fastapi import APIRouter
from typing import Tuple
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from schemas.schemaGenerico import Response
from sqlalchemy.orm import Session
from database import get_db, conexion
from crud.user import get_user_disable_current
import os
from datetime import datetime
import xlsxwriter
import pytz
import copy

from crud.generation_catalogo import (draw_multiline_text, portada_catalogo, generate_barcode, draw_table,
                                      calculator_space_article, next_page)
from crud.article import get_article_by_id_company
from crud.company import get_company_by_id
from crud.active import get_active_by_sucursal, get_active_by_offices

router = APIRouter()

@router.get("/report/article/{id_company}")
def articles_catalog(id_company: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    try:
        name_user, expiration_time = current_user_info
        # Se valida la expiracion del token
        if expiration_time is None:
            return Response(code="401", message="token-exp", result=[])

        db = next(conexion(db, id_company))
        if db is None:
            return Response(code="404", result=[], message="BD no encontrada").model_dump()

        # Lógica para obtener los detalles de los artículos
        articles, count = get_article_by_id_company(db, id_company, adjust_limit=True)
        company = get_company_by_id(db, id_company)

        #while len(articles) < 15:
            #articles.extend(copy.deepcopy(articles))

        #Fecha y hora
        chile_timezone = pytz.timezone('Chile/Continental')
        now = datetime.now(chile_timezone)
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")


        # Lógica para generar el catálogo PDF con ReportLab
        ruta_temporal = os.path.abspath("Generations_files/catalogo_reportlab.pdf")
        os.makedirs(os.path.dirname(ruta_temporal), exist_ok=True)

        ruta_barcodes = os.path.abspath("bar_codes")
        os.makedirs(ruta_barcodes, exist_ok=True)

        with open(ruta_temporal, 'wb') as f:
            pdf = canvas.Canvas(f, pagesize=letter)

            width, height = pdf._pagesize
            #print(f"Ancho del PDF: {width}, Alto del PDF: {height}")

            #Portada
            portada_catalogo(pdf,company)

            pdf.setTitle(f"Catálogo de Artículos des {company.name.upper()}")
            pdf.showPage()

            # Agregamos el título al PDF
            pdf.setFont("Helvetica", 16)
            pdf.drawCentredString(300, 750, f"Catálogo de Artículos de {company.name.upper()}")

            y_position = 770
            page_number = 1

            # Iteramos sobre los artículos y los agregamos al PDF
            y_line = 90
            for i, article in enumerate(articles, start=1):
                y_position -= y_line
                y_line = 0

                pdf.setFont("Helvetica", 11)

                draw_lines = draw_multiline_text(pdf, 50, y_position, f"Nombre: {article.name}")
                y_line += (20 * draw_lines)
                #print(y_line)

                draw_lines = draw_multiline_text(pdf, 50, (y_position - y_line), f"Código: {article.code}")
                #x_position_end = 50 + pdf.stringWidth(f"Código: {article.code}", "Helvetica", 12)

                # Generar y agregar el código de barras
                ruta_imagen = os.path.join(ruta_barcodes, f"barcode_{article.code}")
                ruta_imagen_png = ruta_imagen + ".png"
                generate_barcode(str(article.code), ruta_imagen)
                pdf.drawImage(ruta_imagen_png, x=420, y=(y_position - (y_line + 60)), width=100, height=100, preserveAspectRatio=True)
                y_line += (20 * draw_lines)

                #Se verifica si la descripcion no sobrepasa los limites del pdf
                num_lines = calculator_space_article(article.description)
                if ((y_position - (y_line + ((15 * (num_lines - 1)) + 20)) ) < 50):
                    next_page(pdf, page_number, date_time)
                    # siguiente página
                    y_position = 790
                    y_line = 50
                    page_number += 1

                draw_lines = draw_multiline_text(pdf, 50, (y_position - y_line), f"Descripción: {article.description}")
                y_line += (15 * (draw_lines - 1))
                y_line += 20

                # Se verifica si la fecha no sobrepasa los limites del pdf
                if(y_position - ( y_line + 15) < 50):
                    next_page(pdf, page_number, date_time)
                    # siguiente página
                    y_position = 790
                    y_line = 50
                    page_number += 1
                draw_lines = draw_multiline_text(pdf, 50, y_position - y_line,
                                                 f"Fecha de Creación: {article.creation_date}")
                y_line += (15 * draw_lines)

                # Se verifica si la imagenes no sobrepasan los limites del pdf
                #Se carga las imagenes de articulo
                if(y_position - (y_line + 70) < 50):
                    next_page(pdf, page_number, date_time)
                    # siguiente página
                    y_position = 790
                    y_line = 50
                    page_number += 1

                if (article.photo):
                    photos_article = article.photo.split(",")

                    eje_x = 100
                    y_line = y_line + 65
                    for photo_article in photos_article:

                    # Intentamos cargar la imagen desde una ruta específica
                        image_path = f"files/images_article/{photo_article}"
                        try:
                            image = ImageReader(image_path)
                            pdf.drawImage(image, x=eje_x, y=y_position - y_line, width=70, height=70,
                                          preserveAspectRatio=True)
                            eje_x = eje_x + 100
                        except Exception as e:
                         print(f"No se pudo cargar la imagen para el artículo {article.name}: {e}")

                    y_line = y_line + 5

                # Separador entre cada artículo
                pdf.line(50, y_position - y_line, 550, y_position - y_line)
                y_line += 15

                #elimina el codigo de barra generado
                os.remove(ruta_imagen_png)

                # Verificamos si hay espacio suficiente en la página actual
                if (y_position - y_line <= 100 and i < len(articles)):
                    next_page(pdf, page_number, date_time)
                    # siguiente página
                    y_position = 790
                    y_line = 50
                    page_number += 1


            pdf.setFont("Helvetica", 8)
            pdf.drawRightString(550, 30, f"Página {page_number}")
            pdf.drawString(50, 30, f"{date_time}")

            pdf.save()

        # Devolver el archivo PDF al cliente
        return FileResponse(ruta_temporal, filename=f"catalogo_{company.name.upper()}.pdf", media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el catálogo de {company.name}: {e}")

# no se ocupa
@router.get("/report/article/test/{id_company}")
def articles_catalog_2(id_company: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    try:
        name_user, expiration_time = current_user_info
        # Se valida la expiracion del token
        if expiration_time is None:
            return Response(code="401", message="token-exp", result=[])

        db = next(conexion(db, id_company))
        if db is None:
            return Response(code="404", result=[], message="BD no encontrada").model_dump()

        # Lógica para obtener los detalles de los artículos
        articles, count = get_article_by_id_company(db, id_company, adjust_limit=True)
        company = get_company_by_id(db, id_company)

        # while len(articles) < 10:
        #     articles.extend(copy.deepcopy(articles))

        #Fecha y hora
        chile_timezone = pytz.timezone('Chile/Continental')
        now = datetime.now(chile_timezone)
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")

        # Lógica para generar el catálogo PDF con ReportLab
        ruta_temporal = os.path.abspath("Generations_files/catalogo_reportlab.pdf")
        os.makedirs(os.path.dirname(ruta_temporal), exist_ok=True)

        ruta_barcodes = os.path.abspath("bar_codes")
        os.makedirs(ruta_barcodes, exist_ok=True)

        with (open(ruta_temporal, 'wb') as f):
            pdf = canvas.Canvas(f, pagesize=letter)

            width, height = pdf._pagesize
            print(f"Ancho del PDF: {width}, Alto del PDF: {height}")

            #Portada
            portada_catalogo(pdf,company)

            pdf.setTitle(f"Catálogo de Artículos des {company.name.upper()}")
            pdf.showPage()

            # Agregamos el título al PDF
            pdf.setFont("Helvetica", 16)
            pdf.drawCentredString(300, 750, f"Catálogo de Artículos de {company.name.upper()}")

            y_position = 770
            page_number = 1

            # Iteramos sobre los artículos y los agregamos al PDF
            y_line = 90
            for i, article in enumerate(articles, start=1):
                y_position -= y_line
                y_position_img = y_position #posicion eje y para img
                y_line = 0

                pdf.setFont("Helvetica", 12)

                draw_lines = draw_multiline_text(pdf, 260, y_position, f"Nombre: {article.name}")
                y_line += (20 * draw_lines)

                draw_lines = draw_multiline_text(pdf, 260, (y_position - y_line), f"Código: {article.code}")
                y_line += (20 * draw_lines)

                draw_lines = draw_multiline_text(pdf, 260, (y_position - y_line), f"Descripción: {article.description}")
                y_line += (20 * draw_lines)
                draw_lines = draw_multiline_text(pdf, 260, y_position - y_line, f"Fecha de Creación: {article.creation_date}")
                y_line += (15 * draw_lines)

                # Generar y agregar el código de barras
                ruta_imagen = os.path.join(ruta_barcodes, f"barcode_{article.code}")
                ruta_imagen_png = ruta_imagen + ".png"
                generate_barcode(str(article.code), ruta_imagen)
                pdf.drawImage(ruta_imagen_png, x=280, y=y_position - (y_line + 80 ), width=100, height=100, preserveAspectRatio=True)

                #Se carga las imagenes de articulo
                y_line = y_line + 65
                if (len(article.photo) > 0):
                    photos_article = article.photo.split(",")

                    y_position_img = y_position_img - 65
                    eje_x = 70
                    num_photos = 1
                    for photo_article in photos_article:
                        # Intentamos cargar la imagen desde una ruta específica x=400  y = y_position - (y_line - 10)
                        image_path = f"files/images_article/{photo_article}"
                        try:
                            image = ImageReader(image_path)
                            pdf.drawImage(image, x=eje_x, y=y_position_img, width=70, height=70,
                                          preserveAspectRatio=True)
                            eje_x = eje_x + 80
                            num_photos+= 1
                            if(num_photos == 3):
                                eje_x = 70
                                y_position_img = y_position_img - 75

                        except Exception as e:
                            print(f"No se pudo cargar la imagen para el artículo {article.name}: {e}")

                y_line = y_line + 10


                # Agregamos un separador entre cada artículo
                pdf.line(50, y_position - y_line, 550, y_position - y_line)
                y_line += 20

                #elimina el codigo de barra generado
                os.remove(ruta_imagen_png)

                # Verificamos si hay espacio suficiente en la página actual
                if y_position - y_line <= 180 and i < len(articles):
                    pdf.setFont("Helvetica", 8)
                    #numero pagina
                    pdf.drawRightString(550, 30, f"Página {page_number}")

                    #Fexha y hora
                    pdf.drawString(50, 30, f"{date_time}")

                    pdf.showPage()
                    # siguiente página
                    y_position = 870
                    page_number += 1


            pdf.setFont("Helvetica", 8)
            pdf.drawRightString(550, 30, f"Página {page_number}")
            pdf.drawString(50, 30, f"{date_time}")

            pdf.save()

        # Devolver el archivo PDF al cliente
        return FileResponse(ruta_temporal, filename=f"catalogo_{company.name.upper()}.pdf", media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el catálogo de {company.name}: {e}")

@router.get("/report/active/sucursal/{id_sucursal}")
def actives_catalog_sucursal(id_sucursal: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    try:
        name_user, expiration_time = current_user_info
        # Se valida la expiracion del token
        if expiration_time is None:
            return Response(code="401", message="token-exp", result=[])

        db = next(conexion(db, companyId))
        if db is None:
            return Response(code="404", result=[], message="BD no encontrada").model_dump()

        # Lógica para obtener los detalles de los artículos (por ejemplo, desde una base de datos)
        actives, count = get_active_by_sucursal(db, id_sucursal, adjust_limit=True)
        sucursal = actives[0].office.sucursal
        company = actives[0].office.sucursal.company

        #Fecha y hora
        chile_timezone = pytz.timezone('Chile/Continental')
        now = datetime.now(chile_timezone)
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")


        # Lógica para generar el catálogo PDF con ReportLab
        ruta_temporal = os.path.abspath("Generations_files/catalogo_reportlab.pdf")
        os.makedirs(os.path.dirname(ruta_temporal), exist_ok=True)

        custom_page_size = (816, 1056)

        with (open(ruta_temporal, 'wb') as f):
            pdf = canvas.Canvas(f, pagesize=custom_page_size)

            width, height = pdf._pagesize
            #print(f"Ancho del PDF: {width}, Alto del PDF: {height}")

            pdf.setTitle(f"Catálogo de Activos de {company.name.upper()}")

            # Dibujar un rectángulo
            ancho_rect = width - 100
            alto_rect = 100
            eje_y = height - (alto_rect + 16)
            pdf.setLineWidth(1.5)
            pdf.rect(50, eje_y, ancho_rect, alto_rect)

            # Agregamos el título al PDF
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(70, eje_y + 75, f"Catálogo de activos")

            pdf.setFont("Helvetica", 12)
            pdf.drawString(70, eje_y + 55, f"Cliente")
            pdf.drawString(145, eje_y + 55, f"{company.name.upper()}")

            pdf.drawString(70, eje_y + 35, f"Sucursal")
            pdf.drawString(145, eje_y + 35, f"{sucursal.number}    {sucursal.description}")

            image_path = "images-sca/sca-2.jpeg"
            try:
                image = ImageReader(image_path)
                pdf.drawImage(image, x=606, y=eje_y - 10, width=140, height=140, preserveAspectRatio=True)
            except Exception as e:
                print(f"No se pudo cargar la imagen para la portada: {e}")

            # Crear y configurar la tabla
            table_data = [["Cod. activo","Marca", "Modelo", "Serie", "F. Adquisición", "N. de registro","Estado", "Encargado", "Rut encargado", "Cod. articulo", "Oficina"]]

            #y_position = 700
            page_number = 1
            cant_items = 0
            # Iteramos sobre los artículos y los agregamos al PDF
            eje_y_table = eje_y - 40
            for i, active in enumerate(actives, start=1):

                if ((eje_y_table - (20 * len(table_data))) < 80 and i < len(actives)):
                    if (page_number == 1):
                        draw_table(pdf, table_data, eje_y_table)
                    else:
                        draw_table(pdf, table_data, eje_y)
                    cant_items = i
                    pdf.setFont("Helvetica", 8)
                    pdf.drawRightString(755, 30, f"Página {page_number}")
                    pdf.drawString(25, 30, f"{date_time}")
                    pdf.showPage()
                    table_data = [table_data[0]]
                    page_number += 1
                    eje_y_table = height - 100

                table_data.append([
                    active.bar_code,
                    active.brand,
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

            draw_table(pdf, table_data, eje_y_table, 35)

            pdf.setFont("Helvetica", 8)
            pdf.drawRightString(755, 30, f"Página {page_number}")
            pdf.drawString(25, 30, f"{date_time}")

            pdf.save()

        # Devolver el archivo PDF al cliente
        return FileResponse(ruta_temporal, filename=f"catalogo_{company.name.upper()}.pdf", media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el catálogo de {company.name}: {e}")

@router.get("/report/active/offices/{id_offices}")
def actives_catalog_office(id_offices: str , db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    try:
        name_user, expiration_time = current_user_info
        # Se valida la expiracion del token
        if expiration_time is None:
            return Response(code="401", message="token-exp", result=[])

        db = next(conexion(db, companyId))
        if db is None:
            return Response(code="404", result=[], message="BD no encontrada").model_dump()

        # Lógica para obtener los detalles de los artículos (por ejemplo, desde una base de datos)
        id_offices_list = id_offices.split(",")
        id_offices_int = [int(id_office) for id_office in id_offices_list]
        #print(len(id_offices_int))
        actives, count = get_active_by_offices(db, id_offices_int, adjust_limit=True)
        sucursal = actives[0].office.sucursal
        company = actives[0].office.sucursal.company

        #Creando mas datos para test
        # while len(actives) < 80:
        #     actives.extend(copy.deepcopy(actives))

        #Fecha y hora
        chile_timezone = pytz.timezone('Chile/Continental')
        now = datetime.now(chile_timezone)
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")


        # Lógica para generar el catálogo PDF con ReportLab
        ruta_temporal = os.path.abspath("Generations_files/catalogo_reportlab.pdf")
        os.makedirs(os.path.dirname(ruta_temporal), exist_ok=True)

        custom_page_size = (816, 1056)

        with open(ruta_temporal, 'wb') as f:
            pdf = canvas.Canvas(f, pagesize=custom_page_size)

            width, height = pdf._pagesize
            #print(f"Ancho del PDF: {width}, Alto del PDF: {height}")

            pdf.setTitle(f"Catálogo de Activos de {company.name.upper()}")

            # Dibujar un rectángulo
            ancho_rect = width - 100
            alto_rect = 100
            eje_y = height - (alto_rect + 16)
            pdf.setLineWidth(1.5)
            pdf.rect(50, eje_y, ancho_rect, alto_rect)

            # Agregamos el título al PDF
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(70, eje_y + 75, f"Catálogo de activos")

            pdf.setFont("Helvetica", 12)
            pdf.drawString(70, eje_y + 55, f"Cliente")
            pdf.drawString(145, eje_y + 55, f"{company.name.upper()}")

            pdf.drawString(70, eje_y + 35, f"Sucursal")
            pdf.drawString(145, eje_y + 35, f"{sucursal.number}    {sucursal.description}")

            image_path = "images-sca/sca-2.jpeg"
            try:
                image = ImageReader(image_path)
                pdf.drawImage(image, x=606, y=eje_y - 10, width=140, height=140, preserveAspectRatio=True)
            except Exception as e:
                print(f"No se pudo cargar la imagen para la portada: {e}")

            # Crear y configurar la tabla
            table_data = [["Cod. activo", "Marca", "Modelo", "Serie", "F. Adquisición", "N. de registro", "Estado",
                           "Encargado", "Rut encargado", "Cod. articulo", "Oficina"]]

            page_number = 1
            cant_items = 0
            # Iteramos sobre los artículos y los agregamos al PDF
            eje_y_table = eje_y - 40
            for i, active in enumerate(actives, start=1):

                if ((eje_y_table - (20 * len(table_data))) < 80 and i < len(actives)):
                    if (page_number == 1):
                        draw_table(pdf, table_data, eje_y_table)
                    else:
                        draw_table(pdf, table_data, eje_y)
                    cant_items = i
                    pdf.setFont("Helvetica", 8)
                    pdf.drawRightString(755, 30, f"Página {page_number}")
                    pdf.drawString(25, 30, f"{date_time}")
                    pdf.showPage()
                    table_data = [table_data[0]]
                    page_number += 1
                    eje_y_table = height - 100

                table_data.append([
                    active.bar_code,
                    active.brand,
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

            draw_table(pdf, table_data, eje_y_table, 35)

            pdf.setFont("Helvetica", 8)
            pdf.drawRightString(755, 30, f"Página {page_number}")
            pdf.drawString(25, 30, f"{date_time}")

            pdf.save()

        # Devolver el archivo PDF al cliente
        return FileResponse(ruta_temporal, filename=f"catalogo_{company.name.upper()}.pdf", media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el catálogo de {company.name}: {e}")

@router.get("/report/excel/active/sucursal/{id_sucursal}")
def actives_catalog_sucursal_excel(id_sucursal: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    try:
        name_user, expiration_time = current_user_info
        # Se valida la expiracion del token
        if expiration_time is None:
            return Response(code="401", message="token-exp", result=[])

        db = next(conexion(db, companyId))
        if db is None:
            return Response(code="404", result=[], message="BD no encontrada").model_dump()

        # Lógica para obtener los detalles de los artículos
        actives, count = get_active_by_sucursal(db, id_sucursal, adjust_limit=True)
        sucursal = actives[0].office.sucursal
        company = actives[0].office.sucursal.company

        chile_timezone = pytz.timezone('Chile/Continental')
        now = datetime.now(chile_timezone)
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")

        # Lógica para generar el catálogo Excel
        excel_filename = f'catalogo_{company.name.upper()}.xlsx'
        excel_path = os.path.join('Generations_files', excel_filename)

        # Crear un libro de trabajo y una hoja de trabajo
        workbook = xlsxwriter.Workbook(excel_path)
        worksheet = workbook.add_worksheet()

        # Configurar la ruta de la imagen
        imagen_path = "images-sca/sca-2.jpeg"
        factor_x = 0.3
        factor_y = 0.3

        try:
            # Insertar la imagen en la hoja de trabajo
            worksheet.insert_image('G2', imagen_path, {'x_offset': 15, 'y_offset': 10, 'x_scale': factor_x, 'y_scale': factor_y})
        except Exception as e:
            print(f"No se pudo cargar la imagen para la portada: {e}")

        #ancho por defecto de las filas
        worksheet.set_default_row(18)

        # Configurar un formato para el título con la fuente Helvetica
        formato_titulo = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_name': 'Helvetica',
            'font_size': 18,
        })

        worksheet.set_row(1, 25)
        # Escribir el título en una celda específica
        worksheet.merge_range('B2:E2', ' Catálogo de activos ', formato_titulo)

        formato_sub_titulo = workbook.add_format({
            'align': 'left',
            'indent': 1,
            'valign': 'vcenter',
            'font_name': 'Helvetica',
            'font_size': 13,
        })

        formato_sub_titulo_2 = workbook.add_format({
            'align': 'right',
            'indent': 1,
            'valign': 'vcenter',
            'font_name': 'Helvetica',
            'font_size': 13,
        })

        #worksheet.write('C3', 'Cliente', formato_sub_titulo)
        worksheet.merge_range('B3:C3', 'Cliente', formato_sub_titulo_2)
        worksheet.merge_range('D3:E3', f'{company.name.upper()}', formato_sub_titulo)
        worksheet.merge_range('B4:C4', 'Sucursal', formato_sub_titulo_2)
        worksheet.merge_range('D4:E4', f'{sucursal.number}   {sucursal.description}', formato_sub_titulo)
        worksheet.merge_range('B5:C5', 'Fecha', formato_sub_titulo_2)
        worksheet.merge_range('D5:E5', f'{date_time}', formato_sub_titulo)

        # Datos a escribir en el archivo Excel
        datos = ["Cod. activo", "Marca", "Modelo", "Serie", "Fecha adquisición", "Num. de registro", "Estado", "Encargado", "Rut encargado", "Cod. articulo", "Oficina"]

        start_table = 7

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

        # Configurar un formato para los datos
        formato_datos = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'font_name': 'Helvetica',
            'font_size': 9
        })

        # Escribir los datos en el resto de las filas
        width_column = [0] * len(datos)
        for index, value in enumerate(datos):
            width_column[index] = len(value)

        # Escribir los datos desde la base de datos en el resto de las filas
        for row, active in enumerate(actives, start=1):
            for col, value in enumerate([active.bar_code, active.brand, active.model, active.serie, str(active.acquisition_date),
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
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/report/excel/active/offices/{id_offices}")
def actives_catalog_office_excel(id_offices: str , db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    try:
        name_user, expiration_time = current_user_info
        # Se valida la expiracion del token
        if expiration_time is None:
            return Response(code="401", message="token-exp", result=[])

        db = next(conexion(db, companyId))
        if db is None:
            return Response(code="404", result=[], message="BD no encontrada").model_dump()

        # Lógica para obtener los detalles de los artículos (por ejemplo, desde una base de datos)
        id_offices_list = id_offices.split(",")
        id_offices_int = [int(id_office) for id_office in id_offices_list]
        actives, count = get_active_by_offices(db, id_offices_int, adjust_limit=True)
        sucursal = actives[0].office.sucursal
        company = actives[0].office.sucursal.company

        chile_timezone = pytz.timezone('Chile/Continental')
        now = datetime.now(chile_timezone)
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")

        # Lógica para generar el catálogo Excel
        excel_filename = f'catalogo_{company.name.upper()}.xlsx'
        excel_path = os.path.join('Generations_files', excel_filename)

        # Crear un libro de trabajo y una hoja de trabajo
        workbook = xlsxwriter.Workbook(excel_path)
        worksheet = workbook.add_worksheet()

        # Configurar la ruta de la imagen
        imagen_path = "images-sca/sca-2.jpeg"
        factor_x = 0.3
        factor_y = 0.3

        try:
            # Insertar la imagen en la hoja de trabajo
            worksheet.insert_image('G2', imagen_path, {'x_offset': 15, 'y_offset': 10, 'x_scale': factor_x, 'y_scale': factor_y})
        except Exception as e:
            print(f"No se pudo cargar la imagen para la portada: {e}")

        #ancho por defecto de las filas
        worksheet.set_default_row(18)

        # Configurar un formato para el título con la fuente Helvetica
        formato_titulo = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_name': 'Helvetica',
            'font_size': 18,
        })

        worksheet.set_row(1, 25)
        # Escribir el título en una celda específica
        worksheet.merge_range('B2:E2', ' Catálogo de activos ', formato_titulo)

        formato_sub_titulo = workbook.add_format({
            'align': 'left',
            'indent': 1,
            'valign': 'vcenter',
            'font_name': 'Helvetica',
            'font_size': 13,
        })

        formato_sub_titulo_2 = workbook.add_format({
            'align': 'right',
            'indent': 1,
            'valign': 'vcenter',
            'font_name': 'Helvetica',
            'font_size': 13,
        })

        worksheet.merge_range('B3:C3', 'Cliente', formato_sub_titulo_2)
        worksheet.merge_range('D3:E3', f'{company.name.upper()}', formato_sub_titulo)
        worksheet.merge_range('B4:C4', 'Sucursal', formato_sub_titulo_2)
        worksheet.merge_range('D4:E4', f'{sucursal.number}   {sucursal.description}', formato_sub_titulo)
        worksheet.merge_range('B5:C5', 'Fecha', formato_sub_titulo_2)
        worksheet.merge_range('D5:E5', f'{date_time}', formato_sub_titulo)

        # Datos a escribir en el archivo Excel
        datos = ["Cod. activo", "Marca", "Modelo", "Serie", "Fecha adquisición", "Num. de registro", "Estado", "Encargado", "Rut encargado", "Cod. articulo", "Oficina"]

        start_table = 7

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

        # Configurar un formato para los datos
        formato_datos = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'font_name': 'Helvetica',
            'font_size': 9
        })

        # Escribir los datos en el resto de las filas
        width_column = [0] * len(datos)
        for index, value in enumerate(datos):
            width_column[index] = len(value)

        # Escribir los datos desde la base de datos en el resto de las filas
        for row, active in enumerate(actives, start=1):
            for col, value in enumerate([active.bar_code, active.brand, active.model, active.serie, str(active.acquisition_date),
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
        raise HTTPException(status_code=500, detail=str(e))