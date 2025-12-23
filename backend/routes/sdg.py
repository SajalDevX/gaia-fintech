"""
GAIA SDG Routes
Sustainable Development Goals analysis endpoints
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import structlog

from services.analysis_service import AnalysisService, get_analysis_service
from config import get_settings, SDG_GOALS

logger = structlog.get_logger()
settings = get_settings()

router = APIRouter()


# Request/Response Models

class SDGImpactScore(BaseModel):
    """SDG impact score for a specific goal."""
    sdg_number: int = Field(..., ge=1, le=17)
    sdg_name: str
    impact_score: float = Field(..., ge=-100, le=100, description="Impact score (-100 to 100)")
    confidence: float = Field(..., ge=0, le=100, description="Confidence percentage")
    sentiment: str = Field(..., description="positive, negative, or neutral")
    evidence: List[str] = Field(default_factory=list)
    related_activities: List[str] = Field(default_factory=list)


class SDGImpactResponse(BaseModel):
    """Complete SDG impact analysis for a company."""
    ticker: str
    company_name: str
    analysis_id: Optional[str] = None
    overall_sdg_score: float = Field(..., ge=-100, le=100)
    sdg_impacts: List[SDGImpactScore]
    top_positive_impacts: List[Dict[str, Any]]
    top_negative_impacts: List[Dict[str, Any]]
    sdg_alignment_summary: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class PortfolioSDGRequest(BaseModel):
    """Request model for portfolio SDG analysis."""
    tickers: List[str] = Field(..., min_items=1, max_items=50, description="List of company tickers")
    weights: Optional[Dict[str, float]] = Field(None, description="Optional portfolio weights")

    class Config:
        json_schema_extra = {
            "example": {
                "tickers": ["AAPL", "MSFT", "GOOGL"],
                "weights": {
                    "AAPL": 0.4,
                    "MSFT": 0.35,
                    "GOOGL": 0.25
                }
            }
        }


class PortfolioSDGImpact(BaseModel):
    """Portfolio-level SDG impact."""
    sdg_number: int
    sdg_name: str
    portfolio_impact: float
    contributing_companies: List[Dict[str, Any]]


class PortfolioSDGResponse(BaseModel):
    """Complete portfolio SDG analysis."""
    portfolio_name: Optional[str] = None
    total_companies: int
    overall_portfolio_score: float
    sdg_impacts: List[PortfolioSDGImpact]
    diversification_score: float
    sustainability_grade: str
    recommendations: List[str]
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class SDGGoalInfo(BaseModel):
    """Information about a specific SDG goal."""
    number: int
    name: str
    description: str
    targets: int
    color: str
    icon: str


# Routes

@router.get("/goals", response_model=List[SDGGoalInfo])
async def get_sdg_goals():
    """
    Get information about all 17 Sustainable Development Goals.

    Returns:
        List of SDG goals with metadata

    """
    try:
        logger.info("fetching_sdg_goals")

        goals = []
        for num, goal_data in SDG_GOALS.items():
            goals.append(SDGGoalInfo(
                number=num,
                name=goal_data["name"],
                description=f"SDG {num}: {goal_data['name']}",
                targets=0,  # TODO: Add actual target counts
                color=goal_data["color"],
                icon=goal_data["icon"]
            ))

        return goals

    except Exception as e:
        logger.error("sdg_goals_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch SDG goals"
        )


@router.get("/impact/{ticker}", response_model=SDGImpactResponse)
async def get_sdg_impact(
    ticker: str,
    analysis_id: Optional[str] = Query(None, description="Specific analysis ID (default: latest)"),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Get SDG impact analysis for a specific company.

    Args:
        ticker: Company stock ticker symbol
        analysis_id: Optional specific analysis ID (uses latest if not provided)
        analysis_service: Injected analysis service

    Returns:
        SDGImpactResponse with detailed SDG impact analysis

    Raises:
        HTTPException: If company not found or no analysis available
    """
    try:
        ticker = ticker.upper().strip()
        logger.info("fetching_sdg_impact", ticker=ticker, analysis_id=analysis_id)

        impact = await analysis_service.get_sdg_impact(
            ticker=ticker,
            analysis_id=analysis_id
        )

        if not impact:
            raise HTTPException(
                status_code=404,
                detail=f"No SDG analysis found for ticker '{ticker}'"
            )

        return impact

    except HTTPException:
        raise

    except Exception as e:
        logger.error("sdg_impact_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch SDG impact"
        )


