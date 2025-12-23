"""
Financial Inclusion Data Models for GAIA

Comprehensive models for measuring financial inclusion impact across
underserved populations - addressing SDG 1, 5, 8, 9, 10.

Design Philosophy:
- Every metric quantifiable per dollar invested
- Intersectional analysis (gender, geography, age, disability)
- Global applicability across different market contexts
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class UnderservedSegment(str, Enum):
    """Categories of underserved populations"""
    UNBANKED = "unbanked"
    UNDERBANKED = "underbanked"
    WOMEN = "women"
    RURAL = "rural"
    YOUTH = "youth"
    ELDERLY = "elderly"
    REFUGEES = "refugees"
    DISABLED = "disabled"
    INFORMAL_WORKERS = "informal_workers"
    SMALLHOLDER_FARMERS = "smallholder_farmers"
    MICRO_ENTREPRENEURS = "micro_entrepreneurs"
    LOW_INCOME = "low_income"


class InclusionChannel(str, Enum):
    """Financial service delivery channels"""
    MOBILE_MONEY = "mobile_money"
    AGENT_BANKING = "agent_banking"
    DIGITAL_WALLET = "digital_wallet"
    MICROFINANCE = "microfinance"
    COMMUNITY_BANKING = "community_banking"
    COOPERATIVE = "cooperative"
    FINTECH_APP = "fintech_app"
    BNPL = "buy_now_pay_later"  # Buy Now Pay Later
    PAYGO = "pay_as_you_go"  # Pay-as-you-go financing


class InclusionRiskLevel(str, Enum):
    """Risk levels for inclusion washing (similar to greenwashing)"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================================
# ACCESS METRICS - Who can access financial services?
# ============================================================

class AccessMetrics(BaseModel):
    """
    Measures basic access to financial services.
    Key question: "Can underserved populations reach and use financial services?"
    """
    # Population reach
    unbanked_individuals_reached_per_million: float = Field(
        default=0.0,
        description="Number of previously unbanked individuals gaining account access per $1M invested"
    )
    new_accounts_opened_per_million: float = Field(
        default=0.0,
        description="New financial accounts opened per $1M invested"
    )
    active_users_per_million: float = Field(
        default=0.0,
        description="Monthly active users of financial services per $1M invested"
    )

    # Digital access
    mobile_money_users_enabled_per_million: float = Field(
        default=0.0,
        description="New mobile money users per $1M invested"
    )
    digital_payment_points_created_per_million: float = Field(
        default=0.0,
        description="New digital payment access points per $1M invested"
    )
    smartphone_penetration_increase: float = Field(
        default=0.0,
        description="Percentage increase in smartphone-based financial access"
    )

    # Physical access
    last_mile_agents_deployed_per_million: float = Field(
        default=0.0,
        description="Banking agents deployed in underserved areas per $1M"
    )
    average_distance_to_access_point_km: float = Field(
        default=0.0,
        description="Average distance reduction to nearest financial access point"
    )

    # Overall score
    access_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Composite access score (0-100)"
    )


# ============================================================
# CREDIT METRICS - Who can borrow affordably?
# ============================================================

class CreditMetrics(BaseModel):
    """
    Measures access to credit for underserved populations.
    Key question: "Can those who need credit get it at fair terms?"
    """
    # Microlending
    microloans_disbursed_per_million: int = Field(
        default=0,
        description="Number of microloans disbursed per $1M invested"
    )
    average_microloan_size_usd: float = Field(
        default=0.0,
        description="Average microloan size in USD"
    )
    first_time_borrowers_per_million: int = Field(
        default=0,
        description="First-time borrowers served per $1M invested"
    )

    # Small business lending
    sme_loans_to_underserved_per_million: int = Field(
        default=0,
        description="SME loans to underserved entrepreneurs per $1M"
    )
    informal_business_formalization_rate: float = Field(
        default=0.0,
        description="Rate of informal businesses gaining formal credit access"
    )

    # Affordability
    average_interest_rate_vs_market: float = Field(
        default=0.0,
        description="Interest rate compared to market average (negative = below market)"
    )
    interest_rate_fairness_index: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Fairness of interest rates (0-100, higher = fairer)"
    )

    # Alternative credit scoring
    alternative_data_credit_scores_enabled: int = Field(
        default=0,
        description="People with no traditional credit history now scoreable per $1M"
    )
    credit_approval_rate_underserved: float = Field(
        default=0.0,
        description="Credit approval rate for underserved applicants (%)"
    )

    # Repayment & sustainability
    portfolio_at_risk_30_days: float = Field(
        default=0.0,
        description="Portfolio at risk >30 days (%)"
    )
    client_retention_rate: float = Field(
        default=0.0,
        description="Client retention rate (%)"
    )

    credit_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Composite credit inclusion score (0-100)"
    )


