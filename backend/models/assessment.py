"""
ESG Assessment and Rating Models
GAIA - Global AI-powered Impact Assessment System
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


class RatingLevel(str, Enum):
    """Overall sustainability rating levels."""
    LEADER = "leader"  # 80-100
    ADVANCED = "advanced"  # 60-80
    AVERAGE = "average"  # 40-60
    LAGGARD = "laggard"  # 20-40
    CRITICAL = "critical"  # 0-20


class InvestmentRecommendation(str, Enum):
    """Investment recommendation levels."""
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    STRONG_SELL = "strong_sell"
    AVOID = "avoid"


class RiskLevel(str, Enum):
    """Risk assessment levels."""
    MINIMAL = "minimal"  # 80-100
    LOW = "low"  # 60-80
    MODERATE = "moderate"  # 40-60
    HIGH = "high"  # 20-40
    CRITICAL = "critical"  # 0-20


class ESGComponentScore(BaseModel):
    """Individual ESG component score with detailed breakdown."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "category": "Environmental",
            "score": 78.5,
            "weight": 0.33,
            "weighted_score": 25.9,
            "factors": {
                "carbon_emissions": 85.0,
                "energy_efficiency": 72.0,
                "water_management": 78.0,
                "renewable_energy": 82.0
            },
            "strengths": ["Strong renewable energy adoption", "Excellent carbon reduction targets"],
            "weaknesses": ["Limited water recycling programs", "Scope 3 emissions tracking incomplete"],
            "trend": "improving",
            "peer_percentile": 75.0
        }
    })

    category: str = Field(..., description="ESG category (Environmental, Social, or Governance)")
    score: float = Field(..., ge=0, le=100, description="Component score (0-100)")
    weight: float = Field(default=0.33, ge=0, le=1, description="Weight in overall score")
    weighted_score: float = Field(..., ge=0, le=100, description="Weighted contribution to overall score")

    factors: Dict[str, float] = Field(
        default_factory=dict,
        description="Individual factor scores within this component"
    )

    strengths: List[str] = Field(default_factory=list, description="Key strengths in this component")
    weaknesses: List[str] = Field(default_factory=list, description="Key weaknesses in this component")
    opportunities: List[str] = Field(default_factory=list, description="Improvement opportunities")
    threats: List[str] = Field(default_factory=list, description="Potential threats or risks")

    trend: Optional[str] = Field(None, description="Score trend: improving, stable, declining")
    year_over_year_change: Optional[float] = Field(None, description="Year-over-year score change")
    peer_percentile: Optional[float] = Field(None, ge=0, le=100, description="Percentile rank vs industry peers")

    data_quality: Optional[str] = Field(None, description="Data quality rating: excellent, good, fair, poor")
    data_coverage: Optional[float] = Field(None, ge=0, le=100, description="Percentage of data coverage")


