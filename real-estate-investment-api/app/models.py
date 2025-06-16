from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class PropertyType(str, Enum):
    SINGLE_FAMILY = "single_family"
    CONDO = "condo"
    TOWNHOUSE = "townhouse"
    DUPLEX = "duplex"
    MULTIPLEX = "multiplex"
    COMMERCIAL = "commercial"

class ZoningType(str, Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    MIXED_USE = "mixed_use"
    INDUSTRIAL = "industrial"
    AGRICULTURAL = "agricultural"

class MLSProperty(BaseModel):
    mls_number: str
    address: str
    city: str
    province: str = "BC"
    postal_code: str
    price: float
    bedrooms: int
    bathrooms: float
    square_feet: Optional[int] = None
    lot_size: Optional[float] = None
    property_type: PropertyType
    year_built: Optional[int] = None
    listing_date: datetime
    amenities: List[str] = []
    description: Optional[str] = None

class BCAssessmentData(BaseModel):
    pid: str  # Property Identifier
    address: str
    assessed_value: float
    assessed_land_value: float
    assessed_improvement_value: float
    assessment_year: int
    property_class: str
    land_size: Optional[float] = None
    year_built: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None

class ZoningInfo(BaseModel):
    zoning_code: str
    zoning_description: str
    zoning_type: ZoningType
    max_density: Optional[float] = None
    max_height: Optional[float] = None
    setback_requirements: Dict[str, float] = {}
    multiplex_allowed: bool = False
    laneway_house_allowed: bool = False

class GISData(BaseModel):
    municipality: str
    zoning: ZoningInfo
    lot_dimensions: Dict[str, float] = {}  # width, depth, area
    has_lane_access: bool = False
    flood_zone: Optional[str] = None
    development_permits: List[str] = []

class LTSAData(BaseModel):
    title_number: str
    legal_description: str
    owner_name: str
    registration_date: datetime
    encumbrances: List[str] = []
    easements: List[str] = []
    covenants: List[str] = []

class RecurringExpenses(BaseModel):
    property_tax_annual: float
    insurance_annual: float
    utilities_monthly: Dict[str, float] = {
        "water": 0.0,
        "electricity": 0.0,
        "gas": 0.0,
        "internet": 0.0,
        "sewage": 0.0,
        "garbage": 0.0
    }
    maintenance_annual: float
    management_fee_percentage: float = 0.0
    vacancy_rate_percentage: float = 5.0

class RentalIncomeEstimate(BaseModel):
    estimated_monthly_rent: float
    comparable_rents: List[float] = []
    rent_per_sqft: Optional[float] = None
    market_analysis_date: datetime

class InvestmentAnalysis(BaseModel):
    cap_rate: float
    gross_rental_yield: float
    net_rental_yield: float
    cash_flow_monthly: float
    cash_flow_annual: float
    total_annual_expenses: float
    roi_percentage: float

class ConsolidatedProperty(BaseModel):
    address: str
    city: str
    postal_code: str
    
    mls_data: Optional[MLSProperty] = None
    
    bc_assessment: Optional[BCAssessmentData] = None
    
    gis_data: Optional[GISData] = None
    
    ltsa_data: Optional[LTSAData] = None
    
    rental_estimate: Optional[RentalIncomeEstimate] = None
    expenses: Optional[RecurringExpenses] = None
    investment_analysis: Optional[InvestmentAnalysis] = None
    
    data_sources_used: List[str] = []
    last_updated: datetime = Field(default_factory=datetime.now)

class PropertyAnalysisRequest(BaseModel):
    address: str
    city: str
    postal_code: Optional[str] = None
    mls_number: Optional[str] = None
    purchase_price: Optional[float] = None  # If different from listing price

class PropertyAnalysisResponse(BaseModel):
    success: bool
    property: Optional[ConsolidatedProperty] = None
    errors: List[str] = []
    warnings: List[str] = []
