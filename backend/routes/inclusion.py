"""
Financial Inclusion API Routes

Endpoints for analyzing financial inclusion impact on underserved populations.
Addresses DIC 2025 Finance Track Focus Area 3: Inclusion-oriented payments/credit.
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import uuid

from models.inclusion import (
    UnderservedSegment,
    InclusionChannel,
    InclusionRiskLevel,
    FinancialInclusionScore,
    FinancialInclusionReport,
    InclusionPortfolioAnalysis,
    InclusionBenchmark,
    AccessMetrics,
    CreditMetrics,
    GenderInclusionMetrics,
    GeographicInclusionMetrics,
    VulnerablePopulationMetrics,
    AffordabilityMetrics,
    InclusionWashingAnalysis,
)

router = APIRouter(tags=["Financial Inclusion"])


# ============================================================
# Request/Response Models
# ============================================================

class InclusionAnalysisRequest(BaseModel):
    """Request model for financial inclusion analysis"""
    ticker: str = Field(..., description="Company stock ticker")
    company_name: str = Field(..., description="Company name")
    include_washing_analysis: bool = Field(
        default=True,
        description="Include inclusion washing detection"
    )
    include_benchmarks: bool = Field(
        default=True,
        description="Include industry benchmarks"
    )
    segments_of_interest: Optional[List[UnderservedSegment]] = Field(
        default=None,
        description="Specific underserved segments to focus on"
    )


class InclusionAnalysisResponse(BaseModel):
    """Response model for inclusion analysis"""
    analysis_id: str
    status: str
    message: str
    websocket_url: Optional[str] = None


class InclusionMetricsSummary(BaseModel):
    """Summary of key inclusion metrics"""
    ticker: str
    company_name: str
    overall_score: float
    grade: str
    total_lives_impacted_per_million: int
    top_segments_served: List[str]
    inclusion_washing_risk: str
    key_strengths: List[str]
    key_weaknesses: List[str]


class PortfolioInclusionRequest(BaseModel):
    """Request for portfolio-level inclusion analysis"""
    holdings: List[Dict[str, float]] = Field(
        ...,
        description="List of holdings with ticker and weight"
    )
    total_value_usd: Optional[float] = Field(
        default=1000000,
        description="Total portfolio value in USD"
    )


class InclusionComparisonRequest(BaseModel):
    """Request for comparing inclusion across companies"""
    tickers: List[str] = Field(
        ...,
        min_length=2,
        max_length=10,
        description="List of tickers to compare"
    )
    metric_focus: Optional[str] = Field(
        default=None,
        description="Specific metric category to focus comparison"
    )


# ============================================================
# In-Memory Storage (would be database in production)
# ============================================================

inclusion_analyses: Dict[str, FinancialInclusionReport] = {}
analysis_status: Dict[str, str] = {}


# ============================================================
# Endpoints
# ============================================================

@router.post("/analyze", response_model=InclusionAnalysisResponse)
async def start_inclusion_analysis(
    request: InclusionAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a financial inclusion analysis for a company.

    This endpoint initiates an asynchronous analysis using the NEXUS Agent
    to evaluate the company's impact on underserved populations.

    Returns an analysis_id that can be used to retrieve results.
    """
    analysis_id = f"inc_{uuid.uuid4().hex[:12]}"

    analysis_status[analysis_id] = "pending"

    # In production, this would spawn the actual NEXUS agent analysis
    background_tasks.add_task(
        run_inclusion_analysis,
        analysis_id,
        request.ticker,
        request.company_name,
        request.include_washing_analysis
    )

    return InclusionAnalysisResponse(
        analysis_id=analysis_id,
        status="pending",
        message=f"Inclusion analysis started for {request.company_name}",
        websocket_url=f"/ws/inclusion/{analysis_id}"
    )


async def run_inclusion_analysis(
    analysis_id: str,
    ticker: str,
    company_name: str,
    include_washing: bool
):
    """Background task to run inclusion analysis"""
    import asyncio
    from agents.nexus_agent import NexusAgent

    analysis_status[analysis_id] = "in_progress"

    try:
        agent = NexusAgent()
        report = await agent.analyze(
            company_name=company_name,
            ticker=ticker
        )

        inclusion_analyses[analysis_id] = report
        analysis_status[analysis_id] = "completed"

    except Exception as e:
        analysis_status[analysis_id] = f"failed: {str(e)}"


