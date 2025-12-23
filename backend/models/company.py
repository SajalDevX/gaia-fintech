"""
Company and Investment Data Models
GAIA - Global AI-powered Impact Assessment System
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


class IndustryClassification(str, Enum):
    """Standard industry classification codes."""
    TECHNOLOGY = "technology"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    ENERGY = "energy"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    TRANSPORTATION = "transportation"
    AGRICULTURE = "agriculture"
    CONSTRUCTION = "construction"
    TELECOMMUNICATIONS = "telecommunications"
    UTILITIES = "utilities"
    MINING = "mining"
    REAL_ESTATE = "real_estate"
    CONSUMER_GOODS = "consumer_goods"
    SERVICES = "services"
    OTHER = "other"


class MarketCapSize(str, Enum):
    """Market capitalization size classification."""
    MEGA_CAP = "mega_cap"  # >$200B
    LARGE_CAP = "large_cap"  # $10B-$200B
    MID_CAP = "mid_cap"  # $2B-$10B
    SMALL_CAP = "small_cap"  # $300M-$2B
    MICRO_CAP = "micro_cap"  # $50M-$300M
    NANO_CAP = "nano_cap"  # <$50M


class StockExchange(str, Enum):
    """Major stock exchanges."""
    NYSE = "NYSE"
    NASDAQ = "NASDAQ"
    LSE = "LSE"
    TSE = "TSE"
    HKEX = "HKEX"
    EURONEXT = "EURONEXT"
    SSE = "SSE"
    BSE = "BSE"
    OTHER = "OTHER"


class GeographicRegion(str, Enum):
    """Geographic regions for operations."""
    NORTH_AMERICA = "north_america"
    SOUTH_AMERICA = "south_america"
    EUROPE = "europe"
    ASIA = "asia"
    AFRICA = "africa"
    OCEANIA = "oceania"
    MIDDLE_EAST = "middle_east"


class StockInformation(BaseModel):
    """Stock/ticker information for a company."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "ticker": "TSLA",
            "exchange": "NASDAQ",
            "isin": "US88160R1014",
            "cusip": "88160R101",
            "currency": "USD",
            "current_price": 242.84,
            "market_cap": 770000000000,
            "market_cap_size": "mega_cap",
            "shares_outstanding": 3170000000,
            "fifty_two_week_high": 299.29,
            "fifty_two_week_low": 138.80,
            "beta": 2.31,
            "pe_ratio": 76.52,
            "dividend_yield": 0.0,
            "last_updated": "2025-12-23T10:30:00Z"
        }
    })

    ticker: str = Field(..., description="Stock ticker symbol", min_length=1, max_length=10)
    exchange: StockExchange = Field(..., description="Stock exchange")
    isin: Optional[str] = Field(None, description="International Securities Identification Number")
    cusip: Optional[str] = Field(None, description="CUSIP identifier")
    currency: str = Field(default="USD", description="Trading currency")

    current_price: Optional[float] = Field(None, ge=0, description="Current stock price")
    market_cap: Optional[float] = Field(None, ge=0, description="Market capitalization in USD")
    market_cap_size: Optional[MarketCapSize] = Field(None, description="Market cap size category")
    shares_outstanding: Optional[int] = Field(None, ge=0, description="Total shares outstanding")

    fifty_two_week_high: Optional[float] = Field(None, ge=0, description="52-week high price")
    fifty_two_week_low: Optional[float] = Field(None, ge=0, description="52-week low price")
    beta: Optional[float] = Field(None, description="Beta coefficient (volatility)")
    pe_ratio: Optional[float] = Field(None, description="Price-to-earnings ratio")
    dividend_yield: Optional[float] = Field(None, ge=0, le=100, description="Dividend yield percentage")

    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    @field_validator('ticker')
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        """Validate and normalize ticker symbol."""
        return v.upper().strip()


