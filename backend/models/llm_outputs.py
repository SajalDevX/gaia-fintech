"""
LLM Output Models for GAIA
Pydantic models for structured LLM responses used by agents.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Severity levels for findings."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class RiskLevel(str, Enum):
    """Risk levels for assessments."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"
    MINIMAL = "MINIMAL"


class InvestmentAction(str, Enum):
    """Investment recommendation actions."""
    AVOID = "AVOID"
    CAUTION = "CAUTION"
    MONITOR = "MONITOR"
    ACCEPTABLE = "ACCEPTABLE"
    RECOMMENDED = "RECOMMENDED"


# Base Finding Model
class LLMFinding(BaseModel):
    """Base structured output for agent findings."""
    title: str = Field(..., description="Brief title for the finding")
    description: str = Field(..., description="Detailed description of the finding")
    severity: Severity = Field(..., description="Severity level of the finding")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in this finding")
    evidence_descriptions: List[str] = Field(default_factory=list, description="Supporting evidence")
    data_sources: List[str] = Field(default_factory=list, description="Sources of information")
    reasoning: str = Field("", description="Explanation of how conclusion was reached")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Quantitative metrics if available")


class LLMFindingsList(BaseModel):
    """Collection of findings from an analysis."""
    findings: List[LLMFinding] = Field(default_factory=list)
    overall_assessment: str = Field("", description="Summary of all findings")
    data_quality_score: float = Field(0.5, ge=0.0, le=1.0, description="Quality of available data")


# Sentinel Agent Models
class EnvironmentalFinding(LLMFinding):
    """Finding specific to environmental analysis."""
    environmental_category: str = Field("general", description="Category: emissions, pollution, biodiversity, etc.")
    estimated_impact: Optional[str] = Field(None, description="Quantified impact if available")
    trend_direction: Optional[str] = Field(None, description="improving, stable, or worsening")


class EnvironmentalAnalysisResult(BaseModel):
    """Complete environmental analysis result."""
    findings: List[EnvironmentalFinding] = Field(default_factory=list)
    carbon_footprint_assessment: Optional[str] = Field(None)
    compliance_status: Optional[str] = Field(None)
    climate_risk_level: Optional[RiskLevel] = Field(None)
    overall_environmental_score: float = Field(50.0, ge=0.0, le=100.0)
    key_concerns: List[str] = Field(default_factory=list)
    positive_practices: List[str] = Field(default_factory=list)


class DeforestationFinding(LLMFinding):
    """Finding specific to deforestation analysis."""
    ndvi_change_estimate: Optional[float] = Field(None, description="Estimated NDVI change percentage")
    forest_loss_hectares: Optional[float] = Field(None, description="Estimated forest loss in hectares")
    affected_area_description: Optional[str] = Field(None)
    certification_status: Optional[str] = Field(None, description="FSC, RSPO, etc. status")


class PollutionFinding(LLMFinding):
    """Finding specific to pollution analysis."""
    pollution_type: str = Field("general", description="air, water, soil, noise")
    contaminants: List[str] = Field(default_factory=list)
    regulatory_threshold_exceeded: bool = Field(False)
    affected_population: Optional[str] = Field(None)


# Veritas Agent Models
class SupplierInfo(BaseModel):
    """Information about a supplier."""
    name: str
    country: str
    tier: int = Field(1, description="1 for direct, 2+ for indirect")
    certifications: List[str] = Field(default_factory=list)
    risk_level: RiskLevel = Field(RiskLevel.MODERATE)
    risk_factors: List[str] = Field(default_factory=list)


class SupplyChainFinding(LLMFinding):
    """Finding specific to supply chain analysis."""
    supply_chain_tier: Optional[int] = Field(None)
    geographic_region: Optional[str] = Field(None)
    risk_category: str = Field("general", description="human_rights, environment, quality, etc.")


