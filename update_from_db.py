"""
Script para actualizar PDFs usando la base de datos de coordenadas.
Este método es más rápido que buscar las coordenadas cada vez.

Uso:
    python update_from_db.py <org_id> "<texto_a_buscar>" "<texto_de_reemplazo>"

Ejemplo:
    python update_from_db.py "02_ORGANIGRAMA_LUCAS" "Lucas Capuano" "Diego Piñero"
"""

import sys
import os
import json
import io
import pikepdf
from reportlab.pdfgen import canvas

def load_database():
    """Carga la base de datos de coordenadas."""
    db_path = "coordinates_db.json"
    
    if not os.path.exists(db_path):
        print(f"❌ No se encontró la base de datos: {db_path}")
        print("   Ejecuta primero: python extract_coordinates.py")
        return None
    
    with open(db_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_text_in_database(database, org_id, search_text):
    """Busca un texto en la base de datos y retorna sus coordenadas."""
    if org_id not in database['organigramas']:
        print(f"❌ Organigrama '{org_id}' no encontrado en la base de datos")
        print(f"   Organigramas disponibles: {list(database['organigramas'].keys())}")
        return None
    
    org = database['organigramas'][org_id]
    
    # Buscar coincidencias (puede ser texto parcial o múltiples palabras)
    search_lower = search_text.lower()
    matches = []
    
    for element in org['text_elements']:
        if search_lower in element['text'].lower():
            matches.append(element)
    
    if not matches:
        print(f"❌ No se encontró '{search_text}' en el organigrama")
        print(f"   Textos disponibles: {[e['text'] for e in org['text_elements'][:20]]}")
        return None
    
    # Si hay múltiples coincidencias, usar la primera
    if len(matches) > 1:
        print(f"⚠️  Se encontraron {len(matches)} coincidencias, usando la primera")
        for i, m in enumerate(matches[:5]):
            print(f"   {i+1}. '{m['text']}' en ({m['x']}, {m['y']})")
    
    element = matches[0]
    print(f"✓ Texto encontrado: '{element['text']}' en coordenadas ({element['x']}, {element['y']})")
    
    return {
        'x': element['x'],
        'y': element['y'],
        'w': element['w'],
        'h': element['h'],
        'page_width': org['page_dimensions']['width'],
        'page_height': org['page_dimensions']['height'],
        'pdf_path': org['pdf_path']
    }

def generate_text_overlay(coords, replacement_text):
    """Genera un PDF overlay con el texto de reemplazo."""
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(coords['page_width'], coords['page_height']))
    
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
    
    font = "Helvetica-Bold"
    font_size = 6
    c.setFont(font, font_size)
    
    # Dividir texto en líneas
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

def update_pdf_from_db(org_id, search_text, replacement_text, output_path=None):
    """Actualiza un PDF usando coordenadas de la base de datos."""
    
    # 1. Cargar base de datos
    print("📂 Cargando base de datos de coordenadas...")
    database = load_database()
    if not database:
        return False
    
    # 2. Buscar coordenadas
    print(f"🔍 Buscando '{search_text}' en '{org_id}'...")
    coords = find_text_in_database(database, org_id, search_text)
    if not coords:
        return False
    
    pdf_path = coords['pdf_path']
    
    if not os.path.exists(pdf_path):
        print(f"❌ El archivo PDF no existe: {pdf_path}")
        return False
    
    # 3. Generar overlay
    print(f"📝 Generando overlay con '{replacement_text}'...")
    overlay_stream = generate_text_overlay(coords, replacement_text)
    
    # 4. Fusionar PDFs
    print("🔄 Fusionando PDFs...")
    base_pdf = pikepdf.Pdf.open(pdf_path)
    overlay_pdf = pikepdf.Pdf.open(overlay_stream)
    
    base_page = base_pdf.pages[0]
    overlay_page = overlay_pdf.pages[0]
    
    base_page.add_overlay(overlay_page, pikepdf.Rectangle(base_page.mediabox))
    
    # 5. Guardar resultado
    if not output_path:
        output_path = os.path.join("output", f"{org_id}_actualizado.pdf")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    base_pdf.save(output_path)
    
    print(f"✅ PDF actualizado guardado en: {output_path}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python update_from_db.py <org_id> <texto_a_buscar> <texto_de_reemplazo>")
        print("\nEjemplo:")
        print('  python update_from_db.py "02_ORGANIGRAMA_LUCAS" "Lucas" "Diego Piñero"')
        print("\nPara ver organigramas disponibles, ejecuta:")
        print('  python extract_coordinates.py')
        sys.exit(1)
    
    org_id = sys.argv[1]
    search_text = sys.argv[2]
    replacement_text = sys.argv[3]
    
    print("=" * 60)
    print("🔄 ACTUALIZADOR DE ORGANIGRAMAS (desde BD)")
    print("=" * 60)
    
    success = update_pdf_from_db(org_id, search_text, replacement_text)
    
    print("=" * 60)
    sys.exit(0 if success else 1)
