# BC Real Estate Investment Analysis API - Specification

## Overview

The BC Real Estate Investment Analysis API consolidates real estate data from multiple British Columbia sources and provides comprehensive investment analysis for rental property managers, landlords, and property developers.

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, the API does not require authentication for public endpoints. External data source integrations require API keys configured in environment variables.

## Content Type
All requests and responses use `application/json` content type.

## Error Handling

### Standard Error Response
```json
{
  "detail": "Error description"
}
```

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request (missing required parameters)
- `404` - Not Found (property or data not available)
- `500` - Internal Server Error

## Endpoints

### Health Check

#### GET /healthz
Check API health status.

**Response:**
```json
{
  "status": "ok"
}
```

---

### Property Analysis

#### POST /api/v1/property/analyze
Comprehensive property analysis consolidating all data sources.

**Request Body:**
```json
{
  "address": "123 Main Street",
  "city": "Vancouver",
  "postal_code": "V6B 1A1",
  "mls_number": "MLS123456",
  "purchase_price": 850000.0
}
```

**Request Parameters:**
- `address` (string, required): Property street address
- `city` (string, required): City name
- `postal_code` (string, optional): Postal code
- `mls_number` (string, optional): MLS listing number
- `purchase_price` (number, optional): Purchase price override

**Response:**
```json
{
  "success": true,
  "property": {
    "address": "123 Main Street",
    "city": "Vancouver",
    "postal_code": "V6B 1A1",
    "mls_data": {
      "mls_number": "MLS123456",
      "price": 850000.0,
      "bedrooms": 3,
      "bathrooms": 2.0,
      "square_feet": 1200,
      "lot_size": 5000.0,
      "property_type": "single_family",
      "year_built": 1995,
      "amenities": ["parking", "garden"]
    },
    "bc_assessment": {
      "pid": "123-456-789",
      "assessed_value": 825000.0,
      "assessed_land_value": 650000.0,
      "assessed_improvement_value": 175000.0,
      "assessment_year": 2024,
      "property_class": "01 - Residential"
    },
    "gis_data": {
      "municipality": "Vancouver",
      "zoning": {
        "zoning_code": "RS-1",
        "zoning_description": "One-Family Dwelling",
        "zoning_type": "residential",
        "multiplex_allowed": false,
        "laneway_house_allowed": true
      },
      "has_lane_access": true
    },
    "ltsa_data": {
      "title_number": "CA123456",
      "legal_description": "LOT 1 DISTRICT LOT 123 PLAN 456",
      "owner_name": "JOHN DOE",
      "encumbrances": [],
      "easements": ["STATUTORY RIGHT OF WAY"]
    },
    "rental_estimate": {
      "estimated_monthly_rent": 2800.0,
      "comparable_rents": [2660.0, 2940.0, 2744.0, 2856.0, 3024.0],
      "rent_per_sqft": 2.33
    },
    "expenses": {
      "property_tax_annual": 2062.50,
      "insurance_annual": 2125.00,
      "utilities_monthly": {
        "water": 49.50,
        "electricity": 93.50,
        "gas": 71.50,
        "internet": 82.50,
        "sewage": 38.50,
        "garbage": 27.50
      },
      "maintenance_annual": 12750.00,
      "vacancy_rate_percentage": 5.0
    },
    "investment_analysis": {
      "cap_rate": 5.85,
      "gross_rental_yield": 3.95,
      "net_rental_yield": 2.89,
      "cash_flow_monthly": 1247.33,
      "cash_flow_annual": 14968.00,
      "total_annual_expenses": 18632.00,
      "roi_percentage": 8.81
    },
    "data_sources_used": ["MLS", "BC_Assessment", "GIS", "LTSA", "Investment_Analysis"],
    "last_updated": "2024-06-16T20:11:00Z"
  },
  "errors": [],
  "warnings": []
}
```

---

### Individual Data Sources

#### GET /api/v1/property/{property_id}/mls
Get MLS listing data only.

