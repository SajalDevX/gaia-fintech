"""
SQLAlchemy Database Models for GAIA
Stores analysis history, company cache, and related data.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    Boolean,
    JSON,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AnalysisHistory(Base):
    """
    Stores completed analysis results for historical reference.
    Each row represents one complete analysis run for a company.
    """
    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(String(64), unique=True, nullable=False, index=True)

    # Company Information
    ticker = Column(String(10), nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)

    # ESG Scores
    environmental_score = Column(Float, nullable=True)
    social_score = Column(Float, nullable=True)
    governance_score = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True)

    # Risk Assessment
    risk_level = Column(String(20), nullable=True)  # MINIMAL, LOW, MODERATE, HIGH, CRITICAL
    recommendation = Column(String(20), nullable=True)  # STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL

    # SDG Impact (stored as JSON)
    sdg_scores = Column(JSON, nullable=True)  # {"1": 75.5, "7": 82.3, ...}
    top_sdgs = Column(JSON, nullable=True)  # [{"goal": 7, "score": 82.3}, ...]

    # Greenwashing Detection
    greenwashing_risk_score = Column(Float, nullable=True)
    greenwashing_signals_count = Column(Integer, default=0)
    greenwashing_signals = Column(JSON, nullable=True)  # List of signals

    # Debate Information
    debate_rounds = Column(Integer, default=0)
    debate_summary = Column(JSON, nullable=True)
    consensus_reached = Column(Boolean, default=True)

    # Agent Reports (stored as JSON)
    agent_reports = Column(JSON, nullable=True)

    # Blockchain
    blockchain_hash = Column(String(128), nullable=True)
    blockchain_transactions = Column(Integer, default=0)

    # Full Results (for detailed view)
    full_results = Column(JSON, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    processing_time_seconds = Column(Float, nullable=True)
    status = Column(String(20), default="completed")  # completed, failed, partial
    error_message = Column(Text, nullable=True)

    # Indexes for common queries
    __table_args__ = (
        Index('idx_ticker_created', 'ticker', 'created_at'),
        Index('idx_overall_score', 'overall_score'),
        Index('idx_risk_level', 'risk_level'),
    )

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "ticker": self.ticker,
            "company_name": self.company_name,
            "sector": self.sector,
            "industry": self.industry,
            "esg_scores": {
                "environmental": self.environmental_score,
                "social": self.social_score,
                "governance": self.governance_score,
                "overall": self.overall_score,
            },
            "risk_level": self.risk_level,
            "recommendation": self.recommendation,
            "sdg_scores": self.sdg_scores,
            "top_sdgs": self.top_sdgs,
            "greenwashing": {
                "risk_score": self.greenwashing_risk_score,
                "signals_count": self.greenwashing_signals_count,
                "signals": self.greenwashing_signals,
            },
            "debate": {
                "rounds": self.debate_rounds,
                "consensus_reached": self.consensus_reached,
                "summary": self.debate_summary,
            },
            "blockchain_hash": self.blockchain_hash,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "processing_time_seconds": self.processing_time_seconds,
            "status": self.status,
        }

    def to_summary_dict(self) -> dict:
        """Convert to summary dictionary for list views."""
        return {
            "analysis_id": self.analysis_id,
            "ticker": self.ticker,
            "company_name": self.company_name,
            "overall_score": self.overall_score,
            "risk_level": self.risk_level,
            "recommendation": self.recommendation,
            "greenwashing_signals_count": self.greenwashing_signals_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "status": self.status,
        }


class CompanyCache(Base):
    """
    Cache for company information to reduce API calls.
    Stores data from Alpha Vantage and other sources.
    """
    __tablename__ = "company_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), unique=True, nullable=False, index=True)

    # Company Info
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)

    # Financial Data
    market_cap = Column(Float, nullable=True)
    pe_ratio = Column(Float, nullable=True)
    dividend_yield = Column(Float, nullable=True)

    # Additional Data
    extra_data = Column(JSON, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "ticker": self.ticker,
            "name": self.name,
            "description": self.description,
            "sector": self.sector,
            "industry": self.industry,
            "market_cap": self.market_cap,
            "pe_ratio": self.pe_ratio,
            "dividend_yield": self.dividend_yield,
            "extra_data": self.extra_data,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