class SupplyChainAnalysisResult(BaseModel):
    """Complete supply chain analysis result."""
    findings: List[SupplyChainFinding] = Field(default_factory=list)
    known_suppliers: List[SupplierInfo] = Field(default_factory=list)
    transparency_score: float = Field(50.0, ge=0.0, le=100.0)
    human_rights_risk_level: RiskLevel = Field(RiskLevel.MODERATE)
    conflict_minerals_risk: Optional[str] = Field(None)
    certification_gaps: List[str] = Field(default_factory=list)


# Pulse Agent Models
class SentimentTopic(BaseModel):
    """Sentiment for a specific topic."""
    topic: str
    sentiment_score: float = Field(..., ge=-1.0, le=1.0)
    article_count: int = Field(0)
    key_themes: List[str] = Field(default_factory=list)


class SentimentAnalysisResult(BaseModel):
    """Complete sentiment analysis result."""
    overall_sentiment: float = Field(0.0, ge=-1.0, le=1.0, description="Overall sentiment score")
    sentiment_by_topic: List[SentimentTopic] = Field(default_factory=list)
    positive_themes: List[str] = Field(default_factory=list)
    negative_themes: List[str] = Field(default_factory=list)
    trending_concerns: List[str] = Field(default_factory=list)
    source_quality_score: float = Field(0.5, ge=0.0, le=1.0)
    article_count_analyzed: int = Field(0)
    confidence: float = Field(0.5, ge=0.0, le=1.0)


class ControversyFinding(LLMFinding):
    """Finding specific to controversy analysis."""
    controversy_type: str = Field("general")
    incident_date: Optional[str] = Field(None)
    company_response: Optional[str] = Field(None)
    resolution_status: str = Field("unknown", description="resolved, ongoing, unknown")
    reputational_impact: str = Field("moderate", description="minimal, moderate, significant, severe")


# Regulus Agent Models
class RegulatoryViolation(BaseModel):
    """Information about a regulatory violation."""
    regulation: str
    violation_date: Optional[str] = Field(None)
    penalty_amount: Optional[float] = Field(None)
    description: str
    resolution_status: str = Field("unknown")
    jurisdiction: str = Field("US")


class RegulatoryFinding(LLMFinding):
    """Finding specific to regulatory analysis."""
    regulation_name: Optional[str] = Field(None)
    jurisdiction: str = Field("US")
    compliance_status: str = Field("unknown", description="compliant, non-compliant, under_review")
    penalty_risk: Optional[str] = Field(None)


class RegulatoryAnalysisResult(BaseModel):
    """Complete regulatory analysis result."""
    findings: List[RegulatoryFinding] = Field(default_factory=list)
    violations: List[RegulatoryViolation] = Field(default_factory=list)
    compliance_score: float = Field(50.0, ge=0.0, le=100.0)
    total_penalties_usd: float = Field(0.0)
    active_investigations: int = Field(0)
    regulatory_risk_level: RiskLevel = Field(RiskLevel.MODERATE)
    upcoming_regulatory_risks: List[str] = Field(default_factory=list)


# Impact Agent Models
class SDGImpact(BaseModel):
    """Impact on a specific SDG."""
    sdg_number: int = Field(..., ge=1, le=17)
    sdg_name: str
    alignment_score: float = Field(0.0, ge=-100.0, le=100.0, description="Negative for harm, positive for benefit")
    positive_contributions: List[str] = Field(default_factory=list)
    negative_impacts: List[str] = Field(default_factory=list)
    impact_per_million_usd: Optional[str] = Field(None, description="Quantified impact per $1M invested")
    evidence_quality: str = Field("moderate", description="strong, moderate, weak")
    confidence: float = Field(0.5, ge=0.0, le=1.0)


class SDGAnalysisResult(BaseModel):
    """Complete SDG impact analysis result."""
    sdg_impacts: List[SDGImpact] = Field(default_factory=list)
    primary_sdg_alignment: Optional[int] = Field(None, description="Main SDG the company contributes to")
    overall_impact_score: float = Field(0.0, ge=-100.0, le=100.0)
    impact_washing_risk: str = Field("low", description="low, medium, high")
    impact_washing_indicators: List[str] = Field(default_factory=list)
    quantifiable_impacts: Dict[str, str] = Field(default_factory=dict)


