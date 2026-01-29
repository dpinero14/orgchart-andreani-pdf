"""
Script unificado para actualizar PDFs de organigramas.

Uso:
    python update_pdf.py <pdf_path> <texto_a_buscar> <texto_de_reemplazo>

Ejemplo:
    python update_pdf.py "input/mi_organigrama.pdf" "Lucas Capuano" "Diego Piñero"
"""

import sys
import os
import json
import io
import pdfplumber
import pikepdf
import textwrap
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def find_text_coordinates(pdf_path, search_text):
    """Encuentra las coordenadas de un texto en el PDF."""
    print(f"Buscando '{search_text}' en {pdf_path}...")
    
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        height = page.height
        
        matches = page.search(search_text)
        
        if not matches:
            print(f"❌ No se encontró '{search_text}' en el PDF")
            return None
        
        match = matches[0]
        print(f"✓ Texto encontrado en coordenadas: {match}")
        
        # Convertir a coordenadas PDF (bottom-left origin)
        x = match['x0'] - 2
        y = height - match['bottom'] - 2
        w = (match['x1'] - match['x0']) + 4
        h = (match['bottom'] - match['top']) + 4
        
        return {
            'x': x,
            'y': y,
            'w': w,
            'h': h,
            'page_height': height,
            'page_width': page.width
        }

def generate_text_overlay(coords, replacement_text, page_width, page_height):
    """Genera un PDF overlay con el texto de reemplazo."""
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(page_width, page_height))
    
    # 1. CUBRIR el texto original con un rectángulo blanco
    # Usar padding mínimo para no tapar elementos adyacentes
    padding = 0.5
    c.setFillColorRGB(1, 1, 1)  # Blanco
    c.rect(
        coords['x'] - padding, 
        coords['y'] - padding, 
        coords['w'] + (padding * 2), 
        coords['h'] + (padding * 2), 
        fill=1, 
        stroke=0
    )
    
    # 2. ESCRIBIR el nuevo texto
    c.setFillColorRGB(0, 0, 0)  # Negro
    
    # Configuración de fuente - más pequeña para que entre mejor
    font = "Helvetica-Bold"
    font_size = 6
    c.setFont(font, font_size)
    
    # Dividir texto en líneas si es necesario
    lines = replacement_text.split('\n')
    
    # Calcular el alto total del texto
    total_text_height = len(lines) * font_size * 1.2
    
    # Centrar verticalmente el texto en la caja
    current_y = coords['y'] + coords['h'] - ((coords['h'] - total_text_height) / 2) - font_size
    
    for line in lines:
        # Centrar horizontalmente
        text_width = c.stringWidth(line, font, font_size)
        x_pos = coords['x'] + (coords['w'] - text_width) / 2
        
        c.drawString(x_pos, current_y, line)
        current_y -= (font_size * 1.2)
    
    c.save()
    packet.seek(0)
    return packet

def update_pdf(pdf_path, search_text, replacement_text, output_path=None):
    """Actualiza un PDF reemplazando texto."""
    
    # 1. Encontrar coordenadas
    coords = find_text_coordinates(pdf_path, search_text)
    if not coords:
        return False
    
    # 2. Generar overlay
    print(f"Generando overlay con '{replacement_text}'...")
    overlay_stream = generate_text_overlay(
        coords, 
        replacement_text,
        coords['page_width'],
        coords['page_height']
    )
    
    # 3. Fusionar PDFs
    print("Fusionando PDFs...")
    base_pdf = pikepdf.Pdf.open(pdf_path)
    overlay_pdf = pikepdf.Pdf.open(overlay_stream)
    
    base_page = base_pdf.pages[0]
    overlay_page = overlay_pdf.pages[0]
    
    base_page.add_overlay(overlay_page, pikepdf.Rectangle(base_page.mediabox))
    
    # 4. Guardar resultado
    if not output_path:
        # Generar nombre automático
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = os.path.join("output", f"{base_name}_actualizado.pdf")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    base_pdf.save(output_path)
    
    print(f"✅ PDF actualizado guardado en: {output_path}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python update_pdf.py <pdf_path> <texto_a_buscar> <texto_de_reemplazo>")
        print("\nEjemplo:")
        print('  python update_pdf.py "input/templates/02_ORGANIGRAMA_LUCAS.pdf" "Lucas Capuano" "Diego Piñero"')
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    search_text = sys.argv[2]
    replacement_text = sys.argv[3]
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: El archivo {pdf_path} no existe")
        sys.exit(1)
    
    success = update_pdf(pdf_path, search_text, replacement_text)
    sys.exit(0 if success else 1)
