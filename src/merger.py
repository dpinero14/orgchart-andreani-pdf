import io
import pikepdf
from src.models import OrgTemplate

def merge_pdfs(base_pdf_path: str, overlay_pdf_stream: io.BytesIO, output_path: str, template: OrgTemplate):
    """
    Merges a base PDF file with an overlay PDF stream.
    Saves the result to output_path.
    """
    # Open base PDF
    try:    
        base_pdf = pikepdf.Pdf.open(base_pdf_path)
    except FileNotFoundError:
        print(f"Error: Base PDF not found at {base_pdf_path}")
        return

    # Open overlay PDF from memory
    overlay_pdf = pikepdf.Pdf.open(overlay_pdf_stream)
    
    # We assume we are overlaying on the specific page defined in the template
    # and that the overlay PDF has only one page (the one we just generated)
    
    target_page_index = template.page
    
    if target_page_index >= len(base_pdf.pages):
        print(f"Error: Template targets page {target_page_index}, but base PDF has only {len(base_pdf.pages)} pages.")
        return

    base_page = base_pdf.pages[target_page_index]
    overlay_page = overlay_pdf.pages[0]
    
    # Apply overlay
    base_page.add_overlay(overlay_page, pikepdf.Rectangle(base_page.mediabox))
    
    # Save output
    base_pdf.save(output_path)
    print(f"Successfully generated: {output_path}")