**Parameters:**
- `property_id` (path): Property address or MLS number
- `city` (query, optional): Required when using address

**Response:**
```json
{
  "success": true,
  "data": {
    "mls_number": "MLS123456",
    "address": "123 Main Street",
    "city": "Vancouver",
    "price": 850000.0,
    "bedrooms": 3,
    "bathrooms": 2.0,
    "square_feet": 1200,
    "property_type": "single_family",
    "amenities": ["parking", "garden"]
  }
}
```

#### GET /api/v1/property/{property_id}/assessment
Get BC Assessment data only.

**Parameters:**
- `property_id` (path): Property address or PID
- `city` (query, optional): Required when using address

**Response:**
```json
{
  "success": true,
  "data": {
    "pid": "123-456-789",
    "address": "123 Main Street",
    "assessed_value": 825000.0,
    "assessed_land_value": 650000.0,
    "assessed_improvement_value": 175000.0,
    "assessment_year": 2024,
    "property_class": "01 - Residential",
    "bedrooms": 3,
    "bathrooms": 2.0
  }
}
```

#### GET /api/v1/property/{property_id}/zoning
Get municipal zoning and GIS data.

**Parameters:**
- `property_id` (path): Property address
- `city` (query, required): City name

**Response:**
```json
{
  "success": true,
  "data": {
    "municipality": "Vancouver",
    "zoning": {
      "zoning_code": "RS-1",
      "zoning_description": "One-Family Dwelling",
      "zoning_type": "residential",
      "max_density": 0.7,
      "max_height": 10.7,
      "setback_requirements": {
        "front": 6.0,
        "rear": 7.5,
        "side": 1.2
      },
      "multiplex_allowed": false,
      "laneway_house_allowed": true
    },
    "lot_dimensions": {
      "width": 33.0,
      "depth": 122.0,
      "area": 4026.0
    },
    "has_lane_access": true
  },
  "development_analysis": {
    "multiplex_potential": false,
    "laneway_house_potential": true,
    "density_utilization": 0.3,
    "additional_units_possible": 1,
    "development_recommendations": ["Laneway house feasible"]
  }
}
```

#### GET /api/v1/property/{property_id}/ltsa
Get LTSA land title information.

**Parameters:**
- `property_id` (path): Property address
- `city` (query, optional): Required when not using PID
- `pid` (query, optional): Property Identifier

**Response:**
```json
{
  "success": true,
  "data": {
    "title_number": "CA123456",
    "legal_description": "LOT 1 DISTRICT LOT 123 PLAN 456",
    "owner_name": "JOHN DOE",
    "registration_date": "2024-06-16T20:11:00Z",
    "encumbrances": [],
    "easements": ["STATUTORY RIGHT OF WAY"],
    "covenants": []
  },
  "risk_analysis": {
    "encumbrance_risk": false,
    "easement_impact": true,
    "covenant_restrictions": false,
    "risk_level": "medium"
  }
}
```

---

### Investment Analysis

#### GET /api/v1/property/{property_id}/investment-analysis
Get detailed investment metrics.

**Parameters:**
- `property_id` (path): Property address
- `city` (query, required): City name
- `purchase_price` (query, optional): Purchase price override

