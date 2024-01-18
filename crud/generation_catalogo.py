import textwrap
from reportlab.lib.utils import ImageReader
from barcode import Code128
from barcode.writer import ImageWriter

def draw_multiline_text(pdf, x, y_position, text):
    pdf.setFont("Helvetica", 12)
    if len(text) > 50:
        #pdf.drawString(50, y_position, text)
        lines = textwrap.wrap(text, width=50)
        i = 0
        for line in lines:
            pdf.drawString(x, y_position, line)
            y_position -= 20
            i+= 1
        return i
    else:
        pdf.drawString(x, y_position, text)
        return 1

def portada_catalogo(pdf, company):
    pdf.setFont("Helvetica-Bold", 32)
    pdf.drawCentredString(300, 450, f"{company.name}")

    # Intentamos cargar la imagen desde una ruta específica
    image_path = "images-sca/sca-1.jpeg"
    try:
        image = ImageReader(image_path)
        pdf.drawImage(image, x=100, y=400, width=400, height=400, preserveAspectRatio=True)
    except Exception as e:
        print(f"No se pudo cargar la imagen para la portada: {e}")

    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawCentredString(300, 400, "Catálogo de articulos")

def generate_barcode(value, filename):
    code = Code128(value, writer=ImageWriter())
    code.save(filename, options={'write_text': False, 'module_height': 8.0, 'module_width': 0.5})


