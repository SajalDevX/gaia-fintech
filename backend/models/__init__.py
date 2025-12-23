"""
GAIA Data Models Package
Global AI-powered Impact Assessment System

This package contains all Pydantic data models for the GAIA system,
including company profiles, ESG assessments, agent communication,
evidence trails, and SDG impact analysis.
"""

# Company and Investment Models
from .company import (
    IndustryClassification,
    MarketCapSize,
    StockExchange,
    GeographicRegion,
    StockInformation,
    GeographicPresence,
    HistoricalESGDataPoint,
    CompanyProfile,
    InvestmentQuery,
)

# Assessment and Rating Models
from .assessment import (
    RatingLevel,
    InvestmentRecommendation,
    RiskLevel,
    ESGComponentScore,
    ESGScores,
    GreenwashingRiskScore,
    SustainabilityRating,
    InvestmentRecommendationResult,
    AssessmentResult,
)

# Agent Communication Models
from .agent_models import (
    AgentType,
    AgentRole,
    ConfidenceLevel,
    FindingType,
    ChallengeType,
    AgentFinding,
    AgentChallenge,
    AgentResponse,
    DebateRound,
    ConsensusResult,
)

# Evidence and Verification Models
from .evidence import (
    EvidenceType,
    SourceType,
    VerificationStatus,
    DataQuality,
    EvidenceSource,
    EvidenceItem,
    BlockchainRecord,
    EvidenceTrail,
    ProvenanceRecord,
)

# SDG Impact Models
from .sdg import (
    SDGGoal,
    ImpactType,
    ImpactMagnitude,
    ContributionType,
    SDGTarget,
    SDGImpactMetric,
    SDGContribution,
    SDGAlignment,
    SDGReport,
)

# Financial Inclusion Models
from .inclusion import (
    UnderservedSegment,
    InclusionChannel,
    InclusionRiskLevel,
    AccessMetrics,
    CreditMetrics,
    GenderInclusionMetrics,
    GeographicInclusionMetrics,
    VulnerablePopulationMetrics,
    AffordabilityMetrics,
    InclusionWashingIndicator,
    InclusionWashingAnalysis,
    FinancialInclusionScore,
    FinancialInclusionReport,
    InclusionPortfolioAnalysis,
    InclusionBenchmark,
)

# Export all models
__all__ = [
    # Company Models
    "IndustryClassification",
    "MarketCapSize",
    "StockExchange",
    "GeographicRegion",
    "StockInformation",
    "GeographicPresence",
    "HistoricalESGDataPoint",
    "CompanyProfile",
    "InvestmentQuery",
    # Assessment Models
    "RatingLevel",
    "InvestmentRecommendation",
    "RiskLevel",
    "ESGComponentScore",
    "ESGScores",
    "GreenwashingRiskScore",
    "SustainabilityRating",
    "InvestmentRecommendationResult",
    "AssessmentResult",
    # Agent Models
    "AgentType",
    "AgentRole",
    "ConfidenceLevel",
    "FindingType",
    "ChallengeType",
    "AgentFinding",
    "AgentChallenge",
    "AgentResponse",
    "DebateRound",
    "ConsensusResult",
    # Evidence Models
    "EvidenceType",
    "SourceType",
    "VerificationStatus",
    "DataQuality",
    "EvidenceSource",
    "EvidenceItem",
    "BlockchainRecord",
    "EvidenceTrail",
    "ProvenanceRecord",
    # SDG Models
    "SDGGoal",
    "ImpactType",
    "ImpactMagnitude",
    "ContributionType",
    "SDGTarget",
    "SDGImpactMetric",
    "SDGContribution",
    "SDGAlignment",
    "SDGReport",
    # Financial Inclusion Models
    "UnderservedSegment",
    "InclusionChannel",
    "InclusionRiskLevel",
    "AccessMetrics",
    "CreditMetrics",
    "GenderInclusionMetrics",
    "GeographicInclusionMetrics",
    "VulnerablePopulationMetrics",
    "AffordabilityMetrics",
    "InclusionWashingIndicator",
    "InclusionWashingAnalysis",
    "FinancialInclusionScore",
    "FinancialInclusionReport",
    "InclusionPortfolioAnalysis",
    "InclusionBenchmark",
]

# Version information
__version__ = "1.0.0"
__author__ = "GAIA Development Team"
__description__ = "Pydantic data models for GAIA ESG assessment system"
