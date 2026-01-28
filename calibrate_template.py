import pdfplumber
import json
import os

def find_text_and_create_template(pdf_path, search_text, node_id, templates_dir):
    print(f"Opening {pdf_path}...")
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0] # Assume page 0
        height = page.height
        
        print(f"Page size: {page.width}x{page.height}")
        print(f"Searching for '{search_text}'...")
        
        # Search for text
        # .search() returns list of dicts with 'x0', 'top', 'x1', 'bottom'
        matches = page.search(search_text)
        
        if not matches:
            print("Text not found!")
            return

        match = matches[0] # Take first match
        print(f"Found match: {match}")
        
        # Convert to PDF coordinates (Bottom-Left origin)
        # pdfplumber 'top' and 'bottom' are from the TOP of the page.
        # ReportLab (and PDF standard) 'y' is from the BOTTOM.
        
        x = match['x0']
        w = match['x1'] - match['x0']
        h = match['bottom'] - match['top']
        
        # y is the bottom-left coordinate of the box
        # y = page_height - match['bottom']
        y = height - match['bottom']
        
        # We might want to expand the box slightly to ensure it covers the original text
        padding = 2
        x -= padding
        y -= padding
        w += (padding * 2)
        h += (padding * 2)

        # Create Template Structure
        template_data = {
            "org_id": "02_ORGANIGRAMA_LUCAS",
            "page": 0,
            "nodes": [
                {
                    "node_id": node_id,
                    "x": x,
                    "y": y,
                    "w": w,
                    "h": h,
                    "font": "Helvetica-Bold",
                    "font_size": 10,
                    "align": "center",
                    "max_lines": 3
                }
            ]
        }
        
        # Save JSON
        json_filename = "02_ORGANIGRAMA_LUCAS.json"
        json_path = os.path.join(templates_dir, json_filename)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, indent=2)
            
        print(f"Created template at {json_path}")

if __name__ == "__main__":
    pdf_path = os.path.join("input", "templates", "02_ORGANIGRAMA_LUCAS.pdf")
    templates_dir = os.path.join("input", "templates")
    
    # We are looking for "Lucas Capuano" to replace him with Diego Piñero
    # We assign node_id="DIRECTOR_IT" (guessing the role, but node_id is arbitrary as long as it matches datalake)
    find_text_and_create_template(pdf_path, "Lucas Capuano", "DIRECTOR_LOGISTICA", templates_dir)
