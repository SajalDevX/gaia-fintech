"""
Analysis History API Routes for GAIA
Provides endpoints for accessing past analysis data.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db, AnalysisRepository
from database.models import AnalysisHistory

router = APIRouter(tags=["History"])


# Response Models
class AnalysisSummary(BaseModel):
    """Summary of an analysis for list views."""
    analysis_id: str
    ticker: str
    company_name: str
    overall_score: Optional[float]
    risk_level: Optional[str]
    recommendation: Optional[str]
    greenwashing_signals_count: int
    created_at: Optional[str]
    status: str

    class Config:
        from_attributes = True


class AnalysisDetail(BaseModel):
    """Detailed analysis response."""
    id: int
    analysis_id: str
    ticker: str
    company_name: str
    sector: Optional[str]
    industry: Optional[str]
    esg_scores: dict
    risk_level: Optional[str]
    recommendation: Optional[str]
    sdg_scores: Optional[dict]
    top_sdgs: Optional[list]
    greenwashing: dict
    debate: dict
    blockchain_hash: Optional[str]
    created_at: Optional[str]
    completed_at: Optional[str]
    processing_time_seconds: Optional[float]
    status: str

    class Config:
        from_attributes = True


class HistoryStats(BaseModel):
    """Statistics about analysis history."""
    total_analyses: int
    unique_companies: int
    analyses_last_7_days: int
    average_scores: dict
    risk_distribution: dict


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    items: List[AnalysisSummary]
    total: int
    page: int
    page_size: int
    has_more: bool


@router.get("/", response_model=PaginatedResponse)
async def get_analysis_history(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    ticker: Optional[str] = Query(None, description="Filter by ticker"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    db: Session = Depends(get_db)
):
    """
    Get paginated analysis history.

    Supports filtering by ticker and risk level.
    """
    repo = AnalysisRepository(db)
    offset = (page - 1) * page_size

    if ticker:
        analyses = repo.get_by_ticker(ticker, limit=page_size, offset=offset)
        total = repo.get_analysis_count(ticker)
    elif risk_level:
        analyses = repo.get_analyses_by_risk_level(risk_level, limit=page_size)
        total = len(analyses)
    else:
        analyses = repo.get_recent_analyses(limit=page_size, offset=offset)
        total = repo.get_analysis_count()

    items = [AnalysisSummary(**a.to_summary_dict()) for a in analyses]

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(offset + page_size) < total
    )


@router.get("/recent", response_model=List[AnalysisSummary])
async def get_recent_analyses(
    limit: int = Query(10, ge=1, le=50, description="Number of analyses"),
    db: Session = Depends(get_db)
):
    """
    Get the most recent analyses.
    Quick endpoint for dashboard display.
    """
    repo = AnalysisRepository(db)
    analyses = repo.get_recent_analyses(limit=limit)
    return [AnalysisSummary(**a.to_summary_dict()) for a in analyses]


@router.get("/stats", response_model=HistoryStats)
async def get_history_stats(db: Session = Depends(get_db)):
    """
    Get statistics about analysis history.
    Useful for dashboard metrics.
    """
    repo = AnalysisRepository(db)
    stats = repo.get_statistics()
    return HistoryStats(**stats)


@router.get("/companies", response_model=List[str])
async def get_analyzed_companies(db: Session = Depends(get_db)):
    """
    Get list of all companies that have been analyzed.
    """
    repo = AnalysisRepository(db)
    return repo.get_unique_tickers()


@router.get("/greenwashing-alerts", response_model=List[AnalysisSummary])
async def get_greenwashing_alerts(
    min_signals: int = Query(2, ge=1, description="Minimum greenwashing signals"),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get analyses with greenwashing alerts.
    Useful for compliance monitoring.
    """
    repo = AnalysisRepository(db)
    analyses = repo.get_high_greenwashing_risk(min_signals=min_signals, limit=limit)
    return [AnalysisSummary(**a.to_summary_dict()) for a in analyses]


@router.get("/ticker/{ticker}", response_model=List[AnalysisSummary])
async def get_analyses_by_ticker(
    ticker: str,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get all analyses for a specific company ticker.
    Shows analysis history for one company.
    """
    repo = AnalysisRepository(db)
    analyses = repo.get_by_ticker(ticker.upper(), limit=limit)
    return [AnalysisSummary(**a.to_summary_dict()) for a in analyses]


@router.get("/ticker/{ticker}/latest")
async def get_latest_analysis(
    ticker: str,
    db: Session = Depends(get_db)
):
    """
    Get the most recent analysis for a specific ticker.
    """
    repo = AnalysisRepository(db)
    analysis = repo.get_latest_by_ticker(ticker.upper())

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=f"No analysis found for ticker {ticker.upper()}"
        )

    return analysis.to_dict()


@router.get("/{analysis_id}")
async def get_analysis_detail(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """
    Get full details of a specific analysis.
    """
    repo = AnalysisRepository(db)
    analysis = repo.get_by_id(analysis_id)

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis {analysis_id} not found"
        )

    # Return full results if available
    if analysis.full_results:
        return {
            **analysis.to_dict(),
            "full_results": analysis.full_results
        }

    return analysis.to_dict()


@router.get("/{analysis_id}/full")
async def get_full_analysis_results(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """
    Get complete stored results for an analysis.
    """
    repo = AnalysisRepository(db)
    analysis = repo.get_by_id(analysis_id)

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis {analysis_id} not found"
        )

    if not analysis.full_results:
        raise HTTPException(
            status_code=404,
            detail="Full results not available for this analysis"
        )

    return analysis.full_results


@router.delete("/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete an analysis from history.
    """
    repo = AnalysisRepository(db)

    if not repo.delete_analysis(analysis_id):
        raise HTTPException(
            status_code=404,
            detail=f"Analysis {analysis_id} not found"
        )

    return {"message": f"Analysis {analysis_id} deleted successfully"}


@router.get("/compare/{ticker1}/{ticker2}")
async def compare_companies(
    ticker1: str,
    ticker2: str,
    db: Session = Depends(get_db)
):
    """
    Compare the latest analyses of two companies.
    """
    repo = AnalysisRepository(db)

    analysis1 = repo.get_latest_by_ticker(ticker1.upper())
    analysis2 = repo.get_latest_by_ticker(ticker2.upper())

    if not analysis1:
        raise HTTPException(
            status_code=404,
            detail=f"No analysis found for ticker {ticker1.upper()}"
        )

    if not analysis2:
        raise HTTPException(
            status_code=404,
            detail=f"No analysis found for ticker {ticker2.upper()}"
        )

    return {
        "company1": analysis1.to_dict(),
        "company2": analysis2.to_dict(),
        "comparison": {
            "overall_score_diff": (analysis1.overall_score or 0) - (analysis2.overall_score or 0),
            "environmental_diff": (analysis1.environmental_score or 0) - (analysis2.environmental_score or 0),
            "social_diff": (analysis1.social_score or 0) - (analysis2.social_score or 0),
            "governance_diff": (analysis1.governance_score or 0) - (analysis2.governance_score or 0),
            "greenwashing_signals_diff": (analysis1.greenwashing_signals_count or 0) - (analysis2.greenwashing_signals_count or 0),
        }
    }