**Response:**
```json
{
  "success": true,
  "investment_analysis": {
    "cap_rate": 5.85,
    "gross_rental_yield": 3.95,
    "net_rental_yield": 2.89,
    "cash_flow_monthly": 1247.33,
    "cash_flow_annual": 14968.00,
    "total_annual_expenses": 18632.00,
    "roi_percentage": 8.81
  },
  "rental_estimate": {
    "estimated_monthly_rent": 2800.0,
    "comparable_rents": [2660.0, 2940.0, 2744.0, 2856.0, 3024.0],
    "rent_per_sqft": 2.33,
    "market_analysis_date": "2024-06-16T20:11:00Z"
  },
  "expenses": {
    "property_tax_annual": 2062.50,
    "insurance_annual": 2125.00,
    "utilities_monthly": {
      "water": 49.50,
      "electricity": 93.50,
      "gas": 71.50,
      "internet": 82.50,
      "sewage": 38.50,
      "garbage": 27.50
    },
    "maintenance_annual": 12750.00,
    "management_fee_percentage": 0.0,
    "vacancy_rate_percentage": 5.0
  },
  "development_analysis": {
    "current_income_potential": 33600.0,
    "development_opportunities": [
      {
        "type": "laneway_house",
        "estimated_cost": 200000,
        "estimated_annual_income": 23520.0
      }
    ],
    "additional_income_potential": 23520.0,
    "development_costs_estimate": 200000,
    "roi_on_development": 11.76
  },
  "errors": [],
  "warnings": []
}
```

#### GET /api/v1/property/{property_id}/comparables
Get comparable properties analysis.

**Parameters:**
- `property_id` (path): Property address
- `city` (query, required): City name

**Response:**
```json
{
  "success": true,
  "data": {
    "comparable_count": 5,
    "price_range": {
      "min": 780000,
      "max": 920000,
      "average": 847500
    },
    "rent_range": {
      "min": 2650,
      "max": 3100,
      "average": 2825
    },
    "comparables": [
      {
        "address": "125 Main Street",
        "price": 820000,
        "bedrooms": 3,
        "bathrooms": 2.0,
        "estimated_rent": 2750
      }
    ]
  }
}
```

---

### Utility Services

#### GET /api/v1/utilities/estimate
Get utility cost estimates.

**Parameters:**
- `city` (query, required): City name
- `bedrooms` (query, optional): Number of bedrooms (default: 3)
- `square_feet` (query, optional): Property square footage

**Response:**
```json
{
  "success": true,
  "utilities_monthly": {
    "water": 49.50,
    "electricity": 93.50,
    "gas": 71.50,
    "internet": 82.50,
    "sewage": 38.50,
    "garbage": 27.50
  },
  "total_monthly_utilities": 363.00
}
```

#### GET /api/v1/tax-rates
Get property tax rates for BC municipalities.

**Response:**
```json
{
  "success": true,
  "tax_rates": {
    "vancouver": {
      "rate": 0.0025,
      "description": "City of Vancouver"
    },
    "burnaby": {
      "rate": 0.0023,
      "description": "City of Burnaby"
    },
    "surrey": {
      "rate": 0.0022,
      "description": "City of Surrey"
    }
  }
}
```

---

## Investment Calculation Formulas

### CAP Rate
```
CAP Rate = (Annual Rental Income - Annual Operating Expenses) / Property Value × 100
```

### Gross Rental Yield
```
Gross Rental Yield = (Annual Rental Income / Property Value) × 100
```

### Net Rental Yield
```
Net Rental Yield = (Annual Rental Income - Annual Operating Expenses) / Property Value × 100
```

### ROI (Return on Investment)
```
ROI = (Annual Cash Flow / Down Payment) × 100
```
*Assumes 20% down payment*

### Cash Flow
```
Monthly Cash Flow = (Monthly Rental Income - Monthly Operating Expenses)
Annual Cash Flow = Monthly Cash Flow × 12
```

---

## Data Sources

### MLS Data (REALTOR.ca DDF Web API)
- Property listings and details
- Market pricing information
- Property characteristics
- Comparable sales data

### BC Assessment
- Official property assessments
- Land and improvement values
- Property classifications
- Historical assessment data

### Municipal GIS Data
- **Vancouver**: opendata.vancouver.ca
- **Burnaby**: data.burnaby.ca
- **Surrey**: surrey.ca open data
- Zoning information and bylaws
- Development potential analysis

### LTSA (Land Title and Survey Authority)
- Land title information
- Legal descriptions
- Encumbrances and easements
- Ownership details

---

## Expense Categories

