from typing import Dict, List, Optional
import logging
from datetime import datetime
from ..models import (
    ConsolidatedProperty, InvestmentAnalysis, RecurringExpenses, 
    RentalIncomeEstimate, MLSProperty, BCAssessmentData, GISData
)

logger = logging.getLogger(__name__)

class InvestmentCalculator:
    """Service for calculating investment metrics and rental property analysis"""
    
    def __init__(self):
        self.base_utility_costs = {
            "water": 45.0,
            "electricity": 85.0,
            "gas": 65.0,
            "internet": 75.0,
            "sewage": 35.0,
            "garbage": 25.0
        }
        
        self.insurance_rates = {
            "single_family": 2.5,
            "condo": 1.8,
            "townhouse": 2.2,
            "duplex": 2.8,
            "multiplex": 3.2
        }
    
    def calculate_investment_analysis(
        self, 
        property_data: ConsolidatedProperty,
        purchase_price: Optional[float] = None
    ) -> InvestmentAnalysis:
        """Calculate comprehensive investment analysis"""
        
        property_value = (
            purchase_price or 
            (property_data.mls_data.price if property_data.mls_data else None) or
            (property_data.bc_assessment.assessed_value if property_data.bc_assessment else 0)
        )
        
        if property_value <= 0:
            raise ValueError("Property value must be greater than 0")
        
        rental_estimate = self.estimate_rental_income(property_data)
        annual_rental_income = rental_estimate.estimated_monthly_rent * 12
        
        expenses = self.calculate_recurring_expenses(property_data, property_value)
        total_annual_expenses = self._calculate_total_annual_expenses(expenses)
        
        net_operating_income = annual_rental_income - total_annual_expenses
        cap_rate = (net_operating_income / property_value) * 100
        gross_rental_yield = (annual_rental_income / property_value) * 100
        net_rental_yield = (net_operating_income / property_value) * 100
        
        monthly_cash_flow = (annual_rental_income - total_annual_expenses) / 12
        annual_cash_flow = net_operating_income
        
        down_payment = property_value * 0.20
        roi_percentage = (annual_cash_flow / down_payment) * 100 if down_payment > 0 else 0
        
        return InvestmentAnalysis(
            cap_rate=round(cap_rate, 2),
            gross_rental_yield=round(gross_rental_yield, 2),
            net_rental_yield=round(net_rental_yield, 2),
            cash_flow_monthly=round(monthly_cash_flow, 2),
            cash_flow_annual=round(annual_cash_flow, 2),
            total_annual_expenses=round(total_annual_expenses, 2),
            roi_percentage=round(roi_percentage, 2)
        )
    
    def estimate_rental_income(self, property_data: ConsolidatedProperty) -> RentalIncomeEstimate:
        """Estimate monthly rental income based on property characteristics"""
        
        base_rent = 1500.0  # Base rent for BC
        
        bedrooms = 0
        bathrooms = 0
        square_feet = 0
        amenities = []
        
        if property_data.mls_data:
            bedrooms = property_data.mls_data.bedrooms
            bathrooms = property_data.mls_data.bathrooms
            square_feet = property_data.mls_data.square_feet or 0
            amenities = property_data.mls_data.amenities
        elif property_data.bc_assessment:
            bedrooms = property_data.bc_assessment.bedrooms or 0
            bathrooms = property_data.bc_assessment.bathrooms or 0
        
        bedroom_multiplier = {
            0: 0.6,  # Studio
            1: 1.0,  # 1 bedroom
            2: 1.4,  # 2 bedroom
            3: 1.8,  # 3 bedroom
            4: 2.2,  # 4 bedroom
            5: 2.6   # 5+ bedroom
        }
        
        rent = base_rent * bedroom_multiplier.get(min(bedrooms, 5), 2.6)
        
        if bathrooms >= 2:
            rent *= 1.1
        elif bathrooms >= 3:
            rent *= 1.2
        
        if square_feet > 0:
            if square_feet > 1500:
                rent *= 1.15
            elif square_feet > 1200:
                rent *= 1.1
            elif square_feet < 800:
                rent *= 0.9
        
        amenity_bonus = 0
        valuable_amenities = [
            "parking", "garage", "garden", "deck", "patio", 
            "fireplace", "air_conditioning", "dishwasher", "laundry"
        ]
        
        for amenity in amenities:
            if any(val_amenity in amenity.lower() for val_amenity in valuable_amenities):
                amenity_bonus += 50
        
        rent += min(amenity_bonus, 300)  # Cap amenity bonus
        
        city_multipliers = {
            "vancouver": 1.3,
            "burnaby": 1.1,
            "richmond": 1.2,
            "surrey": 0.9,
            "coquitlam": 1.0,
            "north vancouver": 1.25,
            "west vancouver": 1.5
        }
        
        city = property_data.city.lower()
        for city_name, multiplier in city_multipliers.items():
            if city_name in city:
                rent *= multiplier
                break
        
        comparable_rents = [
            rent * 0.95,
            rent * 1.05,
            rent * 0.98,
            rent * 1.02,
            rent * 1.08
        ]
        
        rent_per_sqft = rent / square_feet if square_feet > 0 else None
        
        return RentalIncomeEstimate(
            estimated_monthly_rent=round(rent, 2),
            comparable_rents=[round(r, 2) for r in comparable_rents],
            rent_per_sqft=round(rent_per_sqft, 2) if rent_per_sqft else None,
            market_analysis_date=datetime.now()
        )
    
    def calculate_recurring_expenses(
        self, 
        property_data: ConsolidatedProperty, 
        property_value: float
    ) -> RecurringExpenses:
        """Calculate all recurring expenses for the property"""
        
        municipality = property_data.city.lower()
        if property_data.bc_assessment:
            from .bc_assessment_service import BCAssessmentService
            bc_service = BCAssessmentService()
            property_tax = bc_service.calculate_property_tax(
                property_data.bc_assessment.assessed_value, 
                municipality
            )
        else:
            tax_rate = 0.0023  # Average BC rate
            property_tax = property_value * tax_rate
        
        property_type = "single_family"  # Default
        if property_data.mls_data:
            property_type = property_data.mls_data.property_type.value
        
        insurance_rate = self.insurance_rates.get(property_type, 2.5)
        annual_insurance = (property_value / 1000) * insurance_rate
        
        utilities = self.base_utility_costs.copy()
        
        if property_data.mls_data and property_data.mls_data.square_feet:
            sqft = property_data.mls_data.square_feet
            if sqft > 1500:
                for utility in utilities:
                    utilities[utility] *= 1.2
            elif sqft > 1200:
                for utility in utilities:
                    utilities[utility] *= 1.1
        
        maintenance_rate = 0.015  # 1.5% annually
        annual_maintenance = property_value * maintenance_rate
        
        management_fee_percentage = 0.0  # Default to self-managed
        
        vacancy_rate = 5.0
        
        return RecurringExpenses(
            property_tax_annual=round(property_tax, 2),
            insurance_annual=round(annual_insurance, 2),
            utilities_monthly=utilities,
            maintenance_annual=round(annual_maintenance, 2),
            management_fee_percentage=management_fee_percentage,
            vacancy_rate_percentage=vacancy_rate
        )
    
    def _calculate_total_annual_expenses(self, expenses: RecurringExpenses) -> float:
        """Calculate total annual expenses from RecurringExpenses"""
        
        annual_costs = (
            expenses.property_tax_annual +
            expenses.insurance_annual +
            expenses.maintenance_annual
        )
        
        monthly_utilities = sum(expenses.utilities_monthly.values())
        annual_utilities = monthly_utilities * 12
        
        total_before_vacancy = annual_costs + annual_utilities
        
        vacancy_cost = total_before_vacancy * (expenses.vacancy_rate_percentage / 100)
        
        return total_before_vacancy + vacancy_cost
    
    def analyze_development_potential(self, property_data: ConsolidatedProperty) -> Dict:
        """Analyze potential for property development and additional income"""
        
        analysis = {
            "current_income_potential": 0.0,
            "development_opportunities": [],
            "additional_income_potential": 0.0,
            "development_costs_estimate": 0.0,
            "roi_on_development": 0.0
        }
        
        if not property_data.gis_data:
            return analysis
        
        gis_data = property_data.gis_data
        
        current_rental = self.estimate_rental_income(property_data)
        analysis["current_income_potential"] = current_rental.estimated_monthly_rent * 12
        
        additional_annual_income = 0.0
        development_costs = 0.0
        
        if gis_data.zoning.laneway_house_allowed and gis_data.has_lane_access:
            laneway_rent = current_rental.estimated_monthly_rent * 0.7  # 70% of main house
            additional_annual_income += laneway_rent * 12
            development_costs += 200000  # Estimated laneway house cost
            analysis["development_opportunities"].append({
                "type": "laneway_house",
                "estimated_cost": 200000,
                "estimated_annual_income": laneway_rent * 12
            })
        
        if gis_data.zoning.multiplex_allowed:
            duplex_rent = current_rental.estimated_monthly_rent * 0.8  # Each unit 80% of original
            additional_annual_income += duplex_rent * 12  # One additional unit
            development_costs += 150000  # Estimated conversion cost
            analysis["development_opportunities"].append({
                "type": "duplex_conversion",
                "estimated_cost": 150000,
                "estimated_annual_income": duplex_rent * 12
            })
        
        analysis["additional_income_potential"] = additional_annual_income
        analysis["development_costs_estimate"] = development_costs
        
        if development_costs > 0:
            analysis["roi_on_development"] = (additional_annual_income / development_costs) * 100
        
        return analysis