class GeographicPresence(BaseModel):
    """Geographic presence and revenue distribution."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "region": "north_america",
            "countries": ["USA", "Canada", "Mexico"],
            "revenue_percentage": 45.5,
            "employee_count": 75000,
            "facilities_count": 150,
            "headquarters": True
        }
    })

    region: GeographicRegion = Field(..., description="Geographic region")
    countries: List[str] = Field(default_factory=list, description="List of country codes (ISO 3166)")
    revenue_percentage: Optional[float] = Field(None, ge=0, le=100, description="Revenue percentage from this region")
    employee_count: Optional[int] = Field(None, ge=0, description="Number of employees in region")
    facilities_count: Optional[int] = Field(None, ge=0, description="Number of facilities in region")
    headquarters: bool = Field(default=False, description="Whether headquarters is in this region")


class HistoricalESGDataPoint(BaseModel):
    """Historical ESG data point for time-series analysis."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "date": "2024-12-31",
            "environmental_score": 78.5,
            "social_score": 82.3,
            "governance_score": 91.2,
            "overall_score": 84.0,
            "carbon_emissions_tons": 1250000,
            "renewable_energy_percentage": 65.5,
            "data_source": "CDP, Company ESG Report"
        }
    })

    date: datetime = Field(..., description="Data point date")
    environmental_score: Optional[float] = Field(None, ge=0, le=100, description="Environmental score")
    social_score: Optional[float] = Field(None, ge=0, le=100, description="Social score")
    governance_score: Optional[float] = Field(None, ge=0, le=100, description="Governance score")
    overall_score: Optional[float] = Field(None, ge=0, le=100, description="Overall ESG score")

    # Key metrics
    carbon_emissions_tons: Optional[float] = Field(None, ge=0, description="Total carbon emissions in tons CO2e")
    renewable_energy_percentage: Optional[float] = Field(None, ge=0, le=100, description="Renewable energy usage percentage")
    water_usage_cubic_meters: Optional[float] = Field(None, ge=0, description="Water usage in cubic meters")
    waste_recycled_percentage: Optional[float] = Field(None, ge=0, le=100, description="Waste recycled percentage")
    employee_diversity_percentage: Optional[float] = Field(None, ge=0, le=100, description="Employee diversity percentage")

    data_source: Optional[str] = Field(None, description="Source of the data")
    verified: bool = Field(default=False, description="Whether data is third-party verified")


