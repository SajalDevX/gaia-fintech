"""
GAIA Companies Routes
Company management and search endpoints
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import structlog

from services.analysis_service import AnalysisService, get_analysis_service
from config import get_settings

logger = structlog.get_logger()
settings = get_settings()

router = APIRouter()


# Request/Response Models

class CompanySearchRequest(BaseModel):
    """Request model for company search."""
    query: str = Field(..., description="Search query (company name or ticker)", min_length=1)
    limit: int = Field(10, description="Maximum number of results", ge=1, le=100)
    include_analysis: bool = Field(False, description="Include latest analysis data")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Apple",
                "limit": 10,
                "include_analysis": True
            }
        }


class CompanyInfo(BaseModel):
    """Basic company information."""
    ticker: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    market_cap: Optional[float] = None
    employees: Optional[int] = None
    website: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None


class CompanyAnalysisSummary(BaseModel):
    """Summary of company analysis."""
    analysis_id: str
    ticker: str
    overall_score: float
    risk_level: str
    recommendation: str
    esg_scores: Dict[str, float]
    top_sdgs: List[Dict[str, Any]]
    created_at: datetime
    last_updated: datetime


class CompanyDetails(BaseModel):
    """Detailed company information with analysis history."""
    info: CompanyInfo
    analysis_history: List[CompanyAnalysisSummary] = Field(default_factory=list)
    latest_analysis: Optional[CompanyAnalysisSummary] = None
    total_analyses: int = 0


class CompanyListItem(BaseModel):
    """Company list item with summary."""
    ticker: str
    name: str
    sector: Optional[str] = None
    latest_score: Optional[float] = None
    latest_risk_level: Optional[str] = None
    last_analyzed: Optional[datetime] = None
    total_analyses: int = 0


class CompanyListResponse(BaseModel):
    """Response model for company listing."""
    companies: List[CompanyListItem]
    total: int
    page: int
    page_size: int
    has_more: bool


# Routes

@router.get("", response_model=CompanyListResponse)
async def list_companies(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    min_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum overall score"),
    max_score: Optional[float] = Query(None, ge=0, le=100, description="Maximum overall score"),
    sort_by: str = Query("last_analyzed", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    List all analyzed companies with filtering and pagination.

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        sector: Filter by sector
        risk_level: Filter by risk level (CRITICAL, HIGH, MODERATE, LOW, MINIMAL)
        min_score: Minimum overall score filter
        max_score: Maximum overall score filter
        sort_by: Field to sort by (last_analyzed, score, name, ticker)
        sort_order: Sort order (asc, desc)
        analysis_service: Injected analysis service

    Returns:
        CompanyListResponse with paginated company list

    Raises:
        HTTPException: If query parameters are invalid
    """
    try:
        logger.info(
            "listing_companies",
            page=page,
            page_size=page_size,
            sector=sector,
            risk_level=risk_level
        )

        # Validate sort order
        if sort_order not in ["asc", "desc"]:
            raise ValueError("sort_order must be 'asc' or 'desc'")

        # Validate sort field
        valid_sort_fields = ["last_analyzed", "score", "name", "ticker", "total_analyses"]
        if sort_by not in valid_sort_fields:
            raise ValueError(f"sort_by must be one of: {', '.join(valid_sort_fields)}")

        # Get companies from service
        companies, total = await analysis_service.list_companies(
            page=page,
            page_size=page_size,
            sector=sector,
            risk_level=risk_level,
            min_score=min_score,
            max_score=max_score,
            sort_by=sort_by,
            sort_order=sort_order
        )

        # Calculate pagination info
        has_more = (page * page_size) < total

        return CompanyListResponse(
            companies=companies,
            total=total,
            page=page,
            page_size=page_size,
            has_more=has_more
        )

    except ValueError as e:
        logger.warning("invalid_query_parameters", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error("list_companies_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch companies"
        )


@router.get("/{ticker}", response_model=CompanyDetails)
async def get_company_details(
    ticker: str,
    include_history: bool = Query(True, description="Include analysis history"),
    history_limit: int = Query(10, ge=1, le=50, description="Max history items"),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Get detailed information about a specific company.

    Args:
        ticker: Company stock ticker symbol
        include_history: Whether to include analysis history
        history_limit: Maximum number of historical analyses to return
        analysis_service: Injected analysis service

    Returns:
        CompanyDetails with complete company information

    Raises:
        HTTPException: If company not found
    """
    try:
        ticker = ticker.upper().strip()
        logger.info("fetching_company_details", ticker=ticker)

        details = await analysis_service.get_company_details(
            ticker=ticker,
            include_history=include_history,
            history_limit=history_limit
        )

        if not details:
            raise HTTPException(
                status_code=404,
                detail=f"Company with ticker '{ticker}' not found"
            )

        return details

    except HTTPException:
        raise

    except Exception as e:
        logger.error("company_details_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch company details"
        )


@router.post("/search", response_model=List[CompanyInfo])
async def search_companies(
    request: CompanySearchRequest,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Search for companies by name or ticker.

    This endpoint searches both the local database and external sources
    to find matching companies.

    Args:
        request: Search request parameters
        analysis_service: Injected analysis service

    Returns:
        List of matching companies

    Raises:
        HTTPException: If search fails
    """
    try:
        logger.info(
            "searching_companies",
            query=request.query,
            limit=request.limit
        )

        results = await analysis_service.search_companies(
            query=request.query,
            limit=request.limit,
            include_analysis=request.include_analysis
        )

        return results

    except Exception as e:
        logger.error("company_search_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to search companies"
        )


@router.get("/{ticker}/timeline")
async def get_company_timeline(
    ticker: str,
    start_date: Optional[datetime] = Query(None, description="Start date for timeline"),
    end_date: Optional[datetime] = Query(None, description="End date for timeline"),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Get timeline of company's ESG/SDG scores over time.

    Args:
        ticker: Company stock ticker symbol
        start_date: Optional start date filter
        end_date: Optional end date filter
        analysis_service: Injected analysis service

    Returns:
        Timeline data with score evolution

    Raises:
        HTTPException: If company not found
    """
    try:
        ticker = ticker.upper().strip()
        logger.info("fetching_company_timeline", ticker=ticker)

        timeline = await analysis_service.get_company_timeline(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date
        )

        if not timeline:
            raise HTTPException(
                status_code=404,
                detail=f"No timeline data found for ticker '{ticker}'"
            )

        return timeline

    except HTTPException:
        raise

    except Exception as e:
        logger.error("timeline_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch company timeline"
        )


@router.get("/{ticker}/compare")
async def compare_companies(
    ticker: str,
    compare_with: List[str] = Query(..., description="Tickers to compare with"),
    metrics: Optional[List[str]] = Query(None, description="Specific metrics to compare"),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Compare a company with others on ESG/SDG metrics.

    Args:
        ticker: Primary company ticker
        compare_with: List of tickers to compare against
        metrics: Optional list of specific metrics to compare
        analysis_service: Injected analysis service

    Returns:
        Comparison data across companies

    Raises:
        HTTPException: If any company not found
    """
    try:
        ticker = ticker.upper().strip()
        compare_with = [t.upper().strip() for t in compare_with]

        logger.info(
            "comparing_companies",
            ticker=ticker,
            compare_with=compare_with
        )

        if len(compare_with) > 10:
            raise ValueError("Cannot compare more than 10 companies at once")

        comparison = await analysis_service.compare_companies(
            ticker=ticker,
            compare_with=compare_with,
            metrics=metrics
        )

        return comparison

    except ValueError as e:
        logger.warning("invalid_comparison_request", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))

    except HTTPException:
        raise

    except Exception as e:
        logger.error("comparison_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to compare companies"
        )


@router.get("/{ticker}/peers")
async def get_company_peers(
    ticker: str,
    limit: int = Query(5, ge=1, le=20, description="Number of peers to return"),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Get peer companies (same sector/industry) for comparison.

    Args:
        ticker: Company stock ticker symbol
        limit: Maximum number of peers to return
        analysis_service: Injected analysis service

    Returns:
        List of peer companies with comparison data

    Raises:
        HTTPException: If company not found
    """
    try:
        ticker = ticker.upper().strip()
        logger.info("fetching_company_peers", ticker=ticker, limit=limit)

        peers = await analysis_service.get_company_peers(
            ticker=ticker,
            limit=limit
        )

        return peers

    except HTTPException:
        raise

    except Exception as e:
        logger.error("peers_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch company peers"
        )


@router.delete("/{ticker}", status_code=204)
async def delete_company(
    ticker: str,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Delete a company and all its analysis data.

    Args:
        ticker: Company stock ticker symbol
        analysis_service: Injected analysis service

    Raises:
        HTTPException: If company not found or deletion fails
    """
    try:
        ticker = ticker.upper().strip()
        logger.info("deleting_company", ticker=ticker)

        success = await analysis_service.delete_company(ticker)

        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Company with ticker '{ticker}' not found"
            )

        logger.info("company_deleted", ticker=ticker)

    except HTTPException:
        raise

    except Exception as e:
        logger.error("delete_company_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to delete company"
        )


@router.get("/{ticker}/satellite-data")
async def get_company_satellite_data(
    ticker: str,
    date_range: Optional[int] = Query(90, description="Days of historical data"),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Get satellite imagery analysis data for company facilities.

    Args:
        ticker: Company stock ticker symbol
        date_range: Number of days of historical data
        analysis_service: Injected analysis service

    Returns:
        Satellite data analysis results

    Raises:
        HTTPException: If company not found or no satellite data available
    """
    try:
        ticker = ticker.upper().strip()
        logger.info("fetching_satellite_data", ticker=ticker)

        satellite_data = await analysis_service.get_satellite_data(
            ticker=ticker,
            date_range=date_range
        )

        if not satellite_data:
            raise HTTPException(
                status_code=404,
                detail=f"No satellite data available for ticker '{ticker}'"
            )

        return satellite_data

    except HTTPException:
        raise

    except Exception as e:
        logger.error("satellite_data_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch satellite data"
        )