# ============================================================
# GENDER INCLUSION METRICS - SDG 5 Focus
# ============================================================

class GenderInclusionMetrics(BaseModel):
    """
    Measures gender-based financial inclusion.
    Key question: "Are women equally served by financial services?"
    """
    # Women's access
    women_account_holders_per_million: int = Field(
        default=0,
        description="Women gaining financial accounts per $1M invested"
    )
    women_entrepreneurs_funded_per_million: int = Field(
        default=0,
        description="Women entrepreneurs receiving funding per $1M"
    )
    female_headed_household_loans_per_million: int = Field(
        default=0,
        description="Loans to female-headed households per $1M"
    )

    # Parity metrics
    gender_parity_index: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Ratio of women to men accessing services (1.0 = parity)"
    )
    women_in_leadership_percent: float = Field(
        default=0.0,
        description="Women in company leadership positions (%)"
    )
    women_loan_officers_percent: float = Field(
        default=0.0,
        description="Women employed as loan officers (%)"
    )

    # Women-specific products
    has_women_focused_products: bool = Field(
        default=False,
        description="Offers financial products designed for women"
    )
    maternity_friendly_loan_terms: bool = Field(
        default=False,
        description="Offers maternity-friendly repayment terms"
    )
    women_savings_groups_supported: int = Field(
        default=0,
        description="Women's savings groups supported per $1M"
    )

    # Impact
    women_economic_empowerment_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Women's economic empowerment score (0-100)"
    )

    gender_inclusion_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Composite gender inclusion score (0-100)"
    )


# ============================================================
# GEOGRAPHIC INCLUSION METRICS
# ============================================================

class GeographicInclusionMetrics(BaseModel):
    """
    Measures geographic financial inclusion.
    Key question: "Are rural and remote populations served?"
    """
    # Rural reach
    rural_population_coverage_percent: float = Field(
        default=0.0,
        description="Percentage of rural population with financial access"
    )
    rural_branches_per_100k_population: float = Field(
        default=0.0,
        description="Financial service points per 100,000 rural population"
    )
    rural_agents_deployed_per_million: int = Field(
        default=0,
        description="Banking agents in rural areas per $1M invested"
    )

    # Remote and last-mile
    last_mile_communities_reached: int = Field(
        default=0,
        description="Previously unserved remote communities reached per $1M"
    )
    average_travel_time_reduction_minutes: float = Field(
        default=0.0,
        description="Reduction in average travel time to financial services"
    )

    # Urban underserved
    urban_slum_coverage_percent: float = Field(
        default=0.0,
        description="Percentage of urban slum population with access"
    )
    informal_settlement_agents: int = Field(
        default=0,
        description="Agents in informal settlements per $1M"
    )

    # Cross-border
    remittance_corridors_served: int = Field(
        default=0,
        description="Cross-border remittance corridors with reduced fees"
    )
    remittance_cost_reduction_percent: float = Field(
        default=0.0,
        description="Reduction in remittance costs (%)"
    )

    geographic_inclusion_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Composite geographic inclusion score (0-100)"
    )


# ============================================================
# VULNERABLE POPULATION METRICS
# ============================================================

