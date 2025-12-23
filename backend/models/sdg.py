"""
SDG (Sustainable Development Goals) Impact Models
GAIA - Global AI-powered Impact Assessment System
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


class SDGGoal(int, Enum):
    """17 UN Sustainable Development Goals."""
    NO_POVERTY = 1
    ZERO_HUNGER = 2
    GOOD_HEALTH = 3
    QUALITY_EDUCATION = 4
    GENDER_EQUALITY = 5
    CLEAN_WATER = 6
    CLEAN_ENERGY = 7
    DECENT_WORK = 8
    INDUSTRY_INNOVATION = 9
    REDUCED_INEQUALITIES = 10
    SUSTAINABLE_CITIES = 11
    RESPONSIBLE_CONSUMPTION = 12
    CLIMATE_ACTION = 13
    LIFE_BELOW_WATER = 14
    LIFE_ON_LAND = 15
    PEACE_JUSTICE = 16
    PARTNERSHIPS = 17


class ImpactType(str, Enum):
    """Type of impact on SDG."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class ImpactMagnitude(str, Enum):
    """Magnitude of impact."""
    TRANSFORMATIVE = "transformative"  # 80-100
    SIGNIFICANT = "significant"  # 60-80
    MODERATE = "moderate"  # 40-60
    LIMITED = "limited"  # 20-40
    MINIMAL = "minimal"  # 0-20


class ContributionType(str, Enum):
    """Type of contribution to SDG."""
    DIRECT = "direct"  # Direct contribution through core business
    INDIRECT = "indirect"  # Indirect through supply chain or operations
    ENABLING = "enabling"  # Enabling others to contribute
    CATALYTIC = "catalytic"  # Catalyzing systemic change


class SDGTarget(BaseModel):
    """Specific SDG target within a goal."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "target_number": "7.2",
            "target_description": "Increase share of renewable energy in global energy mix",
            "contribution_score": 85.0,
            "evidence": ["65% of energy from renewables", "Invested $2B in solar technology"],
            "metrics": {"renewable_percentage": 65.0}
        }
    })

    target_number: str = Field(..., description="SDG target number (e.g., 7.2)")
    target_description: str = Field(..., description="Description of the target")

    # Contribution
    contribution_score: float = Field(
        default=0.0,
        ge=0,
        le=100,
        description="Contribution to this target (0-100)"
    )
    contribution_type: Optional[ContributionType] = Field(None, description="Type of contribution")

    # Evidence
    evidence: List[str] = Field(default_factory=list, description="Evidence of contribution to target")
    metrics: Dict[str, float] = Field(default_factory=dict, description="Quantitative metrics")

    @field_validator('contribution_score')
    @classmethod
    def validate_contribution_score(cls, v: float) -> float:
        """Validate contribution score."""
        if not 0 <= v <= 100:
            raise ValueError("Contribution score must be between 0 and 100")
        return round(v, 2)


class SDGImpactMetric(BaseModel):
    """Quantified impact metric for SDG contribution."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "metric_id": "SDG-7-METRIC-001",
            "metric_name": "Renewable Energy Generated",
            "metric_description": "Total renewable energy generated annually",
            "value": 125000000,
            "unit": "MWh",
            "baseline_value": 85000000,
            "target_value": 150000000,
            "year": 2023,
            "verified": True
        }
    })

    metric_id: str = Field(..., description="Unique metric identifier")
    metric_name: str = Field(..., description="Name of the metric")
    metric_description: Optional[str] = Field(None, description="Description of what is measured")

    # Values
    value: float = Field(..., description="Current metric value")
    unit: str = Field(..., description="Unit of measurement")
    baseline_value: Optional[float] = Field(None, description="Baseline for comparison")
    target_value: Optional[float] = Field(None, description="Target value if applicable")

    # Context
    year: int = Field(..., ge=2000, le=2100, description="Year of measurement")
    geographic_scope: Optional[str] = Field(None, description="Geographic scope")
    measurement_period: Optional[str] = Field(None, description="Measurement period")

    # Quality
    verified: bool = Field(default=False, description="Whether third-party verified")
    data_source: Optional[str] = Field(None, description="Data source")
    confidence_score: Optional[float] = Field(None, ge=0, le=100, description="Confidence in metric")

    # Change Analysis
    year_over_year_change: Optional[float] = Field(None, description="Year-over-year change")
    percent_change: Optional[float] = Field(None, description="Percentage change")
    trend: Optional[str] = Field(None, description="Trend: improving, stable, declining")


