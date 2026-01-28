from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os

def create_base_pdf(filename):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4 # 595.27, 841.89
    
    # Draw simple boxes to representing the Org Chart structure
    # Box 1: CEO (Top Center)
    # x=220, y=720, w=160, h=45
    c.rect(220, 720, 160, 45)
    
    # Box 2: Asistente (Left-ish below)
    # x=120, y=650, w=140, h=40
    c.rect(120, 650, 140, 40)
    
    c.save()
    print(f"Created {filename}")

if __name__ == "__main__":
    output_path = os.path.join("input", "templates", "01_ORGANIGRAMA_CEO.pdf")
    create_base_pdf(output_path)