# NEXUS Agent Models
class InclusionMetric(BaseModel):
    """Metric for a specific inclusion dimension."""
    dimension: str = Field(..., description="access, credit, gender, geographic, vulnerable, affordability")
    score: float = Field(50.0, ge=0.0, le=100.0)
    population_reached: Optional[str] = Field(None)
    key_indicators: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)


class InclusionAnalysisResult(BaseModel):
    """Complete financial inclusion analysis result."""
    findings: List[LLMFinding] = Field(default_factory=list)
    inclusion_metrics: List[InclusionMetric] = Field(default_factory=list)
    overall_inclusion_score: float = Field(50.0, ge=0.0, le=100.0)
    populations_served: List[str] = Field(default_factory=list)
    service_channels: List[str] = Field(default_factory=list)
    inclusion_washing_detected: bool = Field(False)
    inclusion_washing_indicators: List[str] = Field(default_factory=list)
    affordability_concerns: List[str] = Field(default_factory=list)


# Orchestrator Agent Models
class DebateArgument(BaseModel):
    """Argument in an adversarial debate."""
    position: str = Field(..., description="supporting or challenging")
    argument: str = Field(..., description="The argument text")
    key_points: List[str] = Field(default_factory=list)
    evidence_cited: List[str] = Field(default_factory=list)
    addresses_counterargument: Optional[str] = Field(None)
    confidence: float = Field(0.5, ge=0.0, le=1.0)


class DebateResolution(BaseModel):
    """Resolution of an adversarial debate."""
    winning_position: str = Field(..., description="supporting, challenging, or balanced")
    final_confidence: float = Field(0.5, ge=0.0, le=1.0)
    consensus_reached: bool = Field(False)
    resolution_summary: str = Field("")
    remaining_uncertainties: List[str] = Field(default_factory=list)
    adjusted_severity: Optional[Severity] = Field(None)


class GreenwashingSignal(BaseModel):
    """Detected greenwashing signal."""
    signal_type: str = Field(..., description="vague_claims, lack_of_evidence, contradiction, cherry_picking, hidden_tradeoff")
    severity: str = Field("medium", description="low, medium, high, critical")
    description: str = Field(...)
    evidence: str = Field("")
    affected_claims: List[str] = Field(default_factory=list)
    confidence: float = Field(0.5, ge=0.0, le=1.0)


class GreenwashingAnalysisResult(BaseModel):
    """Complete greenwashing detection result."""
    signals: List[GreenwashingSignal] = Field(default_factory=list)
    overall_risk_level: str = Field("low", description="low, medium, high, critical")
    high_confidence_signals: int = Field(0)
    summary: str = Field("")
    recommendations: List[str] = Field(default_factory=list)


class ESGScores(BaseModel):
    """ESG scoring breakdown."""
    environmental_score: float = Field(50.0, ge=0.0, le=100.0)
    social_score: float = Field(50.0, ge=0.0, le=100.0)
    governance_score: float = Field(50.0, ge=0.0, le=100.0)
    overall_score: float = Field(50.0, ge=0.0, le=100.0)
    rating: str = Field("BBB", description="AAA, AA, A, BBB, BB, B, CCC, CC, C, D")
    environmental_factors: List[str] = Field(default_factory=list)
    social_factors: List[str] = Field(default_factory=list)
    governance_factors: List[str] = Field(default_factory=list)


class FinalAssessment(BaseModel):
    """Final synthesized ESG assessment."""
    company_name: str
    esg_scores: ESGScores
    risk_level: RiskLevel
    investment_action: InvestmentAction
    key_strengths: List[str] = Field(default_factory=list)
    key_risks: List[str] = Field(default_factory=list)
    consensus_findings: List[str] = Field(default_factory=list)
    uncertainty_areas: List[str] = Field(default_factory=list)
    greenwashing_risk: str = Field("low")
    data_quality_assessment: str = Field("")
    confidence_score: float = Field(0.5, ge=0.0, le=1.0)
    summary: str = Field("")
