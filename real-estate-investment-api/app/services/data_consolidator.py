from typing import Optional, List
import logging
from datetime import datetime
from ..models import ConsolidatedProperty, PropertyAnalysisRequest
from .mls_service import MLSService
from .bc_assessment_service import BCAssessmentService
from .gis_service import GISService
from .ltsa_service import LTSAService
from .investment_calculator import InvestmentCalculator

logger = logging.getLogger(__name__)

class DataConsolidator:
    """Service for consolidating data from all external sources"""
    
    def __init__(self):
        self.mls_service = MLSService()
        self.bc_assessment_service = BCAssessmentService()
        self.gis_service = GISService()
        self.ltsa_service = LTSAService()
        self.investment_calculator = InvestmentCalculator()
    
    async def consolidate_property_data(
        self, 
        request: PropertyAnalysisRequest
    ) -> ConsolidatedProperty:
        """Consolidate data from all available sources"""
        
        data_sources_used = []
        errors = []
        warnings = []
        
        if not request.mls_number and not request.address:
            raise ValueError("Either MLS number or address must be provided")
        
        consolidated = ConsolidatedProperty(
            address=request.address or "",
            city=request.city or "",
            postal_code=request.postal_code or "",
            data_sources_used=data_sources_used,
            last_updated=datetime.now()
        )
        
        try:
            if request.mls_number:
                mls_data = await self.mls_service.get_property_by_mls_number(request.mls_number)
                if mls_data:
                    consolidated.address = mls_data.address
                    consolidated.city = mls_data.city
                    consolidated.postal_code = mls_data.postal_code
            elif request.address and request.city:
                mls_data = await self.mls_service.search_property_by_address(
                    request.address, request.city
                )
            else:
                mls_data = None
            
            if mls_data:
                consolidated.mls_data = mls_data
                data_sources_used.append("MLS")
                logger.info("Successfully fetched MLS data")
            else:
                warnings.append("MLS data not available")
                
        except Exception as e:
            error_msg = f"Error fetching MLS data: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
        
        try:
            if consolidated.address and consolidated.city:
                bc_assessment = await self.bc_assessment_service.get_assessment_by_address(
                    consolidated.address, consolidated.city
                )
            else:
                bc_assessment = None
            
            if bc_assessment:
                consolidated.bc_assessment = bc_assessment
                data_sources_used.append("BC_Assessment")
                logger.info("Successfully fetched BC Assessment data")
            else:
                warnings.append("BC Assessment data not available")
                
        except Exception as e:
            error_msg = f"Error fetching BC Assessment data: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
        
        try:
            if consolidated.address and consolidated.city:
                gis_data = await self.gis_service.get_gis_data_by_address(
                    consolidated.address, consolidated.city
                )
            else:
                gis_data = None
            
            if gis_data:
                consolidated.gis_data = gis_data
                data_sources_used.append("GIS")
                logger.info("Successfully fetched GIS data")
            else:
                warnings.append("GIS data not available")
                
        except Exception as e:
            error_msg = f"Error fetching GIS data: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
        
        try:
            if consolidated.bc_assessment and consolidated.bc_assessment.pid:
                ltsa_data = await self.ltsa_service.get_title_info_by_pid(
                    consolidated.bc_assessment.pid
                )
            elif consolidated.address and consolidated.city:
                ltsa_data = await self.ltsa_service.get_title_info_by_address(
                    consolidated.address, consolidated.city
                )
            else:
                ltsa_data = None
            
            if ltsa_data:
                consolidated.ltsa_data = ltsa_data
                data_sources_used.append("LTSA")
                logger.info("Successfully fetched LTSA data")
            else:
                warnings.append("LTSA data not available")
                
        except Exception as e:
            error_msg = f"Error fetching LTSA data: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
        
        try:
            if consolidated.mls_data or consolidated.bc_assessment:
                rental_estimate = self.investment_calculator.estimate_rental_income(consolidated)
                consolidated.rental_estimate = rental_estimate
                
                property_value = (
                    request.purchase_price or
                    (consolidated.mls_data.price if consolidated.mls_data else None) or
                    (consolidated.bc_assessment.assessed_value if consolidated.bc_assessment else 0)
                )
                
                if property_value > 0:
                    expenses = self.investment_calculator.calculate_recurring_expenses(
                        consolidated, property_value
                    )
                    consolidated.expenses = expenses
                    
                    investment_analysis = self.investment_calculator.calculate_investment_analysis(
                        consolidated, request.purchase_price
                    )
                    consolidated.investment_analysis = investment_analysis
                    
                    data_sources_used.append("Investment_Analysis")
                    logger.info("Successfully calculated investment analysis")
                else:
                    warnings.append("Cannot calculate investment analysis without property value")
            else:
                warnings.append("Insufficient data for investment analysis")
                
        except Exception as e:
            error_msg = f"Error calculating investment analysis: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
        
        consolidated.data_sources_used = data_sources_used
        
        return consolidated, errors, warnings
    
    def resolve_data_conflicts(self, consolidated: ConsolidatedProperty) -> ConsolidatedProperty:
        """Resolve conflicts between different data sources"""
        
        if consolidated.bc_assessment and consolidated.mls_data:
            
            bc_bedrooms = consolidated.bc_assessment.bedrooms
            mls_bedrooms = consolidated.mls_data.bedrooms
            
            if bc_bedrooms and mls_bedrooms and abs(bc_bedrooms - mls_bedrooms) > 0:
                logger.warning(
                    f"Bedroom count mismatch: BC Assessment={bc_bedrooms}, MLS={mls_bedrooms}"
                )
            
            bc_bathrooms = consolidated.bc_assessment.bathrooms
            mls_bathrooms = consolidated.mls_data.bathrooms
            
            if bc_bathrooms and mls_bathrooms and abs(bc_bathrooms - mls_bathrooms) > 0.5:
                logger.warning(
                    f"Bathroom count mismatch: BC Assessment={bc_bathrooms}, MLS={mls_bathrooms}"
                )
        
        return consolidated
    
    async def get_comparable_analysis(
        self, 
        consolidated: ConsolidatedProperty
    ) -> dict:
        """Get comparable properties analysis"""
        
        try:
            if not consolidated.mls_data:
                return {"error": "MLS data required for comparable analysis"}
            
            comparables = await self.mls_service.get_comparable_properties(
                consolidated.address, consolidated.city
            )
            
            if not comparables:
                return {"warning": "No comparable properties found"}
            
            comparable_prices = [prop.price for prop in comparables]
            comparable_rents = []
            
            for comp in comparables:
                temp_consolidated = ConsolidatedProperty(
                    address=comp.address,
                    city=comp.city,
                    postal_code=comp.postal_code,
                    mls_data=comp
                )
                
                rental_estimate = self.investment_calculator.estimate_rental_income(temp_consolidated)
                comparable_rents.append(rental_estimate.estimated_monthly_rent)
            
            analysis = {
                "comparable_count": len(comparables),
                "price_range": {
                    "min": min(comparable_prices),
                    "max": max(comparable_prices),
                    "average": sum(comparable_prices) / len(comparable_prices)
                },
                "rent_range": {
                    "min": min(comparable_rents),
                    "max": max(comparable_rents),
                    "average": sum(comparable_rents) / len(comparable_rents)
                },
                "comparables": [
                    {
                        "address": comp.address,
                        "price": comp.price,
                        "bedrooms": comp.bedrooms,
                        "bathrooms": comp.bathrooms,
                        "estimated_rent": rent
                    }
                    for comp, rent in zip(comparables, comparable_rents)
                ]
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in comparable analysis: {str(e)}")
            return {"error": f"Comparable analysis failed: {str(e)}"}