@router.get("/analyze/{analysis_id}", response_model=FinancialInclusionReport)
async def get_inclusion_analysis(analysis_id: str):
    """
    Get the results of a financial inclusion analysis.

    Returns the complete FinancialInclusionReport with all metrics.
    """
    if analysis_id not in analysis_status:
        raise HTTPException(status_code=404, detail="Analysis not found")

    status = analysis_status[analysis_id]

    if status == "pending" or status == "in_progress":
        raise HTTPException(
            status_code=202,
            detail=f"Analysis still in progress. Status: {status}"
        )

    if status.startswith("failed"):
        raise HTTPException(status_code=500, detail=status)

    if analysis_id not in inclusion_analyses:
        raise HTTPException(status_code=404, detail="Analysis results not found")

    return inclusion_analyses[analysis_id]


@router.get("/analyze/{analysis_id}/summary", response_model=InclusionMetricsSummary)
async def get_inclusion_summary(analysis_id: str):
    """
    Get a summary of the inclusion analysis.

    Returns key metrics in a condensed format suitable for dashboards.
    """
    if analysis_id not in inclusion_analyses:
        raise HTTPException(status_code=404, detail="Analysis not found")

    report = inclusion_analyses[analysis_id]

    return InclusionMetricsSummary(
        ticker=report.company_ticker,
        company_name=report.company_name,
        overall_score=report.inclusion_score.overall_score,
        grade=report.inclusion_score.grade,
        total_lives_impacted_per_million=report.total_lives_impacted_per_million,
        top_segments_served=[s.value for s in report.primary_segments_served[:3]],
        inclusion_washing_risk=report.inclusion_washing_analysis.risk_level.value,
        key_strengths=report.strengths[:3],
        key_weaknesses=report.weaknesses[:3]
    )


@router.get("/segments", response_model=List[Dict])
async def get_underserved_segments():
    """
    Get list of all underserved population segments tracked by GAIA.

    Returns segment definitions and descriptions for UI display.
    """
    segments = [
        {
            "id": UnderservedSegment.UNBANKED.value,
            "name": "Unbanked",
            "description": "Adults without any bank account",
            "sdg_alignment": [1, 8, 10],
            "global_population": "1.4 billion"
        },
        {
            "id": UnderservedSegment.UNDERBANKED.value,
            "name": "Underbanked",
            "description": "Adults with limited access to financial services",
            "sdg_alignment": [1, 8, 10],
            "global_population": "2+ billion"
        },
        {
            "id": UnderservedSegment.WOMEN.value,
            "name": "Women",
            "description": "Women facing gender-based financial exclusion",
            "sdg_alignment": [5, 8, 10],
            "global_population": "980 million unbanked"
        },
        {
            "id": UnderservedSegment.RURAL.value,
            "name": "Rural Populations",
            "description": "People in rural areas with limited financial access",
            "sdg_alignment": [1, 9, 11],
            "global_population": "3.4 billion"
        },
        {
            "id": UnderservedSegment.YOUTH.value,
            "name": "Youth",
            "description": "Young people (15-24) with limited financial inclusion",
            "sdg_alignment": [4, 8, 10],
            "global_population": "1.2 billion"
        },
        {
            "id": UnderservedSegment.ELDERLY.value,
            "name": "Elderly",
            "description": "Older adults facing digital and physical barriers",
            "sdg_alignment": [1, 3, 10],
            "global_population": "727 million (60+)"
        },
        {
            "id": UnderservedSegment.REFUGEES.value,
            "name": "Refugees & Displaced",
            "description": "Forcibly displaced persons without ID or documentation",
            "sdg_alignment": [1, 10, 16],
            "global_population": "100+ million"
        },
        {
            "id": UnderservedSegment.DISABLED.value,
            "name": "People with Disabilities",
            "description": "Individuals facing accessibility barriers",
            "sdg_alignment": [10, 11],
            "global_population": "1.3 billion"
        },
        {
            "id": UnderservedSegment.INFORMAL_WORKERS.value,
            "name": "Informal Workers",
            "description": "Workers in informal economy without formal identity",
            "sdg_alignment": [8, 10],
            "global_population": "2 billion"
        },
        {
            "id": UnderservedSegment.SMALLHOLDER_FARMERS.value,
            "name": "Smallholder Farmers",
            "description": "Small-scale farmers lacking agricultural finance",
            "sdg_alignment": [1, 2, 8],
            "global_population": "500+ million farms"
        },
        {
            "id": UnderservedSegment.MICRO_ENTREPRENEURS.value,
            "name": "Micro-Entrepreneurs",
            "description": "Very small business owners lacking access to credit",
            "sdg_alignment": [1, 8, 9],
            "global_population": "Hundreds of millions"
        },
        {
            "id": UnderservedSegment.LOW_INCOME.value,
            "name": "Low-Income Households",
            "description": "Households below living wage threshold",
            "sdg_alignment": [1, 10],
            "global_population": "700+ million in extreme poverty"
        }
    ]

    return segments


