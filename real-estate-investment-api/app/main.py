from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg
import logging
from typing import Optional

from .models import PropertyAnalysisRequest, PropertyAnalysisResponse, ConsolidatedProperty
from .services.data_consolidator import DataConsolidator
from .services.mls_service import MLSService
from .services.bc_assessment_service import BCAssessmentService
from .services.gis_service import GISService
from .services.ltsa_service import LTSAService
from .services.investment_calculator import InvestmentCalculator
from .config import settings

logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BC Real Estate Investment Analysis API",
    description="Consolidate real estate data from multiple BC sources and provide comprehensive investment analysis",
    version="1.0.0"
)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

data_consolidator = DataConsolidator()
mls_service = MLSService()
bc_assessment_service = BCAssessmentService()
gis_service = GISService()
ltsa_service = LTSAService()
investment_calculator = InvestmentCalculator()

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/api/v1/property/analyze", response_model=PropertyAnalysisResponse)
async def analyze_property(request: PropertyAnalysisRequest):
    """
    Main endpoint that takes property address/ID and returns comprehensive analysis
    including MLS data, BC Assessment, GIS/zoning info, LTSA data, and investment metrics
    """
    try:
        logger.info(f"Analyzing property: {request.address}, {request.city}")
        
        consolidated_property, errors, warnings = await data_consolidator.consolidate_property_data(request)
        
        consolidated_property = data_consolidator.resolve_data_conflicts(consolidated_property)
        
        return PropertyAnalysisResponse(
            success=True,
            property=consolidated_property,
            errors=errors,
            warnings=warnings
        )
        
    except Exception as e:
        logger.error(f"Error analyzing property: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/v1/property/{property_id}/mls")
async def get_mls_data(property_id: str, city: Optional[str] = None):
    """Get MLS listing data for a property"""
    try:
        if property_id.startswith("MLS"):
            mls_data = await mls_service.get_property_by_mls_number(property_id)
        else:
            if not city:
                raise HTTPException(status_code=400, detail="City required when using address")
            mls_data = await mls_service.search_property_by_address(property_id, city)
        
        if not mls_data:
            raise HTTPException(status_code=404, detail="MLS data not found")
        
        return {"success": True, "data": mls_data}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching MLS data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"MLS data fetch failed: {str(e)}")

@app.get("/api/v1/property/{property_id}/assessment")
async def get_assessment_data(property_id: str, city: Optional[str] = None):
    """Get BC Assessment data for a property"""
    try:
        if property_id.startswith("PID") or len(property_id.replace("-", "")) == 9:
            assessment_data = await bc_assessment_service.get_assessment_by_pid(property_id)
        else:
            if not city:
                raise HTTPException(status_code=400, detail="City required when using address")
            assessment_data = await bc_assessment_service.get_assessment_by_address(property_id, city)
        
        if not assessment_data:
            raise HTTPException(status_code=404, detail="BC Assessment data not found")
        
        return {"success": True, "data": assessment_data}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching BC Assessment data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"BC Assessment data fetch failed: {str(e)}")