@router.post("/portfolio", response_model=PortfolioSDGResponse)
async def analyze_portfolio_sdg(
    request: PortfolioSDGRequest,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Analyze SDG impact for a portfolio of companies.

    This endpoint aggregates SDG impacts across multiple companies,
    optionally weighted, to provide portfolio-level insights.

    Args:
        request: Portfolio analysis request with tickers and optional weights
        analysis_service: Injected analysis service

    Returns:
        PortfolioSDGResponse with aggregated SDG analysis

    Raises:
        HTTPException: If companies not found or analysis fails
    """
    try:
        # Normalize tickers
        tickers = [t.upper().strip() for t in request.tickers]

        logger.info("analyzing_portfolio_sdg", tickers=tickers)

        # Validate weights if provided
        if request.weights:
            # Normalize weights
            weights = {k.upper(): v for k, v in request.weights.items()}

            # Check that all tickers have weights
            if set(tickers) != set(weights.keys()):
                raise ValueError("Weights must be provided for all tickers")

            # Check that weights sum to ~1.0
            total_weight = sum(weights.values())
            if not (0.99 <= total_weight <= 1.01):
                raise ValueError(f"Weights must sum to 1.0 (current sum: {total_weight})")
        else:
            # Equal weights
            weights = {ticker: 1.0 / len(tickers) for ticker in tickers}

        # Get portfolio analysis
        portfolio_analysis = await analysis_service.analyze_portfolio_sdg(
            tickers=tickers,
            weights=weights
        )

        return portfolio_analysis

    except ValueError as e:
        logger.warning("invalid_portfolio_request", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error("portfolio_sdg_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze portfolio SDG impact"
        )


@router.get("/impact/{ticker}/goal/{sdg_number}")
async def get_sdg_goal_detail(
    ticker: str,
    sdg_number: int = Path(..., ge=1, le=17),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Get detailed analysis for a specific SDG goal and company.

    Args:
        ticker: Company stock ticker symbol
        sdg_number: SDG goal number (1-17)
        analysis_service: Injected analysis service

    Returns:
        Detailed SDG goal analysis

    Raises:
        HTTPException: If company not found or invalid SDG number
    """
    try:
        ticker = ticker.upper().strip()
        logger.info("fetching_sdg_goal_detail", ticker=ticker, sdg_number=sdg_number)

        if sdg_number < 1 or sdg_number > 17:
            raise ValueError("SDG number must be between 1 and 17")

        detail = await analysis_service.get_sdg_goal_detail(
            ticker=ticker,
            sdg_number=sdg_number
        )

        if not detail:
            raise HTTPException(
                status_code=404,
                detail=f"No SDG {sdg_number} analysis found for ticker '{ticker}'"
            )

        return detail

    except ValueError as e:
        logger.warning("invalid_sdg_number", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))

    except HTTPException:
        raise

    except Exception as e:
        logger.error("sdg_goal_detail_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch SDG goal detail"
        )


