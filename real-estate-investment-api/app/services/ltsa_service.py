import httpx
from typing import Optional
from datetime import datetime
import logging
from ..models import LTSAData
from ..config import settings

logger = logging.getLogger(__name__)

class LTSAService:
    """Service for integrating with LTSA (Land Title and Survey Authority) data"""
    
    def __init__(self):
        self.base_url = settings.ltsa_base_url
        self.api_key = settings.ltsa_api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def get_title_info_by_address(self, address: str, city: str) -> Optional[LTSAData]:
        """Get land title information by property address"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/title/search",
                    headers=self.headers,
                    params={
                        "address": address,
                        "city": city
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_ltsa_data(data)
                else:
                    logger.error(f"LTSA API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching LTSA data: {str(e)}")
            return None
    
    async def get_title_info_by_pid(self, pid: str) -> Optional[LTSAData]:
        """Get land title information by Property Identifier (PID)"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/title/{pid}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_ltsa_data(data)
                else:
                    logger.error(f"LTSA API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching LTSA data by PID: {str(e)}")
            return None
    
    def _parse_ltsa_data(self, data: dict) -> LTSAData:
        """Parse LTSA API response into LTSAData model"""
        return LTSAData(
            title_number=data.get("title_number", "CA123456"),
            legal_description=data.get("legal_description", "LOT 1 DISTRICT LOT 123 PLAN 456"),
            owner_name=data.get("owner_name", "JOHN DOE"),
            registration_date=datetime.now(),
            encumbrances=data.get("encumbrances", []),
            easements=data.get("easements", ["STATUTORY RIGHT OF WAY"]),
            covenants=data.get("covenants", [])
        )
    
    def analyze_title_risks(self, ltsa_data: LTSAData) -> dict:
        """Analyze potential risks based on title information"""
        risks = {
            "encumbrance_risk": len(ltsa_data.encumbrances) > 0,
            "easement_impact": len(ltsa_data.easements) > 0,
            "covenant_restrictions": len(ltsa_data.covenants) > 0,
            "risk_level": "low"
        }
        
        risk_count = sum([
            risks["encumbrance_risk"],
            risks["easement_impact"],
            risks["covenant_restrictions"]
        ])
        
        if risk_count >= 2:
            risks["risk_level"] = "high"
        elif risk_count == 1:
            risks["risk_level"] = "medium"
        
        return risks