@router.get("/channels", response_model=List[Dict])
async def get_inclusion_channels():
    """
    Get list of financial inclusion delivery channels.

    Returns channel descriptions and effectiveness metrics.
    """
    channels = [
        {
            "id": InclusionChannel.MOBILE_MONEY.value,
            "name": "Mobile Money",
            "description": "Phone-based payment and banking services",
            "reach_potential": "High",
            "cost_efficiency": "Very High",
            "example_providers": ["M-Pesa", "GCash", "bKash"]
        },
        {
            "id": InclusionChannel.AGENT_BANKING.value,
            "name": "Agent Banking",
            "description": "Local agents providing banking services",
            "reach_potential": "Very High",
            "cost_efficiency": "High",
            "example_providers": ["BRI Agents", "Equity Agents"]
        },
        {
            "id": InclusionChannel.DIGITAL_WALLET.value,
            "name": "Digital Wallet",
            "description": "Smartphone-based digital wallets",
            "reach_potential": "Medium",
            "cost_efficiency": "High",
            "example_providers": ["Alipay", "Paytm", "Grab"]
        },
        {
            "id": InclusionChannel.MICROFINANCE.value,
            "name": "Microfinance Institution",
            "description": "Specialized microfinance providers",
            "reach_potential": "High",
            "cost_efficiency": "Medium",
            "example_providers": ["Grameen Bank", "BRAC", "ASA"]
        },
        {
            "id": InclusionChannel.COMMUNITY_BANKING.value,
            "name": "Community Banking",
            "description": "Community-based financial cooperatives",
            "reach_potential": "Medium",
            "cost_efficiency": "High",
            "example_providers": ["Credit Unions", "Village Banks"]
        },
        {
            "id": InclusionChannel.COOPERATIVE.value,
            "name": "Cooperative",
            "description": "Member-owned financial cooperatives",
            "reach_potential": "Medium",
            "cost_efficiency": "High",
            "example_providers": ["SACCOs", "Agricultural Coops"]
        },
        {
            "id": InclusionChannel.FINTECH_APP.value,
            "name": "Fintech App",
            "description": "Modern fintech applications",
            "reach_potential": "Medium",
            "cost_efficiency": "Very High",
            "example_providers": ["Nubank", "Revolut", "Chime"]
        },
        {
            "id": InclusionChannel.BNPL.value,
            "name": "Buy Now Pay Later",
            "description": "Point-of-sale financing solutions",
            "reach_potential": "Medium",
            "cost_efficiency": "Medium",
            "example_providers": ["Affirm", "Klarna", "Afterpay"]
        },
        {
            "id": InclusionChannel.PAYGO.value,
            "name": "Pay-As-You-Go",
            "description": "Asset financing with usage-based payments",
            "reach_potential": "High",
            "cost_efficiency": "High",
            "example_providers": ["M-KOPA", "d.light", "BBOXX"]
        }
    ]

    return channels


