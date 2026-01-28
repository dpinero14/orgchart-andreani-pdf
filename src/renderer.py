import io
import textwrap
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from src.models import OrgTemplate, PositionData

def generate_overlay_pdf(template: OrgTemplate, data_list: list[PositionData]) -> io.BytesIO:
    """
    Generates a PDF file in memory (BytesIO) containing only the text overlays.
    This PDF will later be merged with the base template.
    """
    packet = io.BytesIO()
    # Create a new PDF with Reportlab
    c = canvas.Canvas(packet, pagesize=A4)
    
    # Map data by node_id for easy lookup
    data_map = {d.node_id: d for d in data_list}
    
    for node in template.nodes:
        if node.node_id not in data_map:
            continue
            
        data = data_map[node.node_id]
        
        # Determine text to draw
        # Format: Title \n Name
        # We might want to customize this logic
        text_content = f"{data.title}\n{data.person_name}"
        
        # Setup font
        c.setFont(node.font, node.font_size)
        
        # Calculate text position
        # ReportLab textobject for multi-line support
        text_object = c.beginText()
        
        # Basic text wrapping logic
        # Estimate chars per line based on width (very rough approximation)
        # Avg char width approx 0.6 * font_size
        avg_char_width = 0.6 * node.font_size
        chars_per_line = int(node.w / avg_char_width)
        
        lines = textwrap.wrap(text_content, width=chars_per_line)
        
        # Limit lines
        lines = lines[:node.max_lines]
        
        # Vertical alignment: start from top of the box
        # y is the bottom-left corner of the box. 
        # So top is y + h.
        # We need to drop down by font_size for the first line.
        
        current_y = node.y + node.h - node.font_size
        
        for line in lines:
            # Horizontal alignment
            text_width = c.stringWidth(line, node.font, node.font_size)
            x_pos = node.x
            
            if node.align == 'center':
                x_pos = node.x + (node.w - text_width) / 2
            elif node.align == 'right':
                x_pos = node.x + node.w - text_width
            
            c.drawString(x_pos, current_y, line)
            current_y -= (node.font_size * 1.2) # Line height
            
    c.save()
    packet.seek(0)
    return packet
