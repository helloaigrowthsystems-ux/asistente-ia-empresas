from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def crear_factura():
    c = canvas.Canvas("factura_prueba.pdf", pagesize=A4)

    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, 800, "FACTURA")

    c.setFont("Helvetica", 12)
    c.drawString(50, 770, "Número de factura: FAC-2024-001")
    c.drawString(50, 750, "Fecha: 14/03/2026")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 710, "PROVEEDOR:")
    c.setFont("Helvetica", 12)
    c.drawString(50, 690, "Empresa Tech Solutions S.L.")
    c.drawString(50, 670, "CIF: B-12345678")
    c.drawString(50, 650, "Calle Mayor 123, Madrid")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 610, "CLIENTE:")
    c.setFont("Helvetica", 12)
    c.drawString(50, 590, "Empresa Cliente S.A.")
    c.drawString(50, 570, "CIF: A-87654321")
    c.drawString(50, 550, "Avenida Central 456, Barcelona")

    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, 510, "CONCEPTO")
    c.drawString(300, 510, "CANTIDAD")
    c.drawString(400, 510, "PRECIO")
    c.drawString(480, 510, "TOTAL")

    c.setFont("Helvetica", 11)
    c.drawString(50, 490, "Desarrollo web")
    c.drawString(300, 490, "1")
    c.drawString(400, 490, "1.500,00 EUR")
    c.drawString(480, 490, "1.500,00 EUR")

    c.drawString(50, 470, "Mantenimiento mensual")
    c.drawString(300, 470, "3")
    c.drawString(400, 470, "200,00 EUR")
    c.drawString(480, 470, "600,00 EUR")

    c.drawString(50, 450, "Consultoría IA")
    c.drawString(300, 450, "2")
    c.drawString(400, 450, "750,00 EUR")
    c.drawString(480, 450, "1.500,00 EUR")

    c.line(50, 435, 550, 435)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(350, 415, "Base imponible:")
    c.drawString(480, 415, "3.600,00 EUR")
    c.drawString(350, 395, "IVA (21%):")
    c.drawString(480, 395, "756,00 EUR")
    c.drawString(350, 375, "TOTAL FACTURA:")
    c.drawString(480, 375, "4.356,00 EUR")

    c.save()
    print("✅ Factura creada: factura_prueba.pdf")


crear_factura()