class CompanyProfile(BaseModel):
    """Comprehensive company profile for ESG assessment."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "company_id": "TSLA-US",
            "name": "Tesla, Inc.",
            "legal_name": "Tesla, Inc.",
            "description": "Tesla designs, manufactures, and sells electric vehicles and energy storage products.",
            "founded_year": 2003,
            "headquarters_location": "Austin, Texas, USA",
            "website": "https://www.tesla.com",
            "industry": "technology",
            "sub_industry": "Electric Vehicles & Renewable Energy",
            "employee_count": 127855,
            "annual_revenue_usd": 96773000000,
            "stock_info": {
                "ticker": "TSLA",
                "exchange": "NASDAQ",
                "current_price": 242.84,
                "market_cap": 770000000000
            },
            "geographic_presence": [],
            "historical_esg_data": [],
            "certifications": ["ISO 14001", "ISO 45001"],
            "sustainability_reports_urls": ["https://www.tesla.com/impact-report/2023"],
            "created_at": "2025-12-23T10:00:00Z",
            "updated_at": "2025-12-23T10:00:00Z"
        }
    })

    # Basic Information
    company_id: str = Field(..., description="Unique company identifier")
    name: str = Field(..., description="Company name", min_length=1, max_length=255)
    legal_name: Optional[str] = Field(None, description="Legal registered name")
    description: Optional[str] = Field(None, description="Company description", max_length=2000)

    # Corporate Information
    founded_year: Optional[int] = Field(None, ge=1800, le=2030, description="Year founded")
    headquarters_location: Optional[str] = Field(None, description="Headquarters location")
    website: Optional[str] = Field(None, description="Company website URL")

    # Industry Classification
    industry: IndustryClassification = Field(..., description="Primary industry")
    sub_industry: Optional[str] = Field(None, description="Specific sub-industry")
    sic_codes: Optional[List[str]] = Field(default_factory=list, description="Standard Industrial Classification codes")
    naics_codes: Optional[List[str]] = Field(default_factory=list, description="North American Industry Classification codes")

    # Company Size
    employee_count: Optional[int] = Field(None, ge=0, description="Total number of employees")
    annual_revenue_usd: Optional[float] = Field(None, ge=0, description="Annual revenue in USD")

    # Stock Information
    stock_info: Optional[StockInformation] = Field(None, description="Stock/ticker information")

    # Geographic Presence
    geographic_presence: List[GeographicPresence] = Field(
        default_factory=list,
        description="Geographic presence and operations"
    )

    # Historical ESG Data
    historical_esg_data: List[HistoricalESGDataPoint] = Field(
        default_factory=list,
        description="Historical ESG performance data"
    )

    # Certifications and Reports
    certifications: List[str] = Field(
        default_factory=list,
        description="Environmental and social certifications (e.g., ISO 14001, B-Corp)"
    )
    sustainability_reports_urls: List[str] = Field(
        default_factory=list,
        description="URLs to sustainability and ESG reports"
    )

    # Additional Data
    parent_company: Optional[str] = Field(None, description="Parent company if subsidiary")
    subsidiaries: List[str] = Field(default_factory=list, description="List of subsidiary companies")
    competitors: List[str] = Field(default_factory=list, description="Main competitors")

    # Metadata
    data_sources: List[str] = Field(default_factory=list, description="Data sources used")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    # Custom fields for extensibility
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Additional custom fields")

    @field_validator('website')
    @classmethod
    def validate_website(cls, v: Optional[str]) -> Optional[str]:
        """Validate website URL format."""
        if v and not v.startswith(('http://', 'https://')):
            return f"https://{v}"
        return v

    @field_validator('employee_count', 'annual_revenue_usd')
    @classmethod
    def validate_positive_numbers(cls, v: Optional[float]) -> Optional[float]:
        """Ensure numbers are positive if provided."""
        if v is not None and v < 0:
            raise ValueError("Value must be non-negative")
        return v


class InvestmentQuery(BaseModel):
    """Investment analysis query request."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "ticker": "TSLA",
            "company_name": "Tesla, Inc.",
            "investment_amount_usd": 50000,
            "investment_horizon_years": 5,
            "risk_tolerance": "moderate",
            "esg_priority": "high",
            "sdg_preferences": [7, 13],
            "excluded_industries": [],
            "custom_criteria": {}
        }
    })

    # Company Identification
    ticker: Optional[str] = Field(None, description="Stock ticker symbol")
    company_name: Optional[str] = Field(None, description="Company name")
    company_id: Optional[str] = Field(None, description="Company identifier")

    # Investment Parameters
    investment_amount_usd: Optional[float] = Field(None, ge=0, description="Investment amount in USD")
    investment_horizon_years: Optional[int] = Field(None, ge=1, le=50, description="Investment time horizon")
    risk_tolerance: Optional[str] = Field(
        "moderate",
        description="Risk tolerance level: low, moderate, high"
    )

    # ESG and Impact Preferences
    esg_priority: Optional[str] = Field(
        "medium",
        description="ESG priority level: low, medium, high"
    )
    sdg_preferences: List[int] = Field(
        default_factory=list,
        description="Preferred SDG goals (1-17)"
    )
    excluded_industries: List[IndustryClassification] = Field(
        default_factory=list,
        description="Industries to exclude"
    )

    # Additional Criteria
    require_certifications: List[str] = Field(
        default_factory=list,
        description="Required certifications (e.g., B-Corp, ISO 14001)"
    )
    minimum_esg_score: Optional[float] = Field(None, ge=0, le=100, description="Minimum acceptable ESG score")
    maximum_greenwashing_risk: Optional[float] = Field(None, ge=0, le=100, description="Maximum acceptable greenwashing risk")

    # Custom Criteria
    custom_criteria: Dict[str, Any] = Field(default_factory=dict, description="Custom analysis criteria")

    # Metadata
    requested_at: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")
    user_id: Optional[str] = Field(None, description="User requesting the analysis")

    @field_validator('sdg_preferences')
    @classmethod
    def validate_sdg_goals(cls, v: List[int]) -> List[int]:
        """Validate SDG goals are in valid range."""
        for goal in v:
            if goal < 1 or goal > 17:
                raise ValueError(f"SDG goal must be between 1 and 17, got {goal}")
        return v