@router.get("/impact/{ticker}/timeline")
async def get_sdg_timeline(
    ticker: str,
    sdg_number: Optional[int] = Query(None, ge=1, le=17, description="Specific SDG goal"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Get timeline of SDG impacts over time for a company.

    Args:
        ticker: Company stock ticker symbol
        sdg_number: Optional specific SDG goal number
        start_date: Optional start date filter
        end_date: Optional end date filter
        analysis_service: Injected analysis service

    Returns:
        Timeline of SDG impacts

    Raises:
        HTTPException: If company not found
    """
    try:
        ticker = ticker.upper().strip()
        logger.info(
            "fetching_sdg_timeline",
            ticker=ticker,
            sdg_number=sdg_number
        )

        timeline = await analysis_service.get_sdg_timeline(
            ticker=ticker,
            sdg_number=sdg_number,
            start_date=start_date,
            end_date=end_date
        )

        if not timeline:
            raise HTTPException(
                status_code=404,
                detail=f"No SDG timeline data found for ticker '{ticker}'"
            )

        return timeline

    except HTTPException:
        raise

    except Exception as e:
        logger.error("sdg_timeline_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch SDG timeline"
        )


@router.get("/sector/{sector}/impact")
async def get_sector_sdg_impact(
    sector: str,
    limit: int = Query(10, ge=1, le=50, description="Number of companies"),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Get aggregated SDG impact analysis for a sector.

    Args:
        sector: Industry sector name
        limit: Maximum number of companies to include
        analysis_service: Injected analysis service

    Returns:
        Sector-level SDG impact analysis

    Raises:
        HTTPException: If sector not found
    """
    try:
        logger.info("fetching_sector_sdg_impact", sector=sector, limit=limit)

        sector_impact = await analysis_service.get_sector_sdg_impact(
            sector=sector,
            limit=limit
        )

        if not sector_impact:
            raise HTTPException(
                status_code=404,
                detail=f"No SDG data found for sector '{sector}'"
            )

        return sector_impact

    except HTTPException:
        raise

    except Exception as e:
        logger.error("sector_sdg_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch sector SDG impact"
        )


@router.get("/benchmarks")
async def get_sdg_benchmarks(
    sector: Optional[str] = Query(None, description="Filter by sector"),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Get SDG impact benchmarks for comparison.

    Args:
        sector: Optional sector filter
        analysis_service: Injected analysis service

    Returns:
        SDG benchmarks data

    Raises:
        HTTPException: If benchmarks unavailable
    """
    try:
        logger.info("fetching_sdg_benchmarks", sector=sector)

        benchmarks = await analysis_service.get_sdg_benchmarks(sector=sector)

        return benchmarks

    except Exception as e:
        logger.error("sdg_benchmarks_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch SDG benchmarks"
        )


@router.get("/impact/{ticker}/recommendations")
async def get_sdg_recommendations(
    ticker: str,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Get SDG improvement recommendations for a company.

    Args:
        ticker: Company stock ticker symbol
        analysis_service: Injected analysis service

    Returns:
        Actionable SDG improvement recommendations

    Raises:
        HTTPException: If company not found
    """
    try:
        ticker = ticker.upper().strip()
        logger.info("fetching_sdg_recommendations", ticker=ticker)

        recommendations = await analysis_service.get_sdg_recommendations(ticker=ticker)

        if not recommendations:
            raise HTTPException(
                status_code=404,
                detail=f"No SDG recommendations available for ticker '{ticker}'"
            )

        return recommendations

    except HTTPException:
        raise

    except Exception as e:
        logger.error("sdg_recommendations_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch SDG recommendations"
        )


@router.post("/compare")
async def compare_sdg_impacts(
    tickers: List[str] = Query(..., min_items=2, max_items=10, description="Company tickers to compare"),
    sdg_number: Optional[int] = Query(None, ge=1, le=17, description="Specific SDG to compare"),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Compare SDG impacts across multiple companies.

    Args:
        tickers: List of company tickers to compare
        sdg_number: Optional specific SDG goal to focus on
        analysis_service: Injected analysis service

    Returns:
        Comparative SDG analysis

    Raises:
        HTTPException: If companies not found
    """
    try:
        tickers = [t.upper().strip() for t in tickers]
        logger.info("comparing_sdg_impacts", tickers=tickers, sdg_number=sdg_number)

        comparison = await analysis_service.compare_sdg_impacts(
            tickers=tickers,
            sdg_number=sdg_number
        )

        return comparison

    except Exception as e:
        logger.error("sdg_comparison_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to compare SDG impacts"
        )