class SDGContribution(BaseModel):
    """Company's contribution to a specific SDG goal."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "sdg_goal": 7,
            "goal_name": "Affordable and Clean Energy",
            "contribution_score": 88.5,
            "impact_type": "positive",
            "impact_magnitude": "significant",
            "contribution_type": "direct",
            "alignment_rationale": "Core business in renewable energy and electric vehicles",
            "targets": [],
            "impact_metrics": [],
            "strengths": ["Leading EV manufacturer", "Major solar energy producer"],
            "challenges": ["Limited energy storage solutions in some markets"],
            "confidence_score": 85.0
        }
    })

    # SDG Identification
    sdg_goal: int = Field(..., ge=1, le=17, description="SDG goal number (1-17)")
    goal_name: str = Field(..., description="Name of SDG goal")
    goal_description: Optional[str] = Field(None, description="Description of SDG goal")

    # Overall Contribution
    contribution_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Overall contribution score to this goal (0-100)"
    )
    impact_type: ImpactType = Field(..., description="Type of impact")
    impact_magnitude: ImpactMagnitude = Field(..., description="Magnitude of impact")
    contribution_type: ContributionType = Field(..., description="Type of contribution")

    # Rationale
    alignment_rationale: str = Field(..., description="Explanation of how company aligns with this SDG")
    alignment_examples: List[str] = Field(
        default_factory=list,
        description="Specific examples of alignment"
    )

    # Detailed Targets
    targets: List[SDGTarget] = Field(default_factory=list, description="Specific SDG targets addressed")
    primary_targets: List[str] = Field(
        default_factory=list,
        description="Primary target numbers (e.g., ['7.2', '7.3'])"
    )

    # Impact Metrics
    impact_metrics: List[SDGImpactMetric] = Field(
        default_factory=list,
        description="Quantified impact metrics"
    )

    # Qualitative Assessment
    strengths: List[str] = Field(default_factory=list, description="Key strengths in this area")
    challenges: List[str] = Field(default_factory=list, description="Challenges or limitations")
    opportunities: List[str] = Field(default_factory=list, description="Future opportunities")

    # Evidence
    evidence_ids: List[str] = Field(
        default_factory=list,
        description="IDs of supporting evidence items"
    )
    key_evidence: List[str] = Field(
        default_factory=list,
        description="Summary of key supporting evidence"
    )

    # Comparison
    industry_average_score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Industry average contribution score"
    )
    peer_percentile: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Percentile vs peers"
    )

    # Confidence
    confidence_score: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="Confidence in assessment (0-100)"
    )
    data_completeness: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Data completeness for this SDG"
    )

    # Temporal Analysis
    trend: Optional[str] = Field(None, description="Trend over time: improving, stable, declining")
    year_over_year_change: Optional[float] = Field(None, description="Year-over-year score change")

    # Metadata
    assessed_at: datetime = Field(default_factory=datetime.utcnow, description="Assessment timestamp")

    @field_validator('sdg_goal')
    @classmethod
    def validate_sdg_goal(cls, v: int) -> int:
        """Validate SDG goal number."""
        if not 1 <= v <= 17:
            raise ValueError("SDG goal must be between 1 and 17")
        return v

    @field_validator('contribution_score', 'confidence_score')
    @classmethod
    def validate_scores(cls, v: float) -> float:
        """Validate scores are in valid range."""
        if not 0 <= v <= 100:
            raise ValueError("Scores must be between 0 and 100")
        return round(v, 2)


class SDGAlignment(BaseModel):
    """Overall SDG alignment assessment for a company."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "alignment_id": "SDG-ALIGN-TSLA-20251223",
            "company_id": "TSLA-US",
            "company_name": "Tesla, Inc.",
            "overall_alignment_score": 78.5,
            "sdg_contributions": [],
            "primary_sdgs": [7, 9, 13],
            "secondary_sdgs": [8, 11, 12],
            "total_sdgs_aligned": 8,
            "confidence_score": 82.0,
            "assessed_at": "2025-12-23T10:30:00Z"
        }
    })

    # Identification
    alignment_id: str = Field(..., description="Unique alignment assessment identifier")
    company_id: str = Field(..., description="Company identifier")
    company_name: str = Field(..., description="Company name")

    # Overall Alignment
    overall_alignment_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Overall SDG alignment score (0-100)"
    )

    # Individual SDG Contributions
    sdg_contributions: List[SDGContribution] = Field(
        default_factory=list,
        description="Contributions to each SDG"
    )

    # SDG Categorization
    primary_sdgs: List[int] = Field(
        default_factory=list,
        description="Primary SDGs (contribution score > 60)"
    )
    secondary_sdgs: List[int] = Field(
        default_factory=list,
        description="Secondary SDGs (contribution score 30-60)"
    )
    minimal_sdgs: List[int] = Field(
        default_factory=list,
        description="SDGs with minimal contribution (score < 30)"
    )
    total_sdgs_aligned: int = Field(
        default=0,
        ge=0,
        le=17,
        description="Total number of SDGs with meaningful contribution"
    )

    # Impact Summary
    positive_impact_count: int = Field(default=0, ge=0, le=17, description="Number of SDGs with positive impact")
    negative_impact_count: int = Field(default=0, ge=0, le=17, description="Number of SDGs with negative impact")
    transformative_impact_count: int = Field(
        default=0,
        ge=0,
        le=17,
        description="Number of SDGs with transformative impact"
    )

    # Highlights
    top_sdg_contributions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Top 3-5 SDG contributions"
    )
    key_achievements: List[str] = Field(default_factory=list, description="Key SDG achievements")
    areas_for_improvement: List[str] = Field(default_factory=list, description="Areas for improvement")

    # Business Integration
    sdgs_in_strategy: List[int] = Field(
        default_factory=list,
        description="SDGs explicitly mentioned in corporate strategy"
    )
    sdgs_with_targets: List[int] = Field(
        default_factory=list,
        description="SDGs with quantified company targets"
    )
    business_model_alignment: Optional[str] = Field(
        None,
        description="How well business model aligns with SDGs"
    )

    # Sectoral Context
    industry_sdg_priorities: List[int] = Field(
        default_factory=list,
        description="Priority SDGs for this industry"
    )
    industry_average_score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Industry average SDG alignment score"
    )

    # Quality Metrics
    confidence_score: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="Overall confidence in SDG assessment"
    )
    data_quality_score: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="Data quality score"
    )
    coverage_completeness: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="Completeness of SDG coverage"
    )

    # Narrative
    executive_summary: Optional[str] = Field(
        None,
        max_length=1000,
        description="Executive summary of SDG alignment"
    )
    strategic_recommendations: List[str] = Field(
        default_factory=list,
        description="Strategic recommendations for SDG alignment"
    )

    # Metadata
    assessed_at: datetime = Field(default_factory=datetime.utcnow, description="Assessment timestamp")
    assessment_methodology: str = Field(
        default="1.0",
        description="Assessment methodology version"
    )

    @field_validator('overall_alignment_score', 'confidence_score', 'data_quality_score', 'coverage_completeness')
    @classmethod
    def validate_scores(cls, v: float) -> float:
        """Validate scores are in valid range."""
        if not 0 <= v <= 100:
            raise ValueError("Scores must be between 0 and 100")
        return round(v, 2)

    @field_validator('primary_sdgs', 'secondary_sdgs', 'minimal_sdgs', 'sdgs_in_strategy', 'sdgs_with_targets', 'industry_sdg_priorities')
    @classmethod
    def validate_sdg_lists(cls, v: List[int]) -> List[int]:
        """Validate SDG goal numbers in lists."""
        for goal in v:
            if not 1 <= goal <= 17:
                raise ValueError(f"SDG goal must be between 1 and 17, got {goal}")
        return v


