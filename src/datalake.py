from typing import List
from src.models import PositionData

class DataLakeService:
    """
    Service to fetch organization chart data.
    """
    
    def get_positions_for_org(self, org_id: str) -> List[PositionData]:
        """
        Fetches position data for a given org_id.
        Currently returns mock data.
        """
        # Mock Data Implementation
        if org_id == "01_ORGANIGRAMA_CEO":
            return [
                PositionData(
                    org_id="01_ORGANIGRAMA_CEO",
                    node_id="GERENTE_GENERAL",
                    title="CEO",
                    person_name="Carlos Andreani",
                    active_flag=True
                ),
                PositionData(
                    org_id="01_ORGANIGRAMA_CEO",
                    node_id="ASISTENTE",
                    title="Executive Assistant",
                    person_name="Maria Gonzalez",
                    active_flag=True
                )
            ]
        
        if org_id == "02_ORGANIGRAMA_LUCAS":
            return [
                PositionData(
                    org_id="02_ORGANIGRAMA_LUCAS",
                    node_id="DIRECTOR_LOGISTICA",
                    title="Director de Logística",
                    person_name="Diego Piñero",
                    active_flag=True
                )
            ]
        
        return []
