"""
Script para extraer todas las coordenadas de texto de los organigramas
y guardarlas en una base de datos JSON.

Uso:
    python extract_coordinates.py

Genera un archivo coordinates_db.json con todas las coordenadas.
"""

import os
import json
import pdfplumber
from pathlib import Path

def group_nearby_words(words, max_distance=5):
    """Agrupa palabras que están cerca horizontalmente para formar frases."""
    if not words:
        return []
    
    # Ordenar palabras por línea (y) y luego por x
    sorted_words = sorted(words, key=lambda w: (round(w['top']), w['x0']))
    
    groups = []
    current_group = [sorted_words[0]]
    
    for word in sorted_words[1:]:
        last_word = current_group[-1]
        
        # Verificar si están en la misma línea y cerca horizontalmente
        same_line = abs(word['top'] - last_word['top']) < 3
        close_horizontally = word['x0'] - last_word['x1'] < max_distance
        
        if same_line and close_horizontally:
            current_group.append(word)
        else:
            groups.append(current_group)
            current_group = [word]
    
    groups.append(current_group)
    
    return groups

def extract_all_text_from_pdf(pdf_path):
    """Extrae todas las palabras y sus coordenadas de un PDF, agrupando palabras cercanas."""
    print(f"\n📄 Procesando: {pdf_path}")
    
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        height = page.height
        width = page.width
        
        # Extraer todas las palabras
        words = page.extract_words()
        
        # Agrupar palabras cercanas
        word_groups = group_nearby_words(words)
        
        text_elements = []
        for group in word_groups:
            # Combinar las palabras del grupo
            combined_text = ' '.join(word['text'] for word in group)
            
            # Calcular bounding box del grupo
            x0 = min(word['x0'] for word in group)
            x1 = max(word['x1'] for word in group)
            top = min(word['top'] for word in group)
            bottom = max(word['bottom'] for word in group)
            
            # Convertir a coordenadas PDF (bottom-left origin)
            x = x0 - 2
            y = height - bottom - 2
            w = (x1 - x0) + 4
            h = (bottom - top) + 4
            
            text_elements.append({
                'text': combined_text,
                'x': round(x, 2),
                'y': round(y, 2),
                'w': round(w, 2),
                'h': round(h, 2)
            })
        
        print(f"  ✓ Extraídos {len(text_elements)} grupos de texto")
        
        return {
            'page_width': width,
            'page_height': height,
            'elements': text_elements
        }

def build_coordinates_database():
    """Construye la base de datos de coordenadas de todos los organigramas."""
    templates_dir = Path("input/templates")
    pdf_files = list(templates_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No se encontraron PDFs en input/templates/")
        return
    
    database = {
        "version": "1.0",
        "description": "Base de datos de coordenadas de organigramas",
        "organigramas": {}
    }
    
    print(f"🔍 Encontrados {len(pdf_files)} PDFs para procesar\n")
    
    for pdf_file in pdf_files:
        org_id = pdf_file.stem  # Nombre sin extensión
        
        try:
            data = extract_all_text_from_pdf(str(pdf_file))
            database["organigramas"][org_id] = {
                "pdf_path": f"input/templates/{pdf_file.name}",
                "page_dimensions": {
                    "width": data['page_width'],
                    "height": data['page_height']
                },
                "text_elements": data['elements']
            }
        except Exception as e:
            print(f"  ❌ Error procesando {pdf_file.name}: {e}")
    
    # Guardar base de datos
    output_path = "coordinates_db.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Base de datos guardada en: {output_path}")
    print(f"📊 Total organigramas: {len(database['organigramas'])}")
    
    # Estadísticas
    total_elements = sum(len(org['text_elements']) for org in database['organigramas'].values())
    print(f"📝 Total elementos de texto: {total_elements}")
    
    return database

def search_text_in_database(database, org_id, search_text):
    """Busca un texto en la base de datos y retorna sus coordenadas."""
    if org_id not in database['organigramas']:
        return None
    
    org = database['organigramas'][org_id]
    
    # Buscar coincidencias exactas
    for element in org['text_elements']:
        if search_text.lower() in element['text'].lower():
            return {
                'x': element['x'],
                'y': element['y'],
                'w': element['w'],
                'h': element['h'],
                'page_width': org['page_dimensions']['width'],
                'page_height': org['page_dimensions']['height'],
                'found_text': element['text']
            }
    
    return None

if __name__ == "__main__":
    print("=" * 60)
    print("🗺️  EXTRACTOR DE COORDENADAS DE ORGANIGRAMAS")
    print("=" * 60)
    
    database = build_coordinates_database()
    
    if database:
        print("\n" + "=" * 60)
        print("📋 Resumen por organigrama:")
        print("=" * 60)
        for org_id, org_data in database['organigramas'].items():
            print(f"\n{org_id}:")
            print(f"  - Elementos: {len(org_data['text_elements'])}")
            print(f"  - Dimensiones: {org_data['page_dimensions']['width']} x {org_data['page_dimensions']['height']}")
            print(f"  - Primeros textos: {[e['text'] for e in org_data['text_elements'][:5]]}")
