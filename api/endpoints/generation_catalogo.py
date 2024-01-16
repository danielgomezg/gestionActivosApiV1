from fastapi import Depends, File, HTTPException
from fastapi.responses import FileResponse
from fastapi import APIRouter
from typing import Tuple
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from jinja2 import Template
from schemas.schemaGenerico import Response
from sqlalchemy.orm import Session
from database import get_db
from crud.user import get_user_disable_current
import os


from crud.article import get_article_by_id_company
from crud.company import get_company_by_id

router = APIRouter()

@router.get("/generation_catalogo/{id_company}")
async def generation_catalogo(id_company: int, db: Session = Depends(get_db), current_user_info: Tuple[int, str] = Depends(get_user_disable_current)):
    try:
        id_user, expiration_time = current_user_info
        # Se valida la expiracion del token
        if expiration_time is None:
            return Response(code="401", message="token-exp", result=[])

        # Lógica para obtener los detalles de los artículos (por ejemplo, desde una base de datos)
        articles = get_article_by_id_company(db, id_company)
        company = get_company_by_id(db, id_company)


        # Lógica para generar el catálogo PDF con ReportLab
        ruta_temporal = os.path.abspath("Generations_files/catalogo_reportlab.pdf")
        os.makedirs(os.path.dirname(ruta_temporal), exist_ok=True)

        # Creamos un archivo PDF con ReportLab
        with open(ruta_temporal, 'wb') as f:
            pdf = canvas.Canvas(f, pagesize=letter)

            pdf.setTitle(f"Catálogo de Artículos de {company.name}")

            # Agregamos el título al PDF
            pdf.setFont("Helvetica", 16)
            pdf.drawCentredString(300, 750, f"Catálogo de Artículos de {company.name}")

            y_position = 720
            page_number = 1

            # Iteramos sobre los artículos y los agregamos al PDF
            #for article in articles:
            for i, article in enumerate(articles, start=1):
                y_position -= 70

                pdf.setFont("Helvetica", 12)
                pdf.drawString(50, y_position, f"Nombre: {article.name}")
                pdf.drawString(50, y_position - 20, f"Descripción: {article.description}")
                pdf.drawString(50, y_position - 40, f"Fecha de Creación: {article.creation_date}")
                # Agregar más información según sea necesario

                # Intentamos cargar la imagen desde una ruta específica
                image_path = f"files/images_article/{article.photo}"
                try:
                    image = ImageReader(image_path)
                    pdf.drawImage(image, x=400, y=y_position - 45, width=55, height=55, preserveAspectRatio=True)
                except Exception as e:
                    print(f"No se pudo cargar la imagen para el artículo {article.name}: {e}")

                # Agregamos un separador entre cada artículo
                pdf.line(50, y_position - 55, 550, y_position - 50)

                # Verificamos si hay espacio suficiente en la página actual
                if y_position - 60 <= 50 and i < len(articles):
                    pdf.showPage()  # siguiente página
                    y_position = 720  # Reiniciamos la posición vertical
                    page_number += 1

            pdf.setFont("Helvetica", 8)
            pdf.drawRightString(550, 30, f"Página {page_number}")

            pdf.save()

        # Devolver el archivo PDF al cliente
        return FileResponse(ruta_temporal, filename=f"catalogo_{company.name}.pdf", media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el catálogo de {company.name}: {e}")
