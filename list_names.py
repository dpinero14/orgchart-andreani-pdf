"""
Script para listar todos los nombres y cargos disponibles en los organigramas.

Uso:
    python list_names.py [org_id]
"""

import sys
import json

def load_database():
    """Carga la base de datos de coordenadas."""
    with open("coordinates_db.json", 'r', encoding='utf-8') as f:
        return json.load(f)

def list_all_names():
    """Lista todos los nombres de todos los organigramas."""
    db = load_database()
    
    print("=" * 80)
    print("📋 NOMBRES Y TEXTOS DISPONIBLES EN ORGANIGRAMAS")
    print("=" * 80)
    
    for org_id, org_data in db['organigramas'].items():
        print(f"\n📄 {org_id}")
        print(f"   PDF: {org_data['pdf_path']}")
        print(f"   Elementos: {len(org_data['text_elements'])}")
        print("\n   Textos encontrados:")
        
        # Filtrar y mostrar nombres (texto que contiene mayúsculas y minúsculas)
        names = []
        titles = []
        other = []
        
        for element in org_data['text_elements']:
            text = element['text']
            
            # Clasificar el texto
            if any(c.islower() for c in text) and any(c.isupper() for c in text):
                # Probable nombre de persona
                names.append(text)
            elif text.isupper() and len(text) > 3:
                # Probable cargo/título
                titles.append(text)
            else:
                other.append(text)
        
        if names:
            print("\n   👤 Nombres de personas:")
            for name in names:
                print(f"      - {name}")
        
        if titles:
            print("\n   💼 Cargos/Títulos:")
            for title in titles:
                print(f"      - {title}")
        
        if len(other) > 0 and len(other) < 20:
            print(f"\n   📝 Otros ({len(other)} elementos): {', '.join(other[:10])}")
    
    print("\n" + "=" * 80)

def list_org_names(org_id):
    """Lista los nombres de un organigrama específico."""
    db = load_database()
    
    if org_id not in db['organigramas']:
        print(f"❌ Organigrama '{org_id}' no encontrado")
        print(f"   Disponibles: {list(db['organigramas'].keys())}")
        return
    
    org_data = db['organigramas'][org_id]
    
    print("=" * 80)
    print(f"📋 TEXTOS EN: {org_id}")
    print("=" * 80)
    print(f"PDF: {org_data['pdf_path']}")
    print(f"Total elementos: {len(org_data['text_elements'])}\n")
    
    for i, element in enumerate(org_data['text_elements'], 1):
        print(f"{i:3}. '{element['text']}'")
        print(f"     Coordenadas: x={element['x']}, y={element['y']}, "
              f"w={element['w']}, h={element['h']}")
    
    print("=" * 80)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        list_org_names(sys.argv[1])
    else:
        list_all_names()