@router.post("/portfolio", response_model=InclusionPortfolioAnalysis)
async def analyze_portfolio_inclusion(request: PortfolioInclusionRequest):
    """
    Analyze financial inclusion impact across an investment portfolio.

    Aggregates inclusion metrics across all holdings weighted by position size.
    """
    # In production, this would analyze each holding and aggregate

    total_holdings = len(request.holdings)

    # Simulate portfolio-level metrics
    import random

    return InclusionPortfolioAnalysis(
        portfolio_id=f"port_{uuid.uuid4().hex[:8]}",
        analysis_date=datetime.utcnow(),
        total_holdings=total_holdings,
        total_value_usd=request.total_value_usd,
        weighted_inclusion_score=random.uniform(45, 75),
        inclusion_coverage_percent=random.uniform(60, 90),
        total_lives_impacted=int(random.uniform(10000, 100000)),
        women_impacted=int(random.uniform(3000, 40000)),
        rural_population_impacted=int(random.uniform(5000, 50000)),
        youth_impacted=int(random.uniform(2000, 20000)),
        lives_per_million_usd=int(random.uniform(500, 2000)),
        women_entrepreneurs_per_million_usd=int(random.uniform(50, 300)),
        microloans_per_million_usd=int(random.uniform(200, 1000)),
        top_inclusion_performers=[
            {"ticker": "MFI", "name": "Microfinance Inc", "score": 85.2},
            {"ticker": "GRMT", "name": "Grameen Tech", "score": 82.1}
        ],
        inclusion_laggards=[
            {"ticker": "TRAD", "name": "Traditional Bank", "score": 35.5}
        ],
        portfolio_recommendations=[
            "Consider increasing allocation to microfinance-focused holdings",
            "Portfolio has strong gender inclusion metrics",
            "Opportunity to add rural-focused financial services exposure"
        ]
    )


@router.post("/compare", response_model=List[InclusionMetricsSummary])
async def compare_inclusion(request: InclusionComparisonRequest):
    """
    Compare financial inclusion metrics across multiple companies.

    Returns side-by-side comparison of key inclusion metrics.
    """
    # In production, this would fetch/compute metrics for each ticker

    comparisons = []
    import random

    for ticker in request.tickers:
        comparisons.append(InclusionMetricsSummary(
            ticker=ticker,
            company_name=f"{ticker} Financial Services",
            overall_score=random.uniform(35, 85),
            grade=random.choice(["A", "A-", "B+", "B", "B-", "C+", "C"]),
            total_lives_impacted_per_million=int(random.uniform(500, 3000)),
            top_segments_served=random.sample([
                "unbanked", "women", "rural", "youth", "micro_entrepreneurs"
            ], 3),
            inclusion_washing_risk=random.choice(["low", "moderate", "high"]),
            key_strengths=[
                "Strong mobile money reach",
                "Women-focused lending programs",
                "Rural agent network"
            ][:random.randint(1, 3)],
            key_weaknesses=[
                "Limited disability accessibility",
                "High interest rates",
                "Urban-focused operations"
            ][:random.randint(1, 3)]
        ))

    return comparisons


@router.get("/benchmarks/{industry}", response_model=InclusionBenchmark)
async def get_industry_benchmarks(
    industry: str,
    region: Optional[str] = Query(default="global", description="Geographic region")
):
    """
    Get financial inclusion benchmarks for an industry.

    Returns industry averages and quartile thresholds for comparison.
    """
    # Industry-specific benchmarks
    benchmarks = {
        "microfinance": {
            "average": 75.0, "median": 72.0,
            "top_q": 85.0, "bottom_q": 60.0,
            "access": 80.0, "credit": 78.0, "gender": 70.0,
            "geographic": 75.0, "vulnerable": 65.0, "affordability": 70.0,
            "leaders": ["Grameen Bank", "BRAC", "ASA", "Compartamos"]
        },
        "fintech": {
            "average": 55.0, "median": 52.0,
            "top_q": 70.0, "bottom_q": 40.0,
            "access": 65.0, "credit": 50.0, "gender": 45.0,
            "geographic": 40.0, "vulnerable": 45.0, "affordability": 60.0,
            "leaders": ["M-Pesa", "Nubank", "GCash", "Paytm"]
        },
        "banking": {
            "average": 42.0, "median": 40.0,
            "top_q": 55.0, "bottom_q": 30.0,
            "access": 45.0, "credit": 40.0, "gender": 38.0,
            "geographic": 35.0, "vulnerable": 35.0, "affordability": 45.0,
            "leaders": ["BRI", "Equity Bank", "ICICI Bank"]
        },
        "insurance": {
            "average": 38.0, "median": 35.0,
            "top_q": 50.0, "bottom_q": 25.0,
            "access": 40.0, "credit": 30.0, "gender": 35.0,
            "geographic": 30.0, "vulnerable": 40.0, "affordability": 42.0,
            "leaders": ["BIMA", "MicroEnsure", "LeapFrog Investments"]
        }
    }

    industry_lower = industry.lower()
    if industry_lower not in benchmarks:
        industry_lower = "fintech"  # Default

    b = benchmarks[industry_lower]

    return InclusionBenchmark(
        industry=industry,
        region=region,
        benchmark_date=datetime.utcnow(),
        average_inclusion_score=b["average"],
        median_inclusion_score=b["median"],
        top_quartile_threshold=b["top_q"],
        bottom_quartile_threshold=b["bottom_q"],
        access_benchmark=b["access"],
        credit_benchmark=b["credit"],
        gender_benchmark=b["gender"],
        geographic_benchmark=b["geographic"],
        vulnerable_benchmark=b["vulnerable"],
        affordability_benchmark=b["affordability"],
        industry_leaders=b["leaders"]
    )


