from typing import List, Optional
from pydantic import BaseModel, Field

class OrgNode(BaseModel):
    """
    Configuration for a single node (box) in the PDF template.
    Defines where and how text should be rendered.
    """
    node_id: str = Field(..., description="Unique logical identifier for the node (e.g., 'CEO', 'CFO')")
    x: float = Field(..., description="X coordinate of the bottom-left corner of the text box (in points)")
    y: float = Field(..., description="Y coordinate of the bottom-left corner of the text box (in points)")
    w: float = Field(..., description="Width of the text box (in points)")
    h: float = Field(..., description="Height of the text box (in points)")
    font: str = Field("Helvetica", description="Font name to use")
    font_size: int = Field(10, description="Font size in points")
    align: str = Field("center", description="Text alignment: 'left', 'center', 'right'")
    max_lines: int = Field(2, description="Maximum number of lines allowed before truncation or resizing")

class OrgTemplate(BaseModel):
    """
    Configuration for a specific PDF template file.
    """
    org_id: str = Field(..., description="Identifier for the Organization Chart (matches PDF filename logic)")
    page: int = Field(0, description="Page number (0-indexed) where the chart is located")
    nodes: List[OrgNode] = Field(..., description="List of nodes defined in this template")

class PositionData(BaseModel):
    """
    Data payload for a specific position in the org chart.
    Source of truth coming from the Datalake.
    """
    org_id: str
    node_id: str
    title: str = Field(..., description="Job title, e.g. 'Gerente General'")
    person_name: str = Field(..., description="Name of the person holding the position")
    active_flag: bool = True