class VulnerablePopulationMetrics(BaseModel):
    """
    Measures financial inclusion for vulnerable populations.
    Key question: "Are the most vulnerable populations protected and served?"
    """
    # Refugees and displaced persons
    refugees_served_per_million: int = Field(
        default=0,
        description="Refugees/displaced persons with financial access per $1M"
    )
    has_refugee_specific_products: bool = Field(
        default=False,
        description="Offers products for refugees without traditional ID"
    )

    # Disability inclusion
    disability_accessible_branches_percent: float = Field(
        default=0.0,
        description="Percentage of branches with disability accessibility"
    )
    has_screen_reader_compatible_app: bool = Field(
        default=False,
        description="Mobile app compatible with screen readers"
    )
    has_sign_language_support: bool = Field(
        default=False,
        description="Offers sign language customer support"
    )

    # Youth inclusion
    youth_accounts_per_million: int = Field(
        default=0,
        description="Youth financial accounts opened per $1M"
    )
    financial_literacy_programs_youth: int = Field(
        default=0,
        description="Youth reached through financial literacy per $1M"
    )

    # Elderly inclusion
    elderly_friendly_services: bool = Field(
        default=False,
        description="Services designed for elderly users"
    )
    pension_disbursement_digitized: bool = Field(
        default=False,
        description="Supports digital pension disbursement"
    )

    # Informal workers
    gig_worker_financial_products: bool = Field(
        default=False,
        description="Products designed for gig/informal workers"
    )
    informal_workers_formalized_per_million: int = Field(
        default=0,
        description="Informal workers gaining formal financial identity per $1M"
    )

    vulnerable_population_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Composite vulnerable population inclusion score (0-100)"
    )


# ============================================================
# AFFORDABILITY METRICS
# ============================================================

class AffordabilityMetrics(BaseModel):
    """
    Measures affordability of financial services.
    Key question: "Can low-income populations afford these services?"
    """
    # Account affordability
    has_zero_balance_accounts: bool = Field(
        default=False,
        description="Offers accounts with no minimum balance"
    )
    has_zero_fee_basic_account: bool = Field(
        default=False,
        description="Offers basic account with no monthly fees"
    )
    average_monthly_fee_usd: float = Field(
        default=0.0,
        description="Average monthly account fee in USD"
    )

    # Transaction affordability
    transaction_fee_percent_of_min_wage: float = Field(
        default=0.0,
        description="Average transaction fee as % of daily minimum wage"
    )
    free_transactions_per_month: int = Field(
        default=0,
        description="Number of free transactions allowed monthly"
    )

    # Credit affordability
    effective_annual_rate_microloans: float = Field(
        default=0.0,
        description="Effective annual interest rate on microloans (%)"
    )
    has_flexible_repayment: bool = Field(
        default=False,
        description="Offers flexible repayment schedules"
    )
    grace_period_days: int = Field(
        default=0,
        description="Grace period before late fees (days)"
    )

    # Transparency
    fee_transparency_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Fee transparency and disclosure score (0-100)"
    )
    has_plain_language_terms: bool = Field(
        default=False,
        description="Terms and conditions in plain language"
    )
    available_in_local_languages: int = Field(
        default=0,
        description="Number of local languages supported"
    )

    affordability_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Composite affordability score (0-100)"
    )


# ============================================================
# INCLUSION WASHING DETECTION
# ============================================================

class InclusionWashingIndicator(BaseModel):
    """
    Indicators of potential "inclusion washing" - false claims about
    serving underserved populations (similar to greenwashing).
    """
    indicator_name: str
    description: str
    severity: InclusionRiskLevel
    evidence: str
    recommendation: str


class InclusionWashingAnalysis(BaseModel):
    """Complete inclusion washing risk analysis"""
    risk_level: InclusionRiskLevel
    risk_score: float = Field(ge=0.0, le=100.0)
    indicators: List[InclusionWashingIndicator] = []

    # Red flags
    claims_vs_reality_gap: float = Field(
        default=0.0,
        description="Gap between marketing claims and actual metrics (%)"
    )
    cherry_picked_metrics: bool = Field(
        default=False,
        description="Evidence of selectively reported metrics"
    )
    vulnerable_population_exploitation_risk: bool = Field(
        default=False,
        description="Risk of exploiting vulnerable populations"
    )
    predatory_lending_indicators: bool = Field(
        default=False,
        description="Indicators of predatory lending practices"
    )

    summary: str = ""
    recommendations: List[str] = []


# ============================================================
# COMPOSITE FINANCIAL INCLUSION REPORT
# ============================================================