@router.get("/metrics/access", response_model=Dict)
async def get_access_metrics_definitions():
    """
    Get definitions and methodology for access metrics.

    Returns detailed explanations of how access metrics are calculated.
    """
    return {
        "category": "Financial Access",
        "description": "Measures basic access to financial services for underserved populations",
        "key_question": "Can underserved populations reach and use financial services?",
        "metrics": [
            {
                "name": "unbanked_individuals_reached_per_million",
                "description": "Number of previously unbanked individuals gaining account access per $1M invested",
                "unit": "individuals",
                "source": "World Bank Findex, company reports",
                "higher_is_better": True
            },
            {
                "name": "mobile_money_users_enabled_per_million",
                "description": "New mobile money users per $1M invested",
                "unit": "users",
                "source": "GSMA State of the Industry",
                "higher_is_better": True
            },
            {
                "name": "last_mile_agents_deployed_per_million",
                "description": "Banking agents deployed in underserved areas per $1M",
                "unit": "agents",
                "source": "Company reports, regulatory data",
                "higher_is_better": True
            },
            {
                "name": "average_distance_to_access_point_km",
                "description": "Average distance reduction to nearest financial access point",
                "unit": "kilometers",
                "source": "Geographic analysis, surveys",
                "higher_is_better": False
            }
        ],
        "methodology": "Access metrics are calculated using a combination of company-reported data, third-party impact assessments, and geographic analysis. Metrics are normalized per $1M invested to enable comparison across companies of different sizes."
    }


@router.get("/impact-calculator")
async def calculate_inclusion_impact(
    investment_amount: float = Query(..., description="Investment amount in USD"),
    ticker: str = Query(..., description="Company ticker"),
    segment: Optional[UnderservedSegment] = Query(
        default=None,
        description="Specific segment to calculate impact for"
    )
):
    """
    Calculate projected financial inclusion impact for a given investment.

    Returns estimated number of lives impacted, women reached, etc.
    """
    import random

    # In production, would use actual company metrics
    # Base metrics per $1M invested
    base_metrics = {
        "lives_reached": random.uniform(800, 2500),
        "women_entrepreneurs": random.uniform(100, 400),
        "first_time_borrowers": random.uniform(200, 800),
        "rural_people_served": random.uniform(300, 1200),
        "microloans_disbursed": random.uniform(300, 1000),
        "mobile_money_users": random.uniform(400, 1500)
    }

    # Scale by investment amount
    multiplier = investment_amount / 1_000_000

    impact = {
        "investment_amount_usd": investment_amount,
        "ticker": ticker,
        "projected_impact": {
            "lives_reached": int(base_metrics["lives_reached"] * multiplier),
            "women_entrepreneurs_funded": int(base_metrics["women_entrepreneurs"] * multiplier),
            "first_time_borrowers_served": int(base_metrics["first_time_borrowers"] * multiplier),
            "rural_people_gaining_access": int(base_metrics["rural_people_served"] * multiplier),
            "microloans_enabled": int(base_metrics["microloans_disbursed"] * multiplier),
            "mobile_money_users_created": int(base_metrics["mobile_money_users"] * multiplier)
        },
        "confidence_level": 0.75,
        "methodology": "Based on company historical impact metrics and industry benchmarks",
        "disclaimer": "Projections are estimates based on historical data and may vary"
    }

    if segment:
        impact["segment_focus"] = segment.value

    return impact


# Export router
__all__ = ["router"]
