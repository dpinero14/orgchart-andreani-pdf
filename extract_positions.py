"""
Script para extraer posiciones organizacionales y sus coordenadas.
Esto permite un control más preciso al actualizar para evitar superposiciones.

Uso:
    python extract_positions.py
"""

import os
import json
import pdfplumber
from pathlib import Path

def classify_text_element(text, y_coord, all_elements):
    """Clasifica un elemento de texto como CARGO, NOMBRE u OTRO."""
    # Cargos típicamente están en mayúsculas
    if text.isupper() and len(text) > 3:
        # Verificar si hay un nombre justo debajo (posible cargo)
        nearby_below = [e for e in all_elements if 
                       abs(e['y'] - (y_coord - 10)) < 15 and 
                       any(c.islower() for c in e['text']) and 
                       any(c.isupper() for c in e['text'])]
        if nearby_below:
            return 'CARGO'
        return 'TITLE'
    
    # Nombres típicamente tienen mayúsculas y minúsculas
    elif any(c.islower() for c in text) and any(c.isupper() for c in text):
        # Verificar si hay un cargo justo arriba
        nearby_above = [e for e in all_elements if 
                       abs(e['y'] - (y_coord + 10)) < 15 and 
                       e['text'].isupper()]
        if nearby_above:
            return 'NOMBRE'
        return 'TEXT'
    
    return 'OTHER'

def extract_positions_from_pdf(pdf_path):
    """Extrae posiciones organizacionales (cargos y nombres) de un PDF."""
    print(f"\n📄 Procesando: {pdf_path}")
    
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        height = page.height
        width = page.width
        
        # Extraer palabras
        words = page.extract_words()
        
        # Agrupar palabras cercanas horizontalmente
        sorted_words = sorted(words, key=lambda w: (round(w['top']), w['x0']))
        
        groups = []
        if sorted_words:
            current_group = [sorted_words[0]]
            
            for word in sorted_words[1:]:
                last_word = current_group[-1]
                same_line = abs(word['top'] - last_word['top']) < 3
                close_horizontally = word['x0'] - last_word['x1'] < 5
                
                if same_line and close_horizontally:
                    current_group.append(word)
                else:
                    groups.append(current_group)
                    current_group = [word]
            
            groups.append(current_group)
        
        # Convertir grupos a elementos
        all_elements = []
        for group in groups:
            combined_text = ' '.join(word['text'] for word in group)
            x0 = min(word['x0'] for word in group)
            x1 = max(word['x1'] for word in group)
            top = min(word['top'] for word in group)
            bottom = max(word['bottom'] for word in group)
            
            x = x0 - 2
            y = height - bottom - 2
            w = (x1 - x0) + 4
            h = (bottom - top) + 4
            
            all_elements.append({
                'text': combined_text,
                'x': round(x, 2),
                'y': round(y, 2),
                'w': round(w, 2),
                'h': round(h, 2),
                'type': None
            })
        
        # Clasificar elementos
        for elem in all_elements:
            elem['type'] = classify_text_element(elem['text'], elem['y'], all_elements)
        
        # Separar por tipo
        cargos = [e for e in all_elements if e['type'] == 'CARGO']
        nombres = [e for e in all_elements if e['type'] == 'NOMBRE']
        otros = [e for e in all_elements if e['type'] in ['TITLE', 'TEXT', 'OTHER']]
        
        print(f"  ✓ Encontrados: {len(cargos)} cargos, {len(nombres)} nombres, {len(otros)} otros")
        
        return {
            'page_width': width,
            'page_height': height,
            'cargos': cargos,
            'nombres': nombres,
            'otros': otros,
            'all_elements': all_elements
        }

def check_overlap(box1, box2, padding=2):
    """Verifica si dos cajas se superponen (con padding)."""
    x1_min = box1['x'] - padding
    x1_max = box1['x'] + box1['w'] + padding
    y1_min = box1['y'] - padding
    y1_max = box1['y'] + box1['h'] + padding
    
    x2_min = box2['x'] - padding
    x2_max = box2['x'] + box2['w'] + padding
    y2_min = box2['y'] - padding
    y2_max = box2['y'] + box2['h'] + padding
    
    # Verificar si NO se superponen
    if x1_max < x2_min or x2_max < x1_min or y1_max < y2_min or y2_max < y1_min:
        return False
    return True

def build_positions_database():
    """Construye la base de datos de posiciones organizacionales."""
    templates_dir = Path("input/templates")
    pdf_files = list(templates_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No se encontraron PDFs en input/templates/")
        return
    
    database = {
        "version": "2.0",
        "description": "Base de datos de posiciones organizacionales con validación de superposición",
        "organigramas": {}
    }
    
    print(f"🔍 Encontrados {len(pdf_files)} PDFs para procesar\n")
    
    for pdf_file in pdf_files:
        org_id = pdf_file.stem
        
        try:
            data = extract_positions_from_pdf(str(pdf_file))
            database["organigramas"][org_id] = {
                "pdf_path": f"input/templates/{pdf_file.name}",
                "page_dimensions": {
                    "width": data['page_width'],
                    "height": data['page_height']
                },
                "cargos": data['cargos'],
                "nombres": data['nombres'],
                "otros": data['otros']
            }
        except Exception as e:
            print(f"  ❌ Error procesando {pdf_file.name}: {e}")
    
    # Guardar base de datos
    output_path = "positions_db.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Base de datos de posiciones guardada en: {output_path}")
    
    # Estadísticas
    for org_id, org_data in database['organigramas'].items():
        print(f"\n📊 {org_id}:")
        print(f"   - Cargos: {len(org_data['cargos'])}")
        print(f"   - Nombres: {len(org_data['nombres'])}")
        print(f"   - Otros: {len(org_data['otros'])}")
    
    return database

if __name__ == "__main__":
    print("=" * 60)
    print("🏢 EXTRACTOR DE POSICIONES ORGANIZACIONALES")
    print("=" * 60)
    
    database = build_positions_database()
    
    if database:
        print("\n" + "=" * 60)
        print("✅ Base de datos creada exitosamente")
        print("=" * 60)