### Property Tax
- Calculated based on assessed value
- Municipality-specific tax rates
- Annual amount

### Insurance
- Property type-based rates
- Coverage for property value
- Annual premium estimates

### Utilities (Monthly)
- **Water**: Municipal water services
- **Electricity**: BC Hydro or local utility
- **Gas**: Natural gas heating/cooking
- **Internet**: High-speed internet service
- **Sewage**: Municipal sewage services
- **Garbage**: Waste collection services

### Maintenance
- 1.5% of property value annually
- Covers repairs and upkeep
- Preventive maintenance costs

### Vacancy Allowance
- Default 5% of rental income
- Accounts for periods between tenants
- Market-dependent adjustment

---

## Development Potential Analysis

### Multiplex Conversion
- Zoning compliance check
- Duplex/triplex feasibility
- Additional rental income potential
- Estimated conversion costs

### Laneway House
- Lane access verification
- Municipal bylaw compliance
- Construction feasibility
- Rental income projection

### Density Utilization
- Current vs. maximum allowable density
- Additional development opportunities
- Setback and height restrictions
- ROI on development investments

---

## Error Codes and Troubleshooting

### Common Issues

#### 400 Bad Request
- Missing required parameters (city when using address)
- Invalid property identifiers
- Malformed request body

#### 404 Not Found
- Property not found in data sources
- Invalid MLS number or PID
- No data available for specified location

#### 500 Internal Server Error
- External API service unavailable
- Data processing errors
- Configuration issues

### Data Availability
- MLS data requires valid listings
- BC Assessment data may have delays
- GIS data limited to supported municipalities
- LTSA data requires proper property identification

---

## Rate Limits and Usage

### Current Limits
- No rate limiting implemented
- Recommended: Max 100 requests/minute per IP

### Best Practices
- Cache results when possible
- Use specific endpoints for targeted data
- Batch requests for multiple properties
- Handle errors gracefully with retries

---

## SDK and Integration Examples

### cURL Examples
```bash
# Health check
curl -X GET "http://localhost:8000/healthz"

# Full property analysis
curl -X POST "http://localhost:8000/api/v1/property/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "123 Main Street",
    "city": "Vancouver",
    "purchase_price": 850000
  }'

# Get investment analysis only
curl "http://localhost:8000/api/v1/property/123%20Main%20Street/investment-analysis?city=Vancouver&purchase_price=850000"

# Utility estimates
curl "http://localhost:8000/api/v1/utilities/estimate?city=Vancouver&bedrooms=3&square_feet=1200"
```

### Python Example
```python
import requests

# Full property analysis
response = requests.post(
    "http://localhost:8000/api/v1/property/analyze",
    json={
        "address": "123 Main Street",
        "city": "Vancouver",
        "purchase_price": 850000
    }
)

if response.status_code == 200:
    data = response.json()
    property_data = data["property"]
    investment_analysis = property_data["investment_analysis"]
    print(f"CAP Rate: {investment_analysis['cap_rate']}%")
    print(f"Monthly Cash Flow: ${investment_analysis['cash_flow_monthly']}")
else:
    print(f"Error: {response.status_code}")
```

### JavaScript Example
```javascript
// Full property analysis
const analyzeProperty = async (address, city, purchasePrice) => {
  try {
    const response = await fetch('http://localhost:8000/api/v1/property/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        address: address,
        city: city,
        purchase_price: purchasePrice
      })
    });

    if (response.ok) {
      const data = await response.json();
      return data.property;
    } else {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
  } catch (error) {
    console.error('Error analyzing property:', error);
    throw error;
  }
};

// Usage
analyzeProperty("123 Main Street", "Vancouver", 850000)
  .then(property => {
    console.log('CAP Rate:', property.investment_analysis.cap_rate + '%');
    console.log('Monthly Cash Flow: $' + property.investment_analysis.cash_flow_monthly);
  })
  .catch(error => console.error('Analysis failed:', error));
```
