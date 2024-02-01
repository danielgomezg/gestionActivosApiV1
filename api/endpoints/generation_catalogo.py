from fastapi import Depends, File, HTTPException
from fastapi.responses import FileResponse
from fastapi import APIRouter
from typing import Tuple
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
#from jinja2 import Template
from schemas.schemaGenerico import Response
from sqlalchemy.orm import Session
from database import get_db
from crud.user import get_user_disable_current
import os
from datetime import datetime

from crud.generation_catalogo import draw_multiline_text, portada_catalogo, generate_barcode, draw_table
from crud.article import get_article_by_id_company
from crud.company import get_company_by_id, get_company_by_sucursal
from crud.active import get_active_by_sucursal, get_active_by_offices

import copy

router = APIRouter()

@router.get("/report/article/{id_company}")
def articles_catalog(id_company: int, db: Session = Depends(get_db), current_user_info: Tuple[int, str] = Depends(get_user_disable_current)):
    try:
        id_user, expiration_time = current_user_info
        # Se valida la expiracion del token
        if expiration_time is None:
            return Response(code="401", message="token-exp", result=[])

        # Lógica para obtener los detalles de los artículos (por ejemplo, desde una base de datos)
        articles = get_article_by_id_company(db, id_company)
        company = get_company_by_id(db, id_company)

        #Fecha y hora
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")


        # Lógica para generar el catálogo PDF con ReportLab
        ruta_temporal = os.path.abspath("Generations_files/catalogo_reportlab.pdf")
        os.makedirs(os.path.dirname(ruta_temporal), exist_ok=True)

        ruta_barcodes = os.path.abspath("bar_codes")
        os.makedirs(ruta_barcodes, exist_ok=True)

        with open(ruta_temporal, 'wb') as f:
            pdf = canvas.Canvas(f, pagesize=letter)

            #Portada
            portada_catalogo(pdf,company)

            pdf.setTitle(f"Catálogo de Artículos de {company.name}")
            pdf.showPage()

            # Agregamos el título al PDF
            pdf.setFont("Helvetica", 16)
            pdf.drawCentredString(300, 750, f"Catálogo de Artículos de {company.name}")

            y_position = 720
            page_number = 1

            # Iteramos sobre los artículos y los agregamos al PDF
            y_line = 90
            for i, article in enumerate(articles, start=1):
                y_position -= y_line
                y_line = 0

                pdf.setFont("Helvetica", 12)

                draw_lines = draw_multiline_text(pdf, 50, y_position, f"Nombre: {article.name}")
                y_line += (20 * draw_lines)

                draw_lines = draw_multiline_text(pdf, 50, (y_position - y_line), f"Código: {article.id}")
                # Generar y agregar el código de barras
                ruta_imagen = os.path.join(ruta_barcodes, f"barcode_{article.id}")
                ruta_imagen_png = ruta_imagen + ".png"
                generate_barcode(str(article.id), ruta_imagen)
                pdf.drawImage(ruta_imagen_png, x=120, y=(y_position - (y_line + 15)), width=40, height=40, preserveAspectRatio=True)
                y_line += (20 * draw_lines)

                draw_lines = draw_multiline_text(pdf, 50, (y_position - y_line), f"Descripción: {article.description}")
                y_line += (20 * draw_lines)

                draw_lines = draw_multiline_text(pdf, 50, y_position - y_line, f"Fecha de Creación: {article.creation_date}")
                y_line += (15 * draw_lines)

                # Intentamos cargar la imagen desde una ruta específica
                image_path = f"files/images_article/{article.photo}"
                try:
                    image = ImageReader(image_path)
                    pdf.drawImage(image, x=400, y=y_position - (y_line - 10), width=70, height=70, preserveAspectRatio=True)
                except Exception as e:
                    print(f"No se pudo cargar la imagen para el artículo {article.name}: {e}")

                # Agregamos un separador entre cada artículo
                pdf.line(50, y_position - y_line, 550, y_position - y_line)
                y_line += 15

                #elimina el codigo de barra generado
                os.remove(ruta_imagen_png)

                # Verificamos si hay espacio suficiente en la página actual
                if y_position - y_line <= 100 and i < len(articles):
                    pdf.setFont("Helvetica", 8)
                    #numero pagina
                    pdf.drawRightString(550, 30, f"Página {page_number}")

                    #Fexha y hora
                    pdf.drawString(50, 30, f"{date_time}")

                    pdf.showPage()
                    # siguiente página
                    y_position = 800
                    page_number += 1


            pdf.setFont("Helvetica", 8)
            pdf.drawRightString(550, 30, f"Página {page_number}")
            pdf.drawString(50, 30, f"{date_time}")

            pdf.save()

        # Devolver el archivo PDF al cliente
        return FileResponse(ruta_temporal, filename=f"catalogo_{company.name}.pdf", media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el catálogo de {company.name}: {e}")


@router.get("/report/active/sucursal/{id_sucursal}")
def actives_catalog_sucursal(id_sucursal: int, db: Session = Depends(get_db), current_user_info: Tuple[int, str] = Depends(get_user_disable_current)):
    try:
        id_user, expiration_time = current_user_info
        # Se valida la expiracion del token
        if expiration_time is None:
            return Response(code="401", message="token-exp", result=[])

        # Lógica para obtener los detalles de los artículos (por ejemplo, desde una base de datos)
        actives, count = get_active_by_sucursal(db, id_sucursal)
        sucursal = actives[0].office.sucursal
        company = actives[0].office.sucursal.company
        print(sucursal.number)
        print(company.name)
        #result = get_company_by_sucursal(db, id_sucursal)
        #company = result[0]

        #while len(actives) < 40:
            #actives.extend(copy.deepcopy(actives))

        #print(actives[0].office.sucursal.description)
        #Fecha y hora
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")


        # Lógica para generar el catálogo PDF con ReportLab
        ruta_temporal = os.path.abspath("Generations_files/catalogo_reportlab.pdf")
        os.makedirs(os.path.dirname(ruta_temporal), exist_ok=True)

        custom_page_size = (816, 1056)

        with (open(ruta_temporal, 'wb') as f):
            pdf = canvas.Canvas(f, pagesize=custom_page_size)

            width, height = pdf._pagesize
            print(f"Ancho del PDF: {width}, Alto del PDF: {height}")

            pdf.setTitle(f"Catálogo de Activos de {company.name}")

            # Dibujar un rectángulo
            ancho_rect = width - 100
            alto_rect = 100
            eje_y = height - (alto_rect + 16)
            pdf.setLineWidth(1.5)
            #pdf.rect(50, 500, 692, 100)
            pdf.rect(50, eje_y, ancho_rect, alto_rect)

            # Agregamos el título al PDF
            pdf.setFont("Helvetica-Bold", 16)
            #pdf.drawString(70, 575, f"Catálogo de activos")
            pdf.drawString(70, eje_y + 75, f"Catálogo de activos")

            pdf.setFont("Helvetica", 12)
            #pdf.drawString(70, 555, f"Cliente")
            #pdf.drawString(145, 555, f"{company.name}")
            pdf.drawString(70, eje_y + 55, f"Cliente")
            pdf.drawString(145, eje_y + 55, f"{company.name}")

            pdf.drawString(70, eje_y + 35, f"Sucursal")
            pdf.drawString(145, eje_y + 35, f"{sucursal.number}    {sucursal.description}")
            #pdf.drawString(70, 710, f"Sucursal")
            #pdf.drawString(145, 710, f"{sucursal.number}    {sucursal.description}")

            image_path = "images-sca/sca-2.jpeg"
            try:
                image = ImageReader(image_path)
                #pdf.drawImage(image, x=582, y=490, width=140, height=140, preserveAspectRatio=True)
                pdf.drawImage(image, x=606, y=eje_y - 10, width=140, height=140, preserveAspectRatio=True)
            except Exception as e:
                print(f"No se pudo cargar la imagen para la portada: {e}")

            # Crear y configurar la tabla
            table_data = [["Cod. de barra","Modelo", "Serie", "Fecha adquisición", "Num. de registro","Estado", "Encargado", "Rut encargado", "Cod. articulo", "Oficina"]]

            #y_position = 700
            page_number = 1
            cant_items = 0
            # Iteramos sobre los artículos y los agregamos al PDF
            #y_line = 90
            eje_y_table = eje_y - 40
            for i, active in enumerate(actives, start=1):
                if (active.state == "new"):
                    state_active = "nuevo"
                elif(active.state == "damage"):
                    state_active = "dañado"
                else:
                    state_active = active.state

                if ((eje_y_table - (20 * len(table_data))) < 120 and i < len(actives)):
                    if (page_number == 1):
                        draw_table(pdf, table_data, eje_y_table, i)
                    else:
                        draw_table(pdf, table_data, eje_y, i - cant_items)
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
                    active.model,
                    active.serie,
                    str(active.acquisition_date),
                    active.accounting_record_number,
                    state_active,
                    active.name_in_charge_active,
                    active.rut_in_charge_active,
                    active.article_id,
                    str(active.office.floor) + " - " + active.office.description
                ])


            print(i)
            draw_table(pdf, table_data, eje_y_table, i - cant_items)
            #table_style = TableStyle([
                #('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                #('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
             #   ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
              #  ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
              #  ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
             #   ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                #('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
             #   ('FONTSIZE', (0, 0), (-1, 0), 11),
             #   ('FONTSIZE', (0, 1), (-1, -1), 9),
             #   ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.black),
           #
            #table = Table(table_data)
            #table.setStyle(table_style)

            # Posicionar la tabla en el PDF
            #eje_y_table = eje_y - 60
            #table.wrapOn(pdf, 0, 0)
            #table.drawOn(pdf, 30, eje_y_table - (i*20))

            pdf.setFont("Helvetica", 8)
            pdf.drawRightString(755, 30, f"Página {page_number}")
            pdf.drawString(25, 30, f"{date_time}")

            pdf.save()

        # Devolver el archivo PDF al cliente
        return FileResponse(ruta_temporal, filename=f"catalogo_{company.name}.pdf", media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el catálogo de {company.name}: {e}")

@router.get("/report/active/offices/{id_offices}")
def actives_catalog_office(id_offices: str , db: Session = Depends(get_db), current_user_info: Tuple[int, str] = Depends(get_user_disable_current)):
    try:
        id_user, expiration_time = current_user_info
        # Se valida la expiracion del token
        if expiration_time is None:
            return Response(code="401", message="token-exp", result=[])

        # Lógica para obtener los detalles de los artículos (por ejemplo, desde una base de datos)
        id_offices_list = id_offices.split(",")
        id_offices_int = [int(id_office) for id_office in id_offices_list]
        print(len(id_offices_int))
        actives, count = get_active_by_offices(db, id_offices_int)
        sucursal = actives[0].office.sucursal
        company = actives[0].office.sucursal.company

        while len(actives) < 80:
            actives.extend(copy.deepcopy(actives))

        #Fecha y hora
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")


        # Lógica para generar el catálogo PDF con ReportLab
        ruta_temporal = os.path.abspath("Generations_files/catalogo_reportlab.pdf")
        os.makedirs(os.path.dirname(ruta_temporal), exist_ok=True)

        custom_page_size = (816, 1056)

        with open(ruta_temporal, 'wb') as f:
            #pdf = canvas.Canvas(f, pagesize=landscape(letter))
            pdf = canvas.Canvas(f, pagesize=custom_page_size)

            width, height = pdf._pagesize
            print(f"Ancho del PDF: {width}, Alto del PDF: {height}")

            pdf.setTitle(f"Catálogo de Activos de {company.name}")

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
            pdf.drawString(145, eje_y + 55, f"{company.name}")

            pdf.drawString(70, eje_y + 35, f"Sucursal")
            pdf.drawString(145, eje_y + 35, f"{sucursal.number}    {sucursal.description}")

            image_path = "images-sca/sca-2.jpeg"
            try:
                image = ImageReader(image_path)
                pdf.drawImage(image, x=606, y=eje_y - 10, width=140, height=140, preserveAspectRatio=True)
            except Exception as e:
                print(f"No se pudo cargar la imagen para la portada: {e}")

            # Crear y configurar la tabla
            table_data = [["Cod. de barra", "Modelo", "Serie", "Fecha adquisición", "Num. de registro", "Estado",
                           "Encargado", "Rut encargado", "Cod. articulo", "Oficina"]]

            # y_position = 700
            page_number = 1
            cant_items = 0
            # Iteramos sobre los artículos y los agregamos al PDF
            # y_line = 90
            eje_y_table = eje_y - 40
            #pdf.drawString(70, eje_y_table, f"Comienzo")
            for i, active in enumerate(actives, start=1):
                if (active.state == "new"):
                    state_active = "nuevo"
                elif (active.state == "damage"):
                    state_active = "dañado"
                else:
                    state_active = active.state

                if ((eje_y_table - (20 * len(table_data))) < 120 and i < len(actives)):
                    if (page_number == 1):
                        draw_table(pdf, table_data, eje_y_table, i)
                    else:
                        draw_table(pdf, table_data, eje_y, i - cant_items)
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
                    active.model,
                    active.serie,
                    str(active.acquisition_date),
                    active.accounting_record_number,
                    state_active,
                    active.name_in_charge_active,
                    active.rut_in_charge_active,
                    active.article_id,
                    str(active.office.floor) + " - " + active.office.description
                ])

            #print(i)
            draw_table(pdf, table_data, eje_y_table, i - cant_items)

            pdf.setFont("Helvetica", 8)
            pdf.drawRightString(755, 30, f"Página {page_number}")
            pdf.drawString(25, 30, f"{date_time}")

            pdf.save()

        # Devolver el archivo PDF al cliente
        return FileResponse(ruta_temporal, filename=f"catalogo_{company.name}.pdf", media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el catálogo de {company.name}: {e}")
