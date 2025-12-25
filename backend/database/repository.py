"""
Repository Pattern Implementation for GAIA Database Operations
Provides clean interface for database operations.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import structlog

from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from .models import AnalysisHistory, CompanyCache

logger = structlog.get_logger()


class AnalysisRepository:
    """
    Repository for managing analysis history in the database.
    """

    def __init__(self, db: Session):
        self.db = db

    def save_analysis(self, analysis_data: Dict[str, Any]) -> AnalysisHistory:
        """
        Save a completed analysis to the database.

        Args:
            analysis_data: Dictionary containing analysis results

        Returns:
            Created AnalysisHistory object
        """
        # Extract ESG scores
        esg_scores = analysis_data.get("esg_scores", {})
        if not esg_scores:
            esg_scores = {
                "environmental": analysis_data.get("environmental_score"),
                "social": analysis_data.get("social_score"),
                "governance": analysis_data.get("governance_score"),
                "overall": analysis_data.get("overall_score"),
            }

        # Extract greenwashing data (handle None values safely)
        debate_summary = analysis_data.get("debate_summary") or {}
        greenwashing = debate_summary.get("greenwashing_signals", [])
        if not greenwashing:
            greenwashing = analysis_data.get("greenwashing_signals", [])

        # Extract blockchain data safely
        blockchain = analysis_data.get("blockchain") or {}

        # Create analysis history record
        analysis = AnalysisHistory(
            analysis_id=analysis_data.get("analysis_id"),
            ticker=(analysis_data.get("ticker") or "").upper(),
            company_name=analysis_data.get("company_name") or "",
            sector=analysis_data.get("sector"),
            industry=analysis_data.get("industry"),
            environmental_score=esg_scores.get("environmental"),
            social_score=esg_scores.get("social"),
            governance_score=esg_scores.get("governance"),
            overall_score=esg_scores.get("overall"),
            risk_level=analysis_data.get("risk_level"),
            recommendation=analysis_data.get("recommendation"),
            sdg_scores=analysis_data.get("sdg_impact"),
            top_sdgs=analysis_data.get("top_sdgs"),
            greenwashing_risk_score=analysis_data.get("greenwashing_risk_score"),
            greenwashing_signals_count=len(greenwashing) if greenwashing else 0,
            greenwashing_signals=greenwashing,
            debate_rounds=debate_summary.get("total_rounds", 0),
            debate_summary=debate_summary if debate_summary else None,
            consensus_reached=debate_summary.get("consensus_reached", True),
            agent_reports=analysis_data.get("agent_reports"),
            blockchain_hash=blockchain.get("latest_hash"),
            blockchain_transactions=blockchain.get("total_transactions", 0),
            full_results=analysis_data,
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            processing_time_seconds=analysis_data.get("processing_time_seconds"),
            status="completed",
        )

        try:
            self.db.add(analysis)
            self.db.commit()
            self.db.refresh(analysis)
            logger.info("analysis_saved", analysis_id=analysis.analysis_id, ticker=analysis.ticker)
            return analysis
        except Exception as e:
            self.db.rollback()
            logger.error("analysis_save_failed", error=str(e))
            raise

    def get_by_id(self, analysis_id: str) -> Optional[AnalysisHistory]:
        """Get analysis by its unique ID."""
        return self.db.query(AnalysisHistory).filter(
            AnalysisHistory.analysis_id == analysis_id
        ).first()

    def get_by_ticker(
        self,
        ticker: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[AnalysisHistory]:
        """Get all analyses for a specific ticker."""
        return self.db.query(AnalysisHistory).filter(
            AnalysisHistory.ticker == ticker.upper()
        ).order_by(
            desc(AnalysisHistory.created_at)
        ).offset(offset).limit(limit).all()

    def get_latest_by_ticker(self, ticker: str) -> Optional[AnalysisHistory]:
        """Get the most recent analysis for a ticker."""
        return self.db.query(AnalysisHistory).filter(
            AnalysisHistory.ticker == ticker.upper()
        ).order_by(
            desc(AnalysisHistory.created_at)
        ).first()

    def get_recent_analyses(
        self,
        limit: int = 20,
        offset: int = 0
    ) -> List[AnalysisHistory]:
        """Get most recent analyses across all companies."""
        return self.db.query(AnalysisHistory).order_by(
            desc(AnalysisHistory.created_at)
        ).offset(offset).limit(limit).all()

    def get_analyses_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        ticker: Optional[str] = None
    ) -> List[AnalysisHistory]:
        """Get analyses within a date range."""
        query = self.db.query(AnalysisHistory).filter(
            AnalysisHistory.created_at >= start_date,
            AnalysisHistory.created_at <= end_date
        )
        if ticker:
            query = query.filter(AnalysisHistory.ticker == ticker.upper())
        return query.order_by(desc(AnalysisHistory.created_at)).all()

    def get_analyses_by_risk_level(
        self,
        risk_level: str,
        limit: int = 20
    ) -> List[AnalysisHistory]:
        """Get analyses by risk level."""
        return self.db.query(AnalysisHistory).filter(
            AnalysisHistory.risk_level == risk_level.upper()
        ).order_by(
            desc(AnalysisHistory.created_at)
        ).limit(limit).all()

    def get_high_greenwashing_risk(
        self,
        min_signals: int = 2,
        limit: int = 20
    ) -> List[AnalysisHistory]:
        """Get analyses with high greenwashing signals."""
        return self.db.query(AnalysisHistory).filter(
            AnalysisHistory.greenwashing_signals_count >= min_signals
        ).order_by(
            desc(AnalysisHistory.greenwashing_signals_count)
        ).limit(limit).all()

    def get_unique_tickers(self) -> List[str]:
        """Get list of unique tickers that have been analyzed."""
        results = self.db.query(AnalysisHistory.ticker).distinct().all()
        return [r[0] for r in results]

    def get_analysis_count(self, ticker: Optional[str] = None) -> int:
        """Get total count of analyses."""
        query = self.db.query(func.count(AnalysisHistory.id))
        if ticker:
            query = query.filter(AnalysisHistory.ticker == ticker.upper())
        return query.scalar() or 0

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics about analyses."""
        total = self.get_analysis_count()
        unique_companies = len(self.get_unique_tickers())

        # Average scores
        avg_scores = self.db.query(
            func.avg(AnalysisHistory.overall_score),
            func.avg(AnalysisHistory.environmental_score),
            func.avg(AnalysisHistory.social_score),
            func.avg(AnalysisHistory.governance_score),
        ).first()

        # Risk distribution
        risk_dist = self.db.query(
            AnalysisHistory.risk_level,
            func.count(AnalysisHistory.id)
        ).group_by(AnalysisHistory.risk_level).all()

        # Recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_count = self.db.query(func.count(AnalysisHistory.id)).filter(
            AnalysisHistory.created_at >= week_ago
        ).scalar() or 0

        return {
            "total_analyses": total,
            "unique_companies": unique_companies,
            "analyses_last_7_days": recent_count,
            "average_scores": {
                "overall": round(avg_scores[0] or 0, 1),
                "environmental": round(avg_scores[1] or 0, 1),
                "social": round(avg_scores[2] or 0, 1),
                "governance": round(avg_scores[3] or 0, 1),
            },
            "risk_distribution": {
                level: count for level, count in risk_dist if level
            },
        }

    def delete_analysis(self, analysis_id: str) -> bool:
        """Delete an analysis by ID."""
        analysis = self.get_by_id(analysis_id)
        if analysis:
            self.db.delete(analysis)
            self.db.commit()
            logger.info("analysis_deleted", analysis_id=analysis_id)
            return True
        return False

    def delete_old_analyses(self, days: int = 90) -> int:
        """Delete analyses older than specified days."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        count = self.db.query(AnalysisHistory).filter(
            AnalysisHistory.created_at < cutoff
        ).delete()
        self.db.commit()
        logger.info("old_analyses_deleted", count=count, days=days)
        return count


class CompanyCacheRepository:
    """
    Repository for managing company cache.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_company(self, ticker: str) -> Optional[CompanyCache]:
        """Get cached company data."""
        return self.db.query(CompanyCache).filter(
            CompanyCache.ticker == ticker.upper()
        ).first()

    def save_company(self, company_data: Dict[str, Any]) -> CompanyCache:
        """Save or update company cache."""
        ticker = company_data.get("ticker", "").upper()
        existing = self.get_company(ticker)

        if existing:
            # Update existing
            for key, value in company_data.items():
                if hasattr(existing, key) and value is not None:
                    setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()
            company = existing
        else:
            # Create new
            company = CompanyCache(
                ticker=ticker,
                name=company_data.get("name"),
                description=company_data.get("description"),
                sector=company_data.get("sector"),
                industry=company_data.get("industry"),
                market_cap=company_data.get("market_cap"),
                pe_ratio=company_data.get("pe_ratio"),
                dividend_yield=company_data.get("dividend_yield"),
                extra_data=company_data.get("extra_data"),
            )
            self.db.add(company)

        self.db.commit()
        self.db.refresh(company)
        return company

    def get_all_companies(self) -> List[CompanyCache]:
        """Get all cached companies."""
        return self.db.query(CompanyCache).all()