class FinancialInclusionScore(BaseModel):
    """Overall financial inclusion score with breakdown"""
    overall_score: float = Field(ge=0.0, le=100.0)

    # Component scores
    access_score: float = Field(ge=0.0, le=100.0)
    credit_score: float = Field(ge=0.0, le=100.0)
    gender_score: float = Field(ge=0.0, le=100.0)
    geographic_score: float = Field(ge=0.0, le=100.0)
    vulnerable_population_score: float = Field(ge=0.0, le=100.0)
    affordability_score: float = Field(ge=0.0, le=100.0)

    # Weighting used
    weights: Dict[str, float] = Field(
        default={
            "access": 0.20,
            "credit": 0.20,
            "gender": 0.15,
            "geographic": 0.15,
            "vulnerable": 0.15,
            "affordability": 0.15
        }
    )

    # Grade
    grade: str = Field(
        default="",
        description="Letter grade (A+ to F)"
    )

    # Percentile ranking
    percentile_rank: float = Field(
        default=0.0,
        description="Percentile rank compared to industry"
    )


class FinancialInclusionReport(BaseModel):
    """
    Complete Financial Inclusion Analysis Report

    This is the primary output of the NEXUS Agent, providing
    comprehensive analysis of a company's financial inclusion impact.
    """
    # Identification
    company_ticker: str
    company_name: str
    analysis_date: datetime = Field(default_factory=datetime.utcnow)
    analysis_id: str

    # Overall assessment
    inclusion_score: FinancialInclusionScore
    inclusion_washing_analysis: InclusionWashingAnalysis

    # Detailed metrics
    access_metrics: AccessMetrics
    credit_metrics: CreditMetrics
    gender_metrics: GenderInclusionMetrics
    geographic_metrics: GeographicInclusionMetrics
    vulnerable_metrics: VulnerablePopulationMetrics
    affordability_metrics: AffordabilityMetrics

    # Segments served
    primary_segments_served: List[UnderservedSegment] = []
    channels_utilized: List[InclusionChannel] = []

    # Impact summary
    total_lives_impacted_per_million: int = Field(
        default=0,
        description="Total lives positively impacted per $1M invested"
    )

    # SDG alignment
    sdg_alignment: Dict[int, float] = Field(
        default={},
        description="Alignment scores for relevant SDGs (1, 5, 8, 9, 10)"
    )

    # Key findings
    strengths: List[str] = []
    weaknesses: List[str] = []
    opportunities: List[str] = []
    risks: List[str] = []

    # Recommendations
    recommendations: List[str] = []

    # Confidence and methodology
    confidence_level: float = Field(ge=0.0, le=1.0)
    data_sources: List[str] = []
    methodology_notes: str = ""


class InclusionPortfolioAnalysis(BaseModel):
    """Portfolio-level financial inclusion analysis"""
    portfolio_id: str
    analysis_date: datetime = Field(default_factory=datetime.utcnow)

    # Portfolio metrics
    total_holdings: int
    total_value_usd: float

    # Aggregate scores
    weighted_inclusion_score: float = Field(ge=0.0, le=100.0)
    inclusion_coverage_percent: float = Field(
        description="Percentage of portfolio with inclusion data"
    )

    # Impact aggregation
    total_lives_impacted: int
    women_impacted: int
    rural_population_impacted: int
    youth_impacted: int

    # Per million invested
    lives_per_million_usd: float
    women_entrepreneurs_per_million_usd: float
    microloans_per_million_usd: float

    # Top performers
    top_inclusion_performers: List[Dict[str, Any]] = []
    inclusion_laggards: List[Dict[str, Any]] = []

    # Recommendations
    portfolio_recommendations: List[str] = []


class InclusionBenchmark(BaseModel):
    """Industry benchmarks for financial inclusion metrics"""
    industry: str
    region: str
    benchmark_date: datetime

    # Benchmark values
    average_inclusion_score: float
    median_inclusion_score: float
    top_quartile_threshold: float
    bottom_quartile_threshold: float

    # Component benchmarks
    access_benchmark: float
    credit_benchmark: float
    gender_benchmark: float
    geographic_benchmark: float
    vulnerable_benchmark: float
    affordability_benchmark: float

    # Leaders
    industry_leaders: List[str] = []