class ESGScores(BaseModel):
    """Comprehensive ESG scoring breakdown."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "overall_score": 82.3,
            "environmental": {
                "category": "Environmental",
                "score": 78.5,
                "weight": 0.33
            },
            "social": {
                "category": "Social",
                "score": 85.0,
                "weight": 0.33
            },
            "governance": {
                "category": "Governance",
                "score": 83.5,
                "weight": 0.34
            },
            "rating_level": "advanced",
            "confidence_score": 88.5,
            "methodology_version": "1.0",
            "calculated_at": "2025-12-23T10:30:00Z"
        }
    })

    overall_score: float = Field(..., ge=0, le=100, description="Overall ESG score (0-100)")

    environmental: ESGComponentScore = Field(..., description="Environmental component score")
    social: ESGComponentScore = Field(..., description="Social component score")
    governance: ESGComponentScore = Field(..., description="Governance component score")

    rating_level: RatingLevel = Field(..., description="Overall ESG rating level")
    rating_description: Optional[str] = Field(None, description="Human-readable rating description")

    # Score Metrics
    confidence_score: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="Confidence in the assessment (0-100)"
    )
    data_completeness: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="Data completeness percentage"
    )

    # Comparison Metrics
    industry_average: Optional[float] = Field(None, ge=0, le=100, description="Industry average ESG score")
    industry_percentile: Optional[float] = Field(None, ge=0, le=100, description="Percentile rank in industry")
    global_percentile: Optional[float] = Field(None, ge=0, le=100, description="Global percentile rank")

    # Methodology
    methodology_version: str = Field(default="1.0", description="Assessment methodology version")
    assessment_framework: Optional[str] = Field(None, description="Framework used (e.g., GRI, SASB, TCFD)")

    # Metadata
    calculated_at: datetime = Field(default_factory=datetime.utcnow, description="Calculation timestamp")
    valid_until: Optional[datetime] = Field(None, description="Validity expiration date")

    @field_validator('overall_score')
    @classmethod
    def validate_weighted_score(cls, v: float) -> float:
        """Ensure overall score is within valid range."""
        if not 0 <= v <= 100:
            raise ValueError("Overall score must be between 0 and 100")
        return round(v, 2)


class GreenwashingRiskScore(BaseModel):
    """Greenwashing risk assessment with AI-powered detection."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "overall_risk_score": 25.5,
            "risk_level": "low",
            "risk_factors": {
                "claims_evidence_gap": 30.0,
                "disclosure_quality": 15.0,
                "historical_controversies": 20.0,
                "transparency_score": 25.0,
                "third_party_verification": 10.0
            },
            "red_flags": ["Limited third-party verification of carbon claims"],
            "confidence_score": 82.0,
            "detected_patterns": [],
            "assessed_at": "2025-12-23T10:30:00Z"
        }
    })

    overall_risk_score: float = Field(..., ge=0, le=100, description="Overall greenwashing risk (0=low, 100=high)")
    risk_level: RiskLevel = Field(..., description="Risk level classification")
    risk_description: Optional[str] = Field(None, description="Human-readable risk description")

    # Risk Factor Breakdown
    risk_factors: Dict[str, float] = Field(
        default_factory=dict,
        description="Individual risk factor scores"
    )

    # Specific Concerns
    red_flags: List[str] = Field(default_factory=list, description="Identified red flags")
    warning_signs: List[str] = Field(default_factory=list, description="Warning signs")
    positive_indicators: List[str] = Field(default_factory=list, description="Positive indicators")

    # Detection Analysis
    claims_vs_reality_gap: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Gap between claimed and actual performance"
    )
    disclosure_quality_score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Quality of ESG disclosures"
    )
    transparency_score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Overall transparency score"
    )
    third_party_verification: bool = Field(default=False, description="Has third-party verification")

    # AI Detection
    detected_patterns: List[str] = Field(
        default_factory=list,
        description="AI-detected greenwashing patterns"
    )
    nlp_sentiment_analysis: Optional[Dict[str, Any]] = Field(
        None,
        description="NLP analysis of company communications"
    )
    satellite_data_conflicts: List[str] = Field(
        default_factory=list,
        description="Conflicts between claims and satellite observations"
    )

    # Confidence
    confidence_score: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="Confidence in greenwashing assessment"
    )

    # Metadata
    assessed_at: datetime = Field(default_factory=datetime.utcnow, description="Assessment timestamp")
    methodology_version: str = Field(default="1.0", description="Methodology version")


class SustainabilityRating(BaseModel):
    """Overall sustainability rating combining all factors."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "overall_rating": "advanced",
            "rating_score": 82.3,
            "letter_grade": "A-",
            "stars": 4.5,
            "strengths": ["Strong environmental performance", "Excellent governance"],
            "weaknesses": ["Limited supply chain transparency"],
            "key_opportunities": ["Expand renewable energy usage", "Improve diversity metrics"],
            "outlook": "positive",
            "peer_comparison": "above_average"
        }
    })

    overall_rating: RatingLevel = Field(..., description="Overall sustainability rating level")
    rating_score: float = Field(..., ge=0, le=100, description="Numerical rating score")

    # Alternative Representations
    letter_grade: Optional[str] = Field(None, description="Letter grade (A+ to F)")
    stars: Optional[float] = Field(None, ge=0, le=5, description="Star rating (0-5)")
    percentile_rank: Optional[float] = Field(None, ge=0, le=100, description="Percentile rank")

    # Qualitative Assessment
    strengths: List[str] = Field(default_factory=list, description="Key strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Key weaknesses")
    key_opportunities: List[str] = Field(default_factory=list, description="Key improvement opportunities")
    critical_risks: List[str] = Field(default_factory=list, description="Critical risks to address")

    # Forward-Looking
    outlook: Optional[str] = Field(None, description="Future outlook: positive, stable, negative, uncertain")
    improvement_trajectory: Optional[str] = Field(None, description="Improvement trajectory over time")

    # Comparative
    peer_comparison: Optional[str] = Field(
        None,
        description="Comparison to peers: leader, above_average, average, below_average, laggard"
    )
    industry_rank: Optional[int] = Field(None, ge=1, description="Rank within industry")

    # Summary
    executive_summary: Optional[str] = Field(None, max_length=1000, description="Executive summary")


class InvestmentRecommendationResult(BaseModel):
    """Investment recommendation with detailed rationale."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "recommendation": "buy",
            "confidence": 85.0,
            "rationale": "Strong ESG performance with low greenwashing risk",
            "target_allocation_percentage": 5.0,
            "expected_return_annual": 12.5,
            "esg_alignment_score": 88.0,
            "impact_potential_score": 82.0,
            "key_considerations": [],
            "time_horizon_recommendation": "long_term",
            "recommended_at": "2025-12-23T10:30:00Z"
        }
    })

    recommendation: InvestmentRecommendation = Field(..., description="Investment recommendation")
    confidence: float = Field(..., ge=0, le=100, description="Confidence in recommendation")
    rationale: str = Field(..., description="Detailed rationale for recommendation")

    # Portfolio Guidance
    target_allocation_percentage: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Recommended portfolio allocation percentage"
    )
    position_sizing: Optional[str] = Field(None, description="Position sizing guidance")

    # Return Projections
    expected_return_annual: Optional[float] = Field(None, description="Expected annual return percentage")
    risk_adjusted_return: Optional[float] = Field(None, description="Risk-adjusted return estimate")

    # Impact Alignment
    esg_alignment_score: float = Field(..., ge=0, le=100, description="Alignment with ESG criteria")
    impact_potential_score: float = Field(..., ge=0, le=100, description="Potential for positive impact")
    sdg_alignment_score: Optional[float] = Field(None, ge=0, le=100, description="SDG alignment score")

    # Risk Factors
    key_risks: List[str] = Field(default_factory=list, description="Key investment risks")
    mitigating_factors: List[str] = Field(default_factory=list, description="Risk mitigating factors")

    # Considerations
    key_considerations: List[str] = Field(default_factory=list, description="Key investment considerations")
    alternative_options: List[str] = Field(default_factory=list, description="Alternative investment options")

    # Timing
    time_horizon_recommendation: Optional[str] = Field(
        None,
        description="Recommended time horizon: short_term, medium_term, long_term"
    )
    entry_timing: Optional[str] = Field(None, description="Entry timing guidance")

    # Monitoring
    rebalance_frequency: Optional[str] = Field(None, description="Recommended rebalancing frequency")
    monitoring_indicators: List[str] = Field(
        default_factory=list,
        description="Key indicators to monitor"
    )

    # Metadata
    recommended_at: datetime = Field(default_factory=datetime.utcnow, description="Recommendation timestamp")
    valid_until: Optional[datetime] = Field(None, description="Recommendation validity period")


