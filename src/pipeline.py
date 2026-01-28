import os
import json
import glob
from src.models import OrgTemplate, PositionData
from src.datalake import DataLakeService
from src.renderer import generate_overlay_pdf
from src.merger import merge_pdfs

def load_template_config(config_path: str) -> OrgTemplate:
    with open(config_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return OrgTemplate(**data)

def run_pipeline():
    print("Starting Org Chart Update Pipeline...")
    
    # 1. Setup paths
    base_dir = os.getcwd()
    templates_dir = os.path.join(base_dir, "input", "templates")
    output_dir = os.path.join(base_dir, "output")
    
    # 2. Initialize Services
    datalake = DataLakeService()
    
    # 3. Find all JSON configs in templates dir
    config_files = glob.glob(os.path.join(templates_dir, "*.json"))
    
    if not config_files:
        print("No template configurations found in input/templates/")
        return

    for config_file in config_files:
        print(f"Processing config: {config_file}")
        
        # Load Template Config
        try:
            template = load_template_config(config_file)
        except Exception as e:
            print(f"Failed to load config {config_file}: {e}")
            continue
            
        # Determine Base PDF Path (Assumes same filename as json but .pdf)
        base_pdf_filename = f"{template.org_id}.pdf"
        base_pdf_path = os.path.join(templates_dir, base_pdf_filename)
        
        if not os.path.exists(base_pdf_path):
            print(f"Base PDF not found: {base_pdf_path}. Skipping.")
            continue
            
        # Fetch Data
        print(f"Fetching data for Org ID: {template.org_id}")
        positions = datalake.get_positions_for_org(template.org_id)
        
        if not positions:
            print(f"No positions found for {template.org_id}. Skipping.")
            continue
            
        # Generate Overlay
        print("Generating text overlay...")
        overlay_stream = generate_overlay_pdf(template, positions)
        
        # Merge
        output_filename = f"{template.org_id}_actualizado.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        print(f"Merging into {output_path}...")
        merge_pdfs(base_pdf_path, overlay_stream, output_path, template)
        
    print("Pipeline completed.")

if __name__ == "__main__":
    run_pipeline()
