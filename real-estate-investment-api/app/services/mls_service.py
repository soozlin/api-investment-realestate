import httpx
from typing import Optional, List
from datetime import datetime
import logging
from ..models import MLSProperty, PropertyType
from ..config import settings

logger = logging.getLogger(__name__)

class MLSService:
    """Service for integrating with REALTOR.ca DDF Web API"""
    
    def __init__(self):
        self.base_url = settings.realtor_ddf_base_url
        self.api_key = settings.realtor_ddf_api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def search_property_by_address(self, address: str, city: str) -> Optional[MLSProperty]:
        """Search for property by address"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/properties/search",
                    headers=self.headers,
                    params={
                        "address": address,
                        "city": city,
                        "province": "BC"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_mls_data(data)
                else:
                    logger.error(f"MLS API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching MLS data: {str(e)}")
            return None
    
    async def get_property_by_mls_number(self, mls_number: str) -> Optional[MLSProperty]:
        """Get property details by MLS number"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/properties/{mls_number}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_mls_data(data)
                else:
                    logger.error(f"MLS API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching MLS data: {str(e)}")
            return None
    
    def _parse_mls_data(self, data: dict) -> MLSProperty:
        """Parse MLS API response into MLSProperty model"""
        return MLSProperty(
            mls_number=data.get("mls_number", "MOCK123"),
            address=data.get("address", "123 Mock Street"),
            city=data.get("city", "Vancouver"),
            postal_code=data.get("postal_code", "V6B 1A1"),
            price=data.get("price", 850000.0),
            bedrooms=data.get("bedrooms", 3),
            bathrooms=data.get("bathrooms", 2.0),
            square_feet=data.get("square_feet", 1200),
            lot_size=data.get("lot_size", 5000.0),
            property_type=PropertyType(data.get("property_type", "single_family")),
            year_built=data.get("year_built", 1995),
            listing_date=datetime.now(),
            amenities=data.get("amenities", ["parking", "garden"]),
            description=data.get("description", "Beautiful family home")
        )
    
    async def get_comparable_properties(self, address: str, city: str, radius_km: float = 1.0) -> List[MLSProperty]:
        """Get comparable properties in the area"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/properties/comparables",
                    headers=self.headers,
                    params={
                        "address": address,
                        "city": city,
                        "radius": radius_km
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return [self._parse_mls_data(prop) for prop in data.get("properties", [])]
                else:
                    logger.error(f"MLS API error: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching comparable properties: {str(e)}")
            return []