class AssessmentResult(BaseModel):
    """Complete ESG assessment result for a company."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "assessment_id": "TSLA-US-20251223-001",
            "company_id": "TSLA-US",
            "company_name": "Tesla, Inc.",
            "ticker": "TSLA",
            "esg_scores": {},
            "sdg_alignment_scores": [],
            "greenwashing_risk": {},
            "sustainability_rating": {},
            "investment_recommendation": {},
            "assessment_timestamp": "2025-12-23T10:30:00Z",
            "processing_time_seconds": 45.2,
            "data_sources_count": 15
        }
    })

    # Identification
    assessment_id: str = Field(..., description="Unique assessment identifier")
    company_id: str = Field(..., description="Company identifier")
    company_name: str = Field(..., description="Company name")
    ticker: Optional[str] = Field(None, description="Stock ticker")

    # Assessment Results
    esg_scores: ESGScores = Field(..., description="ESG scores breakdown")
    sdg_alignment_scores: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="SDG alignment scores (imported from sdg module)"
    )
    greenwashing_risk: GreenwashingRiskScore = Field(..., description="Greenwashing risk assessment")
    sustainability_rating: SustainabilityRating = Field(..., description="Overall sustainability rating")
    investment_recommendation: InvestmentRecommendationResult = Field(
        ...,
        description="Investment recommendation"
    )

    # Additional Analysis
    key_findings: List[str] = Field(default_factory=list, description="Key assessment findings")
    material_issues: List[str] = Field(default_factory=list, description="Material ESG issues")
    controversies: List[Dict[str, Any]] = Field(default_factory=list, description="Recent controversies")

    # Data Quality
    data_quality_score: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="Overall data quality score"
    )
    data_sources_count: int = Field(default=0, ge=0, description="Number of data sources used")
    data_sources: List[str] = Field(default_factory=list, description="List of data sources")

    # Agent Analysis
    agent_consensus_score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Agent consensus strength"
    )
    debate_rounds_completed: int = Field(default=0, ge=0, description="Number of debate rounds completed")

    # Metadata
    assessment_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Assessment timestamp")
    methodology_version: str = Field(default="1.0", description="Assessment methodology version")
    processing_time_seconds: Optional[float] = Field(None, ge=0, description="Processing time in seconds")

    # Blockchain Verification
    blockchain_hash: Optional[str] = Field(None, description="Blockchain verification hash")
    verification_url: Optional[str] = Field(None, description="Verification URL")

    # User Context
    requested_by: Optional[str] = Field(None, description="User who requested the assessment")
    custom_parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom assessment parameters"
    )