class SDGReport(BaseModel):
    """Comprehensive SDG impact report."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "report_id": "SDG-REPORT-TSLA-20251223",
            "company_id": "TSLA-US",
            "company_name": "Tesla, Inc.",
            "reporting_period_start": "2023-01-01",
            "reporting_period_end": "2023-12-31",
            "sdg_alignment": {},
            "total_impact_score": 82.5,
            "report_summary": "Strong alignment with climate and energy SDGs",
            "generated_at": "2025-12-23T10:30:00Z"
        }
    })

    # Identification
    report_id: str = Field(..., description="Unique report identifier")
    company_id: str = Field(..., description="Company identifier")
    company_name: str = Field(..., description="Company name")

    # Reporting Period
    reporting_period_start: datetime = Field(..., description="Start of reporting period")
    reporting_period_end: datetime = Field(..., description="End of reporting period")

    # SDG Analysis
    sdg_alignment: SDGAlignment = Field(..., description="Comprehensive SDG alignment assessment")

    # Overall Impact
    total_impact_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Total SDG impact score (0-100)"
    )
    impact_rating: Optional[str] = Field(
        None,
        description="Impact rating: transformative, significant, moderate, limited"
    )

    # Detailed Breakdowns
    impact_by_category: Dict[str, float] = Field(
        default_factory=dict,
        description="Impact scores by SDG category (People, Planet, Prosperity, Peace, Partnership)"
    )

    # Highlights
    major_achievements: List[str] = Field(default_factory=list, description="Major SDG achievements")
    key_challenges: List[str] = Field(default_factory=list, description="Key challenges faced")
    future_commitments: List[str] = Field(default_factory=list, description="Future SDG commitments")

    # Comparative Analysis
    year_over_year_comparison: Optional[Dict[str, Any]] = Field(
        None,
        description="Comparison with previous reporting period"
    )
    peer_comparison: Optional[Dict[str, Any]] = Field(
        None,
        description="Comparison with industry peers"
    )

    # Report Narrative
    report_summary: str = Field(..., description="Executive summary of the report")
    detailed_narrative: Optional[str] = Field(None, description="Detailed narrative report")

    # Verification
    third_party_verified: bool = Field(default=False, description="Whether third-party verified")
    verification_body: Optional[str] = Field(None, description="Verification body if applicable")

    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Report generation timestamp")
    report_version: str = Field(default="1.0", description="Report version")
    methodology_framework: str = Field(
        default="UN SDG Impact Standards",
        description="Methodology framework used"
    )

    @field_validator('total_impact_score')
    @classmethod
    def validate_impact_score(cls, v: float) -> float:
        """Validate impact score."""
        if not 0 <= v <= 100:
            raise ValueError("Impact score must be between 0 and 100")
        return round(v, 2)
