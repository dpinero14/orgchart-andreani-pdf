"""
Script mejorado para actualizar PDFs usando la base de datos de posiciones.
Verifica superposiciones automáticamente para evitar cubrir cargos u otros elementos.

Uso:
    python update_smart.py <org_id> "<texto_a_buscar>" "<texto_de_reemplazo>"

Ejemplo:
    python update_smart.py "02_ORGANIGRAMA_LUCAS" "Lucas Capuano" "Diego Piñero"
"""

import sys
import os
import json
import io
import pikepdf
from reportlab.pdfgen import canvas

def load_positions_database():
    """Carga la base de datos de posiciones organizacionales."""
    db_path = "positions_db.json"
    
    if not os.path.exists(db_path):
        print(f"❌ No se encontró la base de datos: {db_path}")
        print("   Ejecuta primero: python extract_positions.py")
        return None
    
    with open(db_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_element_in_database(database, org_id, search_text):
    """Busca un elemento en la base de datos."""
    if org_id not in database['organigramas']:
        print(f"❌ Organigrama '{org_id}' no encontrado")
        return None
    
    org = database['organigramas'][org_id]
    search_lower = search_text.lower()
    
    # Buscar en nombres primero
    for nombre in org['nombres']:
        if search_lower in nombre['text'].lower():
            print(f"✓ Nombre encontrado: '{nombre['text']}' en ({nombre['x']}, {nombre['y']})")
            return nombre, org
    
    # Buscar en cargos
    for cargo in org['cargos']:
        if search_lower in cargo['text'].lower():
            print(f"✓ Cargo encontrado: '{cargo['text']}' en ({cargo['x']}, {cargo['y']})")
            return cargo, org
    
    # Buscar en otros
    for otro in org['otros']:
        if search_lower in otro['text'].lower():
            print(f"✓ Texto encontrado: '{otro['text']}' en ({otro['x']}, {otro['y']})")
            return otro, org
    
    print(f"❌ No se encontró '{search_text}'")
    return None, None

def check_overlap(box1, box2, padding=2):
    """Verifica si dos cajas se superponen."""
    x1_min = box1['x'] - padding
    x1_max = box1['x'] + box1['w'] + padding
    y1_min = box1['y'] - padding
    y1_max = box1['y'] + box1['h'] + padding
    
    x2_min = box2['x'] - padding
    x2_max = box2['x'] + box2['w'] + padding
    y2_min = box2['y'] - padding
    y2_max = box2['y'] + box2['h'] + padding
    
    if x1_max < x2_min or x2_max < x1_min or y1_max < y2_min or y2_max < y1_min:
        return False
    return True

def find_overlapping_elements(element, org_data, padding=2):
    """Encuentra elementos que podrían superponerse con el área de reemplazo."""
    overlapping = []
    
    # Verificar contra todos los elementos
    all_elements = org_data['cargos'] + org_data['nombres'] + org_data['otros']
    
    for other in all_elements:
        if other['text'] != element['text'] and check_overlap(element, other, padding):
            overlapping.append(other)
    
    return overlapping

def adjust_replacement_area(element, overlapping):
    """Ajusta el área de reemplazo para evitar superposiciones."""
    if not overlapping:
        return element
    
    adjusted = element.copy()
    
    # Si hay elementos arriba, reducir altura hacia abajo
    above = [e for e in overlapping if e['y'] > element['y']]
    if above:
        # Reducir altura para no cubrir elementos de arriba
        max_y_above = max(e['y'] for e in above)
        if max_y_above > element['y'] + element['h']:
            adjusted['h'] = element['h'] * 0.9  # Reducir 10%
            print(f"   ⚠️  Ajustando altura para no cubrir elementos arriba")
    
    return adjusted

def generate_smart_overlay(element, replacement_text, page_width, page_height, overlapping):
    """Genera overlay inteligente que evita superposiciones."""
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(page_width, page_height))
    
    # Ajustar área si hay superposiciones
    adjusted = adjust_replacement_area(element, overlapping)
    
    # Usar padding adaptativo
    if overlapping:
        padding = 0.2  # Padding mínimo si hay elementos cerca
        print(f"   🎯 Usando padding mínimo ({padding}px) - {len(overlapping)} elementos cercanos")
    else:
        padding = 0.5
    
    # 1. CUBRIR el texto original
    c.setFillColorRGB(1, 1, 1)
    c.rect(
        adjusted['x'] - padding,
        adjusted['y'] - padding,
        adjusted['w'] + (padding * 2),
        adjusted['h'] + (padding * 2),
        fill=1,
        stroke=0
    )
    
    # 2. ESCRIBIR el nuevo texto
    c.setFillColorRGB(0, 0, 0)
    font = "Helvetica-Bold"
    font_size = 6
    c.setFont(font, font_size)
    
    lines = replacement_text.split('\n')
    total_text_height = len(lines) * font_size * 1.2
    current_y = adjusted['y'] + adjusted['h'] - ((adjusted['h'] - total_text_height) / 2) - font_size
    
    for line in lines:
        text_width = c.stringWidth(line, font, font_size)
        x_pos = adjusted['x'] + (adjusted['w'] - text_width) / 2
        c.drawString(x_pos, current_y, line)
        current_y -= (font_size * 1.2)
    
    c.save()
    packet.seek(0)
    return packet

