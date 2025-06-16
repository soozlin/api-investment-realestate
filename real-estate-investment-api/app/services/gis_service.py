import httpx
from typing import Optional, Dict, Any
import logging
from ..models import GISData, ZoningInfo, ZoningType
from ..config import settings

logger = logging.getLogger(__name__)

class GISService:
    """Service for integrating with municipal GIS and open data APIs"""
    
    def __init__(self):
        self.vancouver_url = settings.vancouver_open_data_url
        self.burnaby_url = settings.burnaby_open_data_url
        self.surrey_url = settings.surrey_open_data_url
    
    async def get_gis_data_by_address(self, address: str, city: str) -> Optional[GISData]:
        """Get GIS data including zoning information by address"""
        try:
            city_lower = city.lower()
            
            if "vancouver" in city_lower:
                return await self._get_vancouver_data(address)
            elif "burnaby" in city_lower:
                return await self._get_burnaby_data(address)
            elif "surrey" in city_lower:
                return await self._get_surrey_data(address)
            else:
                logger.warning(f"GIS data not available for city: {city}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching GIS data: {str(e)}")
            return None
    
    async def _get_vancouver_data(self, address: str) -> Optional[GISData]:
        """Get Vancouver open data"""
        try:
            async with httpx.AsyncClient() as client:
                
                mock_zoning = ZoningInfo(
                    zoning_code="RS-1",
                    zoning_description="One-Family Dwelling",
                    zoning_type=ZoningType.RESIDENTIAL,
                    max_density=0.7,
                    max_height=10.7,
                    setback_requirements={
                        "front": 6.0,
                        "rear": 7.5,
                        "side": 1.2
                    },
                    multiplex_allowed=False,
                    laneway_house_allowed=True
                )
                
                return GISData(
                    municipality="Vancouver",
                    zoning=mock_zoning,
                    lot_dimensions={
                        "width": 33.0,
                        "depth": 122.0,
                        "area": 4026.0
                    },
                    has_lane_access=True,
                    flood_zone=None,
                    development_permits=[]
                )
                
        except Exception as e:
            logger.error(f"Error fetching Vancouver GIS data: {str(e)}")
            return None
    
    async def _get_burnaby_data(self, address: str) -> Optional[GISData]:
        """Get Burnaby open data"""
        try:
            mock_zoning = ZoningInfo(
                zoning_code="R2",
                zoning_description="Two Family Residential",
                zoning_type=ZoningType.RESIDENTIAL,
                max_density=0.6,
                max_height=9.0,
                setback_requirements={
                    "front": 7.5,
                    "rear": 7.5,
                    "side": 1.5
                },
                multiplex_allowed=True,
                laneway_house_allowed=False
            )
            
            return GISData(
                municipality="Burnaby",
                zoning=mock_zoning,
                lot_dimensions={
                    "width": 40.0,
                    "depth": 120.0,
                    "area": 4800.0
                },
                has_lane_access=False,
                flood_zone=None,
                development_permits=[]
            )
            
        except Exception as e:
            logger.error(f"Error fetching Burnaby GIS data: {str(e)}")
            return None
    
    async def _get_surrey_data(self, address: str) -> Optional[GISData]:
        """Get Surrey open data"""
        try:
            mock_zoning = ZoningInfo(
                zoning_code="RF",
                zoning_description="Single Family Residential",
                zoning_type=ZoningType.RESIDENTIAL,
                max_density=0.5,
                max_height=9.5,
                setback_requirements={
                    "front": 6.0,
                    "rear": 6.0,
                    "side": 1.2
                },
                multiplex_allowed=False,
                laneway_house_allowed=False
            )
            
            return GISData(
                municipality="Surrey",
                zoning=mock_zoning,
                lot_dimensions={
                    "width": 50.0,
                    "depth": 100.0,
                    "area": 5000.0
                },
                has_lane_access=False,
                flood_zone=None,
                development_permits=[]
            )
            
        except Exception as e:
            logger.error(f"Error fetching Surrey GIS data: {str(e)}")
            return None
    
    def analyze_development_potential(self, gis_data: GISData) -> Dict[str, Any]:
        """Analyze development potential based on zoning and lot characteristics"""
        analysis = {
            "multiplex_potential": False,
            "laneway_house_potential": False,
            "density_utilization": 0.0,
            "additional_units_possible": 0,
            "development_recommendations": []
        }
        
        if gis_data.zoning.multiplex_allowed:
            analysis["multiplex_potential"] = True
            analysis["additional_units_possible"] = 2  # Duplex potential
            analysis["development_recommendations"].append("Consider duplex conversion")
        
        if gis_data.zoning.laneway_house_allowed and gis_data.has_lane_access:
            analysis["laneway_house_potential"] = True
            analysis["additional_units_possible"] += 1
            analysis["development_recommendations"].append("Laneway house feasible")
        
        lot_area = gis_data.lot_dimensions.get("area", 0)
        if lot_area > 0 and gis_data.zoning.max_density:
            analysis["density_utilization"] = 0.3
            if analysis["density_utilization"] < gis_data.zoning.max_density:
                analysis["development_recommendations"].append("Additional density available")
        
        return analysis
