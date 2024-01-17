import textwrap

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