def update_pdf_smart(org_id, search_text, replacement_text, output_path=None):
    """Actualiza PDF con verificación de superposiciones."""
    
    # 1. Cargar base de datos
    print("📂 Cargando base de datos de posiciones...")
    database = load_positions_database()
    if not database:
        return False
    
    # 2. Buscar elemento
    print(f"🔍 Buscando '{search_text}' en '{org_id}'...")
    result = find_element_in_database(database, org_id, search_text)
    if not result or result[0] is None:
        return False
    
    element, org_data = result
    pdf_path = org_data['pdf_path']
    
    if not os.path.exists(pdf_path):
        print(f"❌ El archivo PDF no existe: {pdf_path}")
        return False
    
    # 3. Verificar superposiciones
    print("🔎 Verificando superposiciones...")
    overlapping = find_overlapping_elements(element, org_data, padding=3)
    
    if overlapping:
        print(f"   ⚠️  {len(overlapping)} elementos cercanos detectados:")
        for overlap in overlapping[:3]:
            print(f"      - '{overlap['text']}' ({overlap['type']})")
    else:
        print(f"   ✓ Sin superposiciones detectadas")
    
    # 4. Generar overlay inteligente
    print(f"📝 Generando overlay con '{replacement_text}'...")
    overlay_stream = generate_smart_overlay(
        element,
        replacement_text,
        org_data['page_dimensions']['width'],
        org_data['page_dimensions']['height'],
        overlapping
    )
    
    # 5. Fusionar PDFs
    print("🔄 Fusionando PDFs...")
    base_pdf = pikepdf.Pdf.open(pdf_path)
    overlay_pdf = pikepdf.Pdf.open(overlay_stream)
    
    base_page = base_pdf.pages[0]
    overlay_page = overlay_pdf.pages[0]
    
    base_page.add_overlay(overlay_page, pikepdf.Rectangle(base_page.mediabox))
    
    # 6. Guardar resultado
    if not output_path:
        output_path = os.path.join("output", f"{org_id}_actualizado.pdf")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    base_pdf.save(output_path)
    
    print(f"✅ PDF actualizado guardado en: {output_path}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python update_smart.py <org_id> <texto_a_buscar> <texto_de_reemplazo>")
        print("\nEjemplo:")
        print('  python update_smart.py "02_ORGANIGRAMA_LUCAS" "Lucas Capuano" "Diego Piñero"')
        sys.exit(1)
    
    org_id = sys.argv[1]
    search_text = sys.argv[2]
    replacement_text = sys.argv[3]
    
    print("=" * 70)
    print("🧠 ACTUALIZADOR INTELIGENTE DE ORGANIGRAMAS")
    print("=" * 70)
    
    success = update_pdf_smart(org_id, search_text, replacement_text)
    
    print("=" * 70)
    sys.exit(0 if success else 1)