@app.get("/api/v1/property/{property_id}/zoning")
async def get_zoning_data(property_id: str, city: str):
    """Get municipal zoning and bylaw information"""
    try:
        gis_data = await gis_service.get_gis_data_by_address(property_id, city)
        
        if not gis_data:
            raise HTTPException(status_code=404, detail="Zoning data not found")
        
        development_analysis = gis_service.analyze_development_potential(gis_data)
        
        return {
            "success": True, 
            "data": gis_data,
            "development_analysis": development_analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching zoning data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Zoning data fetch failed: {str(e)}")

@app.get("/api/v1/property/{property_id}/investment-analysis")
async def get_investment_analysis(
    property_id: str, 
    city: str,
    purchase_price: Optional[float] = None
):
    """Get calculated investment metrics for a property"""
    try:
        request = PropertyAnalysisRequest(
            address=property_id,
            city=city,
            purchase_price=purchase_price
        )
        
        consolidated_property, errors, warnings = await data_consolidator.consolidate_property_data(request)
        
        if not consolidated_property.investment_analysis:
            raise HTTPException(status_code=404, detail="Investment analysis not available - insufficient data")
        
        development_analysis = {}
        if consolidated_property.gis_data:
            development_analysis = investment_calculator.analyze_development_potential(consolidated_property)
        
        return {
            "success": True,
            "investment_analysis": consolidated_property.investment_analysis,
            "rental_estimate": consolidated_property.rental_estimate,
            "expenses": consolidated_property.expenses,
            "development_analysis": development_analysis,
            "errors": errors,
            "warnings": warnings
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating investment analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Investment analysis failed: {str(e)}")

@app.get("/api/v1/property/{property_id}/comparables")
async def get_comparable_analysis(property_id: str, city: str):
    """Get comparable properties analysis"""
    try:
        request = PropertyAnalysisRequest(address=property_id, city=city)
        consolidated_property, _, _ = await data_consolidator.consolidate_property_data(request)
        
        comparable_analysis = await data_consolidator.get_comparable_analysis(consolidated_property)
        
        return {"success": True, "data": comparable_analysis}
        
    except Exception as e:
        logger.error(f"Error fetching comparable analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Comparable analysis failed: {str(e)}")

@app.get("/api/v1/property/{property_id}/ltsa")
async def get_ltsa_data(property_id: str, city: Optional[str] = None, pid: Optional[str] = None):
    """Get LTSA land title information"""
    try:
        if pid:
            ltsa_data = await ltsa_service.get_title_info_by_pid(pid)
        else:
            if not city:
                raise HTTPException(status_code=400, detail="City required when not using PID")
            ltsa_data = await ltsa_service.get_title_info_by_address(property_id, city)
        
        if not ltsa_data:
            raise HTTPException(status_code=404, detail="LTSA data not found")
        
        risk_analysis = ltsa_service.analyze_title_risks(ltsa_data)
        
        return {
            "success": True, 
            "data": ltsa_data,
            "risk_analysis": risk_analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching LTSA data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"LTSA data fetch failed: {str(e)}")

@app.get("/api/v1/utilities/estimate")
async def estimate_utilities(
    city: str,
    bedrooms: int = 3,
    square_feet: Optional[int] = None
):
    """Get utility cost estimates for a property"""
    try:
        from .models import ConsolidatedProperty, MLSProperty, PropertyType
        from datetime import datetime
        
        mock_mls = MLSProperty(
            mls_number="UTIL_CALC",
            address="Utility Calculation",
            city=city,
            postal_code="V0V 0V0",
            price=0,
            bedrooms=bedrooms,
            bathrooms=2.0,
            square_feet=square_feet,
            property_type=PropertyType.SINGLE_FAMILY,
            listing_date=datetime.now()
        )
        
        mock_property = ConsolidatedProperty(
            address="Utility Calculation",
            city=city,
            postal_code="V0V 0V0",
            mls_data=mock_mls
        )
        
        expenses = investment_calculator.calculate_recurring_expenses(mock_property, 500000)
        
        return {
            "success": True,
            "utilities_monthly": expenses.utilities_monthly,
            "total_monthly_utilities": sum(expenses.utilities_monthly.values())
        }
        
    except Exception as e:
        logger.error(f"Error estimating utilities: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Utility estimation failed: {str(e)}")

@app.get("/api/v1/tax-rates")
async def get_tax_rates():
    """Get property tax rates for BC municipalities"""
    try:
        tax_rates = {
            "vancouver": {"rate": 0.0025, "description": "City of Vancouver"},
            "burnaby": {"rate": 0.0023, "description": "City of Burnaby"},
            "surrey": {"rate": 0.0022, "description": "City of Surrey"},
            "richmond": {"rate": 0.0024, "description": "City of Richmond"},
            "coquitlam": {"rate": 0.0021, "description": "City of Coquitlam"},
            "north_vancouver": {"rate": 0.0024, "description": "City of North Vancouver"},
            "west_vancouver": {"rate": 0.0020, "description": "District of West Vancouver"}
        }
        
        return {"success": True, "tax_rates": tax_rates}
        
    except Exception as e:
        logger.error(f"Error fetching tax rates: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Tax rates fetch failed: {str(e)}")
