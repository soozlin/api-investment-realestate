# BC Real Estate Investment Analysis API

A comprehensive API that consolidates real estate data from multiple British Columbia sources and provides investment analysis for rental property managers, landlords, and property developers.

## Features

### Data Integration
- **MLS Listings**: Property details, pricing, and market data via REALTOR.ca DDF Web API
- **BC Assessment**: Official property assessments, land values, and property characteristics
- **Municipal GIS**: Zoning information, bylaws, development potential from Vancouver, Burnaby, Surrey open data
- **LTSA**: Land title information, encumbrances, and legal descriptions

### Investment Analysis
- **CAP Rate Calculation**: Net Operating Income / Property Value
- **Rental Income Estimation**: Based on property characteristics and local market data
- **Recurring Expense Calculation**: Property tax, insurance, utilities, maintenance
- **Development Potential**: Multiplex conversion, laneway house feasibility
- **ROI Analysis**: Return on investment calculations

### Utility Cost Estimates
- Water, electricity, gas, internet, sewage, garbage collection
- Adjusted for property size and location
- Monthly and annual projections

## API Endpoints

### Main Analysis
- `POST /api/v1/property/analyze` - Comprehensive property analysis
- `GET /api/v1/property/{property_id}/investment-analysis` - Investment metrics only

### Data Sources
- `GET /api/v1/property/{property_id}/mls` - MLS listing data
- `GET /api/v1/property/{property_id}/assessment` - BC Assessment data
- `GET /api/v1/property/{property_id}/zoning` - Municipal zoning and GIS data
- `GET /api/v1/property/{property_id}/ltsa` - Land title information

### Utilities & Comparables
- `GET /api/v1/property/{property_id}/comparables` - Comparable properties analysis
- `GET /api/v1/utilities/estimate` - Utility cost estimates
- `GET /api/v1/tax-rates` - Municipal property tax rates

## Setup

### Prerequisites
- Python 3.12+
- Poetry for dependency management

### Installation
```bash
# Install dependencies
poetry install

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Environment Variables
```env
# External API Configuration
REALTOR_DDF_API_KEY=your_realtor_api_key_here
BC_ASSESSMENT_API_KEY=your_bc_assessment_key_here
LTSA_API_KEY=your_ltsa_api_key_here

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
```

### Running the API
```bash
# Development server
poetry run fastapi dev app/main.py

# Production server
poetry run fastapi run app/main.py
```

The API will be available at `http://localhost:8000`

## Usage Examples

### Analyze a Property
```bash
curl -X POST "http://localhost:8000/api/v1/property/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "123 Main Street",
    "city": "Vancouver",
    "postal_code": "V6B 1A1",
    "purchase_price": 850000
  }'
```

### Get Investment Analysis
```bash
curl "http://localhost:8000/api/v1/property/123%20Main%20Street/investment-analysis?city=Vancouver&purchase_price=850000"
```

### Estimate Utilities
```bash
curl "http://localhost:8000/api/v1/utilities/estimate?city=Vancouver&bedrooms=3&square_feet=1200"
```

## Data Sources & Integration

### REALTOR.ca DDF Web API
- Requires authentication token
- Provides MLS listing data, property details, comparable sales
- Real-time market information

### BC Assessment
- Bulk electronic data access
- Official property assessments and characteristics
- Property tax calculations

### Municipal Open Data
- **Vancouver**: opendata.vancouver.ca - Zoning, development permits
- **Burnaby**: data.burnaby.ca - ArcGIS integration, municipal data
- **Surrey**: surrey.ca - Open data program, GIS services

### LTSA (Land Title and Survey Authority)
- myLTSA Enterprise and AUTOPROP services
- Land title information, legal descriptions
- Encumbrances and easements

## Investment Calculations

### CAP Rate
```
CAP Rate = (Annual Rental Income - Annual Operating Expenses) / Property Value × 100
```

### Recurring Expenses Include
- Property tax (based on assessed value and municipality)
- Insurance (varies by property type)
- Utilities (water, electricity, gas, internet, sewage, garbage)
- Maintenance (1.5% of property value annually)
- Vacancy allowance (5% default)

### Development Potential Analysis
- Multiplex conversion feasibility
- Laneway house potential
- Density utilization
- Additional rental income opportunities

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Error Handling

The API provides comprehensive error handling with:
- Detailed error messages
- Warning notifications for missing data
- Graceful degradation when some data sources are unavailable
- Partial results when possible

## Development

### Project Structure
```
app/
├── main.py              # FastAPI application and routes
├── models.py            # Pydantic data models
├── config.py            # Configuration settings
└── services/
    ├── mls_service.py           # MLS data integration
    ├── bc_assessment_service.py # BC Assessment integration
    ├── gis_service.py           # Municipal GIS integration
    ├── ltsa_service.py          # LTSA integration
    ├── investment_calculator.py # Investment analysis
    └── data_consolidator.py     # Data consolidation logic
```

### Testing
```bash
# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app
```

## License

This project is licensed under the MIT License.
